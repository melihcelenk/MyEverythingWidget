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
        if (Directory.Exists(Path))
        {
            Directory.Delete(Path, recursive: true);
        }
    }
}
