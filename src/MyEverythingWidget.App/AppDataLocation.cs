namespace MyEverythingWidget.App;

/// <summary>
/// Resolves the folder where the app keeps its files.
/// </summary>
internal static class AppDataLocation
{
    /// <summary>Environment variable that overrides the data folder; used by UI tests.</summary>
    public const string OverrideVariable = "MEW_DATA_DIR";

    /// <summary>
    /// Command-line form of <see cref="OverrideVariable"/>: a restart passes the folder on, since the restarted process
    /// does not necessarily inherit the environment.
    /// </summary>
    public const string OverrideArgument = "--data-dir=";

    private const string UnpackagedFolderName = "MyEverythingWidget.WinUI";

    /// <summary>
    /// Returns <see cref="OverrideVariable"/> or <see cref="OverrideArgument"/> when set; the package's local folder when
    /// running as MSIX; otherwise <c>%LOCALAPPDATA%\MyEverythingWidget.WinUI</c>.
    /// </summary>
    /// <remarks>
    /// The unpackaged folder name differs from the Python version's <c>MyEverythingWidget</c> folder so the
    /// two versions never overwrite each other's files.
    /// </remarks>
    public static string Resolve()
    {
        if (Override() is { } overridePath)
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

    /// <summary>Returns the overriding data folder, or <see langword="null"/> when the default one is used.</summary>
    public static string? Override()
    {
        var variable = Environment.GetEnvironmentVariable(OverrideVariable);
        if (!string.IsNullOrWhiteSpace(variable))
        {
            return variable;
        }

        var argument = Environment.GetCommandLineArgs()
            .FirstOrDefault(arg => arg.StartsWith(OverrideArgument, StringComparison.Ordinal));
        return argument is null ? null : argument[OverrideArgument.Length..].Trim('"');
    }
}
