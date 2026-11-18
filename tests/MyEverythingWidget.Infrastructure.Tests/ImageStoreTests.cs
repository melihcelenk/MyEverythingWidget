using System.Runtime.InteropServices.WindowsRuntime;
using MyEverythingWidget.Infrastructure.Shell;
using Windows.Graphics.Imaging;
using Windows.Storage.Streams;

namespace MyEverythingWidget.Infrastructure.Tests;

public sealed class ImageStoreTests : IDisposable
{
    private readonly string _dataDirectory = Path.Combine(Path.GetTempPath(), "mew-image-tests", Guid.NewGuid().ToString("N"));

    public void Dispose()
    {
        if (Directory.Exists(_dataDirectory))
        {
            Directory.Delete(_dataDirectory, recursive: true);
        }
    }

    private static async Task<MemoryStream> CreateImageAsync(int width, int height, Guid encoderId)
    {
        var pixels = new byte[width * height * 4];
        Array.Fill(pixels, (byte)200);
        using var bitmap = SoftwareBitmap.CreateCopyFromBuffer(pixels.AsBuffer(), BitmapPixelFormat.Bgra8, width, height, BitmapAlphaMode.Premultiplied);
        using var output = new InMemoryRandomAccessStream();
        var encoder = await BitmapEncoder.CreateAsync(encoderId, output);
        encoder.SetSoftwareBitmap(bitmap);
        await encoder.FlushAsync();
        var bytes = new byte[output.Size];
        output.Seek(0);
        await output.ReadAsync(bytes.AsBuffer(), (uint)bytes.Length, InputStreamOptions.None);
        return new MemoryStream(bytes);
    }

    [Fact]
    public async Task Import_Jpeg_IsSavedAsPngWithItsSize()
    {
        using var jpeg = await CreateImageAsync(160, 90, BitmapEncoder.JpegEncoderId);

        var stored = await new ImageStore(_dataDirectory).ImportAsync(jpeg, TestContext.Current.CancellationToken);

        Assert.NotNull(stored);
        Assert.Equal((160, 90), (stored.PixelWidth, stored.PixelHeight));
        Assert.EndsWith(".png", stored.RelativePath, StringComparison.Ordinal);
        Assert.Equal(0x89, File.ReadAllBytes(Path.Combine(_dataDirectory, stored.RelativePath))[0]);
    }

    [Fact]
    public async Task Import_HugeImage_IsScaledDownKeepingAspect()
    {
        using var png = await CreateImageAsync(4096, 2048, BitmapEncoder.PngEncoderId);

        var stored = await new ImageStore(_dataDirectory).ImportAsync(png, TestContext.Current.CancellationToken);

        Assert.NotNull(stored);
        Assert.Equal((ImageStore.MaxEdge, ImageStore.MaxEdge / 2), (stored.PixelWidth, stored.PixelHeight));
    }

    [Fact]
    public async Task Import_NotAnImage_ReturnsNull()
    {
        using var text = new MemoryStream("hello"u8.ToArray());

        Assert.Null(await new ImageStore(_dataDirectory).ImportAsync(text, TestContext.Current.CancellationToken));
    }

    [Fact]
    public async Task Delete_RemovesSavedImage()
    {
        using var png = await CreateImageAsync(10, 10, BitmapEncoder.PngEncoderId);
        var store = new ImageStore(_dataDirectory);
        var stored = await store.ImportAsync(png, TestContext.Current.CancellationToken);

        store.Delete(stored!.RelativePath);

        Assert.False(File.Exists(Path.Combine(_dataDirectory, stored.RelativePath)));
    }
}
