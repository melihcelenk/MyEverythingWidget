using Windows.ApplicationModel.DataTransfer;

namespace MyEverythingWidget.App;

/// <summary>
/// Reads what was dropped or pasted as plain texts: file and folder paths, a web link, or text lines.
/// </summary>
internal static class DroppedTexts
{
    /// <summary>Returns the paths, link or non-empty text lines in <paramref name="data"/>.</summary>
    public static async Task<IReadOnlyList<string>> ReadAsync(DataPackageView data)
    {
        ArgumentNullException.ThrowIfNull(data);

        if (data.Contains(StandardDataFormats.StorageItems))
        {
            var items = await data.GetStorageItemsAsync();
            return items.Select(item => item.Path).Where(path => !string.IsNullOrEmpty(path)).ToList();
        }

        if (data.Contains(StandardDataFormats.WebLink))
        {
            return [(await data.GetWebLinkAsync()).OriginalString];
        }

        if (data.Contains(StandardDataFormats.Text))
        {
            var text = await data.GetTextAsync();
            return text.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        }

        return [];
    }
}
