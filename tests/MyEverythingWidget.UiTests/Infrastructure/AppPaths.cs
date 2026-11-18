namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Locates the app executable under test.
/// </summary>
internal static class AppPaths
{
    /// <summary>Environment variable with the full path of the executable; set by the sandbox runner.</summary>
    public const string ExecutableVariable = "MEW_APP_EXE";

    private const string RelativeBuildOutput =
        @"src\MyEverythingWidget.App\bin\x64\Debug\net10.0-windows10.0.26100.0\win-x64\MyEverythingWidget.exe";

    /// <summary>
    /// Returns <see cref="ExecutableVariable"/> when set; otherwise the Debug x64 build output in this repository.
    /// </summary>
    public static string Executable()
    {
        var configured = Environment.GetEnvironmentVariable(ExecutableVariable);
        var path = string.IsNullOrWhiteSpace(configured)
            ? Path.Combine(FindRepositoryRoot(), RelativeBuildOutput)
            : configured;

        return File.Exists(path)
            ? path
            : throw new FileNotFoundException($"App executable not found; build the app or set {ExecutableVariable}.", path);
    }

    private static string FindRepositoryRoot()
    {
        for (var directory = new DirectoryInfo(AppContext.BaseDirectory); directory is not null; directory = directory.Parent)
        {
            if (File.Exists(Path.Combine(directory.FullName, "MyEverythingWidget.slnx")))
            {
                return directory.FullName;
            }
        }

        throw new DirectoryNotFoundException($"Repository root not found; set {ExecutableVariable}.");
    }
}
