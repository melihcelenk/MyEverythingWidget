namespace MyEverythingWidget.App;

/// <summary>
/// Resolves the folder where the app keeps its files.
/// </summary>
internal static class AppDataLocation
{
    /// <summary>Environment variable that overrides the data folder; used by UI tests.</summary>
    public const string OverrideVariable = "MEW_DATA_DIR";

    private const string UnpackagedFolderName = "MyEverythingWidget.WinUI";

    /// <summary>
    /// Returns <see cref="OverrideVariable"/> when set; the package's local folder when running as MSIX;
    /// otherwise <c>%LOCALAPPDATA%\MyEverythingWidget.WinUI</c>.
    /// </summary>
    /// <remarks>
    /// The unpackaged folder name differs from the Python version's <c>MyEverythingWidget</c> folder so the
    /// two versions never overwrite each other's files.
    /// </remarks>
    public static string Resolve()
    {
        var overridePath = Environment.GetEnvironmentVariable(OverrideVariable);
        if (!string.IsNullOrWhiteSpace(overridePath))
        {
            return overridePath;
        }

        try
        {
            return Windows.Storage.ApplicationData.Current.LocalFolder.Path;
        }
        catch (InvalidOperationException)
        {
            // Not running as a package: there is no package identity and no ApplicationData.
            return Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                UnpackagedFolderName);
        }
    }
}
