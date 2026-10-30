namespace MyEverythingWidget.App;

/// <summary>
/// Resolves file paths stored in the widget state, which are relative to the data folder.
/// </summary>
internal static class DataFiles
{
    private static readonly Lazy<string> DataDirectory = new(AppDataLocation.Resolve);

    /// <summary>
    /// Returns the full path of <paramref name="relativeOrAbsolutePath"/> when that file exists; otherwise <see langword="null"/>.
    /// </summary>
    public static string? Resolve(string? relativeOrAbsolutePath)
    {
        if (string.IsNullOrWhiteSpace(relativeOrAbsolutePath))
        {
            return null;
        }

        var fullPath = Path.IsPathRooted(relativeOrAbsolutePath)
            ? relativeOrAbsolutePath
            : Path.Combine(DataDirectory.Value, relativeOrAbsolutePath);
        return File.Exists(fullPath) ? fullPath : null;
    }
}
