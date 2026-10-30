namespace MyEverythingWidget.Core.Apps;

/// <summary>An image copied into the data folder.</summary>
/// <param name="RelativePath">Path relative to the data folder, for example <c>images\3f2c….png</c>.</param>
/// <param name="PixelWidth">Width in pixels.</param>
/// <param name="PixelHeight">Height in pixels.</param>
public sealed record StoredImage(string RelativePath, int PixelWidth, int PixelHeight);

/// <summary>Keeps the images shown on image cards.</summary>
public interface IImageStore
{
    /// <summary>
    /// Reads an image in any format Windows can decode and saves it as PNG; returns <see langword="null"/> when
    /// <paramref name="image"/> is not an image.
    /// </summary>
    Task<StoredImage?> ImportAsync(Stream image, CancellationToken cancellationToken);

    /// <summary>Deletes an image saved by <see cref="ImportAsync"/>; missing files are ignored.</summary>
    void Delete(string relativePath);
}

/// <summary>File types that are added as image cards rather than app cards.</summary>
public static class ImageFiles
{
    private static readonly HashSet<string> Extensions = new(StringComparer.OrdinalIgnoreCase)
    {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".heic",
    };

    /// <summary>Returns whether <paramref name="path"/> has an image file extension.</summary>
    public static bool IsImage(string path) => Extensions.Contains(Path.GetExtension(path));
}
