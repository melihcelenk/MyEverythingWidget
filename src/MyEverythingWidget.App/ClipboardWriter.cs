using Windows.ApplicationModel.DataTransfer;
using Windows.Storage;
using Windows.Storage.Streams;

namespace MyEverythingWidget.App;

/// <summary>
/// Puts content from the widget on the Windows clipboard.
/// </summary>
internal static class ClipboardWriter
{
    /// <summary>
    /// Copies the image at <paramref name="imageFile"/> both as a picture (for Paint, Word, chat apps) and as a file (for
    /// File Explorer). The content stays on the clipboard after the widget closes.
    /// </summary>
    public static async Task CopyImageAsync(string imageFile)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(imageFile);

        var file = await StorageFile.GetFileFromPathAsync(imageFile);
        var package = new DataPackage { RequestedOperation = DataPackageOperation.Copy };
        package.SetBitmap(RandomAccessStreamReference.CreateFromFile(file));
        package.SetStorageItems([file]);
        Clipboard.SetContent(package);
        Clipboard.Flush();
    }
}
