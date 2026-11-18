using MyEverythingWidget.Presentation;
using Windows.ApplicationModel.DataTransfer;

namespace MyEverythingWidget.App;

/// <summary>
/// Turns the clipboard content into a <see cref="PastedContent"/> for the view model.
/// </summary>
internal static class ClipboardReader
{
    /// <summary>Reads files, picture and text from <paramref name="data"/>; the picture is opened only when needed.</summary>
    public static async Task<PastedContent> ReadAsync(DataPackageView data)
    {
        ArgumentNullException.ThrowIfNull(data);

        IReadOnlyList<string> files = [];
        if (data.Contains(StandardDataFormats.StorageItems))
        {
            files = (await data.GetStorageItemsAsync()).Select(item => item.Path).Where(path => !string.IsNullOrEmpty(path)).ToList();
        }

        Func<CancellationToken, Task<Stream?>>? openBitmap = null;
        if (data.Contains(StandardDataFormats.Bitmap))
        {
            openBitmap = async _ =>
            {
                var reference = await data.GetBitmapAsync();
                var stream = await reference.OpenReadAsync();
                return stream.AsStreamForRead();
            };
        }

        string? text = null;
        if (data.Contains(StandardDataFormats.Text))
        {
            text = await data.GetTextAsync();
        }

        return new PastedContent(files, openBitmap, text);
    }
}
