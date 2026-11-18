using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Time.Testing;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Core.Tests.Settings;

public sealed class ThemeSettingsTests : IDisposable
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
    public void Theme_DefaultsToSystem()
    {
        Assert.Equal(AppTheme.System, AppSettings.Default.Theme);
        Assert.Equal(AppTheme.System, CreateStore().Load().Theme);
    }

    [Fact]
    public void Theme_IsSavedAsReadableText()
    {
        CreateStore().Save(AppSettings.Default with { Theme = AppTheme.Dark });

        Assert.Contains("\"theme\": \"Dark\"", File.ReadAllText(Path.Combine(_directory, "settings.json")), StringComparison.Ordinal);
        Assert.Equal(AppTheme.Dark, CreateStore().Load().Theme);
    }

    [Fact]
    public void SettingsFromFaz1_WithoutTheme_LoadAsSystem()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(Path.Combine(_directory, "settings.json"), """{ "isAlwaysOnTop": true }""");

        var settings = CreateStore().Load();

        Assert.True(settings.IsAlwaysOnTop);
        Assert.Equal(AppTheme.System, settings.Theme);
    }
}
