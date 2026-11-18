namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// An isolated, temporary data folder for one test; it survives app restarts within the test.
/// </summary>
internal sealed class AppDataFolder : IDisposable
{
    public string Path { get; } = System.IO.Path.Combine(
        System.IO.Path.GetTempPath(), "mew-uitests", Guid.NewGuid().ToString("N"));

    public string SettingsFile => System.IO.Path.Combine(Path, "settings.json");

    public void Dispose()
    {
        // Keep the app's crash record for failure analysis; the data folder itself is deleted below.
        var crashLog = System.IO.Path.Combine(Path, "logs", "crash.log");
        if (File.Exists(crashLog))
        {
            File.Copy(crashLog, Artifacts.PathOf("crash-" + System.IO.Path.GetFileName(Path)).Replace(".png", ".log", StringComparison.Ordinal), overwrite: true);
        }

        if (Directory.Exists(Path))
        {
            Directory.Delete(Path, recursive: true);
        }
    }
}
