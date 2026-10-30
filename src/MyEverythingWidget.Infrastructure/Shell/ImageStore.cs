using System.Runtime.InteropServices.WindowsRuntime;
using MyEverythingWidget.Core.Apps;
using Windows.Graphics.Imaging;
using Windows.Storage.Streams;

namespace MyEverythingWidget.Infrastructure.Shell;

/// <summary>
/// Saves images of image cards as PNG under <c>images\</c> in the data folder. Images larger than
/// <see cref="MaxEdge"/> pixels are scaled down, so a pasted 8K screenshot does not bloat the data folder.
/// </summary>
public sealed class ImageStore(string dataDirectory) : IImageStore
{
    /// <summary>Longest edge kept, in pixels; the largest card (3x3 cells) is far smaller even at 300% scale.</summary>
    public const int MaxEdge = 2048;

    private const string ImageFolder = "images";

    /// <inheritdoc />
    public async Task<StoredImage?> ImportAsync(Stream image, CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(image);

        byte[] bytes;
        using (var buffer = new MemoryStream())
        {
            await image.CopyToAsync(buffer, cancellationToken).ConfigureAwait(false);
            bytes = buffer.ToArray();
        }

        try
        {
            using var input = new InMemoryRandomAccessStream();
            await input.WriteAsync(bytes.AsBuffer());
            input.Seek(0);
            var decoder = await BitmapDecoder.CreateAsync(input);
            var (width, height) = FitWithin(decoder.OrientedPixelWidth, decoder.OrientedPixelHeight);
            var transform = new BitmapTransform { ScaledWidth = (uint)width, ScaledHeight = (uint)height, InterpolationMode = BitmapInterpolationMode.Fant };
            using var bitmap = await decoder.GetSoftwareBitmapAsync(
                BitmapPixelFormat.Bgra8, BitmapAlphaMode.Premultiplied, transform, ExifOrientationMode.RespectExifOrientation, ColorManagementMode.ColorManageToSRgb);

            var relativePath = Path.Combine(ImageFolder, Guid.NewGuid().ToString("N") + ".png");
            var fullPath = Path.Combine(dataDirectory, relativePath);
            Directory.CreateDirectory(Path.GetDirectoryName(fullPath)!);
            await File.WriteAllBytesAsync(fullPath, await EncodePngAsync(bitmap).ConfigureAwait(false), cancellationToken).ConfigureAwait(false);
            return new StoredImage(relativePath, width, height);
        }
        catch (Exception exception) when (exception is ArgumentException or System.Runtime.InteropServices.COMException)
        {
            // Not an image Windows can decode.
            return null;
        }
    }

    /// <inheritdoc />
    public void Delete(string relativePath)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(relativePath);

        var fullPath = Path.GetFullPath(Path.Combine(dataDirectory, relativePath));
        var imageDirectory = Path.GetFullPath(Path.Combine(dataDirectory, ImageFolder)) + Path.DirectorySeparatorChar;
        if (fullPath.StartsWith(imageDirectory, StringComparison.OrdinalIgnoreCase) && File.Exists(fullPath))
        {
            File.Delete(fullPath);
        }
    }

    private static (int Width, int Height) FitWithin(uint width, uint height)
    {
        var longest = Math.Max(width, height);
        if (longest <= MaxEdge)
        {
            return ((int)width, (int)height);
        }

        var scale = (double)MaxEdge / longest;
        return (Math.Max(1, (int)Math.Round(width * scale)), Math.Max(1, (int)Math.Round(height * scale)));
    }

    private static async Task<byte[]> EncodePngAsync(SoftwareBitmap bitmap)
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
