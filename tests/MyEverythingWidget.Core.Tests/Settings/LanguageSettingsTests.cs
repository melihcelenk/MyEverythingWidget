using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Time.Testing;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Core.Tests.Settings;

public sealed class LanguageSettingsTests : IDisposable
{
    private readonly string _directory = Path.Combine(Path.GetTempPath(), "mew-tests", Guid.NewGuid().ToString("N"));

    private JsonSettingsStore CreateStore() => new(_directory, new FakeTimeProvider(), NullLogger<JsonSettingsStore>.Instance);

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, recursive: true);
        }
    }

    [Fact]
    public void Language_DefaultsToTheSystemLanguage()
    {
        Assert.Null(AppSettings.Default.Language);
        Assert.Null(CreateStore().Load().Language);
    }

    [Fact]
    public void Language_IsSavedAndLoaded()
    {
        CreateStore().Save(AppSettings.Default with { Language = "tr" });

        Assert.Contains("\"language\": \"tr\"", File.ReadAllText(Path.Combine(_directory, "settings.json")), StringComparison.Ordinal);
        Assert.Equal("tr", CreateStore().Load().Language);
    }

    [Fact]
    public void SettingsWithoutLanguage_LoadWithTheSystemLanguage()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(Path.Combine(_directory, "settings.json"), """{ "isAlwaysOnTop": true, "theme": "Dark" }""");

        Assert.Null(CreateStore().Load().Language);
    }
}
