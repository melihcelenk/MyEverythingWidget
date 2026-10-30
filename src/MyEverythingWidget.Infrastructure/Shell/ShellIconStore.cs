using System.Runtime.InteropServices.WindowsRuntime;
using Microsoft.Extensions.Logging;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.State;
using Windows.Graphics.Imaging;
using Windows.Storage.Streams;

namespace MyEverythingWidget.Infrastructure.Shell;

/// <summary>
/// Saves app icons as PNG files under <c>icons\</c> in the data folder: the shell icon of a program, shortcut,
/// folder or Store app, or the site icon of a web address.
/// </summary>
public sealed partial class ShellIconStore : IIconStore
{
    /// <summary>Edge length of saved icons, in pixels (enough for 36 DIP at 175% scale).</summary>
    public const int IconSize = 64;

    private const string IconFolder = "icons";
    private const uint DibRgbColors = 0;
    private const int BitsPerPixel = 32;

    private readonly string _dataDirectory;
    private readonly ISiteIconSource _siteIcons;
    private readonly ILogger<ShellIconStore> _logger;

    /// <summary>Creates a store that writes into <paramref name="dataDirectory"/>.</summary>
    public ShellIconStore(string dataDirectory, ISiteIconSource siteIcons, ILogger<ShellIconStore> logger)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(dataDirectory);
        ArgumentNullException.ThrowIfNull(siteIcons);
        ArgumentNullException.ThrowIfNull(logger);

        _dataDirectory = dataDirectory;
        _siteIcons = siteIcons;
        _logger = logger;
    }

    /// <inheritdoc />
    public async Task<string?> CreateIconAsync(LaunchTarget target, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(target);

        try
        {
            var png = target.Kind == LaunchKind.Url
                ? await _siteIcons.GetPngAsync(new Uri(target.Target), IconSize, cancellationToken).ConfigureAwait(false)
                : await Task.Run(() => RenderShellIconAsync(target.Target), cancellationToken).ConfigureAwait(false);
            return png is null ? null : Save(png);
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or System.Runtime.InteropServices.COMException)
        {
            LogIconFailed(exception, target.Target);
            return null;
        }
    }

    /// <inheritdoc />
    public void DeleteIcon(string relativePath)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(relativePath);

        var fullPath = Path.GetFullPath(Path.Combine(_dataDirectory, relativePath));
        var iconDirectory = Path.GetFullPath(Path.Combine(_dataDirectory, IconFolder)) + Path.DirectorySeparatorChar;
        if (fullPath.StartsWith(iconDirectory, StringComparison.OrdinalIgnoreCase) && File.Exists(fullPath))
        {
            File.Delete(fullPath);
        }
    }

    private string Save(byte[] png)
    {
        var relativePath = Path.Combine(IconFolder, Guid.NewGuid().ToString("N") + ".png");
        var fullPath = Path.Combine(_dataDirectory, relativePath);
        Directory.CreateDirectory(Path.GetDirectoryName(fullPath)!);
        File.WriteAllBytes(fullPath, png);
        return relativePath;
    }

    private static async Task<byte[]?> RenderShellIconAsync(string target)
    {
        var pixels = RenderShellIcon(target);
        return pixels is null ? null : await PngEncoding.EncodeAsync(pixels.Value.Bytes, pixels.Value.Width, pixels.Value.Height).ConfigureAwait(false);
    }

    /// <summary>Asks the shell for the item's icon and copies it as top-down premultiplied BGRA.</summary>
    private static (byte[] Bytes, int Width, int Height)? RenderShellIcon(string target)
    {
        var item = ShellNative.ItemFromParsingName(target);
        if (item is null)
        {
            return null;
        }

        var factory = (IShellItemImageFactory)item;
        var size = new NativeSize { Width = IconSize, Height = IconSize };
        if (factory.GetImage(size, ShellImageOptions.IconOnly | ShellImageOptions.BiggerSizeOk, out var bitmap) < 0)
        {
            return null;
        }

        try
        {
            return CopyPixels(bitmap);
        }
        finally
        {
            ShellNative.DeleteObject(bitmap);
        }
    }

    private static (byte[] Bytes, int Width, int Height)? CopyPixels(nint bitmap)
    {
        if (ShellNative.GetObjectW(bitmap, System.Runtime.InteropServices.Marshal.SizeOf<ShellNative.BitmapHeader>(), out var header) == 0)
        {
            return null;
        }

        var info = new ShellNative.BitmapInfoHeader
        {
            Size = (uint)System.Runtime.InteropServices.Marshal.SizeOf<ShellNative.BitmapInfoHeader>(),
            Width = header.Width,
            Height = -header.Height,
            Planes = 1,
            BitCount = BitsPerPixel,
        };
        var bytes = new byte[header.Width * header.Height * 4];
        var screen = ShellNative.GetDC(0);
        try
        {
            return ShellNative.GetDIBits(screen, bitmap, 0, (uint)header.Height, bytes, ref info, DibRgbColors) == 0
                ? null
                : (bytes, header.Width, header.Height);
        }
        finally
        {
            _ = ShellNative.ReleaseDC(0, screen);
        }
    }

    [LoggerMessage(Level = LogLevel.Warning, Message = "Icon of {Target} could not be created; a monogram is used instead")]
    private partial void LogIconFailed(Exception exception, string target);
}

/// <summary>PNG encoding of raw pixels and resizing of image files, through Windows imaging.</summary>
internal static class PngEncoding
{
    /// <summary>Encodes top-down premultiplied BGRA pixels as PNG.</summary>
    public static async Task<byte[]> EncodeAsync(byte[] bgra, int width, int height)
    {
        using var bitmap = SoftwareBitmap.CreateCopyFromBuffer(bgra.AsBuffer(), BitmapPixelFormat.Bgra8, width, height, BitmapAlphaMode.Premultiplied);
        return await EncodeAsync(bitmap).ConfigureAwait(false);
    }

    /// <summary>Decodes any image Windows can read (PNG, ICO, JPEG, BMP...) and re-encodes it as a square PNG.</summary>
    public static async Task<byte[]?> ToPngAsync(byte[] image, int size)
    {
        try
        {
            using var input = new InMemoryRandomAccessStream();
            await input.WriteAsync(image.AsBuffer());
            input.Seek(0);
            var decoder = await BitmapDecoder.CreateAsync(input);
            var transform = new BitmapTransform { ScaledWidth = (uint)size, ScaledHeight = (uint)size, InterpolationMode = BitmapInterpolationMode.Fant };
            using var bitmap = await decoder.GetSoftwareBitmapAsync(BitmapPixelFormat.Bgra8, BitmapAlphaMode.Premultiplied, transform, ExifOrientationMode.RespectExifOrientation, ColorManagementMode.DoNotColorManage);
            return await EncodeAsync(bitmap).ConfigureAwait(false);
        }
        catch (Exception exception) when (exception is ArgumentException or System.Runtime.InteropServices.COMException)
        {
            return null;
        }
    }

    private static async Task<byte[]> EncodeAsync(SoftwareBitmap bitmap)
    {
        using var output = new InMemoryRandomAccessStream();
        var encoder = await BitmapEncoder.CreateAsync(BitmapEncoder.PngEncoderId, output);
        encoder.SetSoftwareBitmap(bitmap);
        await encoder.FlushAsync();

        var bytes = new byte[output.Size];
        output.Seek(0);
        await output.ReadAsync(bytes.AsBuffer(), (uint)bytes.Length, InputStreamOptions.None);
        return bytes;
    }
}
