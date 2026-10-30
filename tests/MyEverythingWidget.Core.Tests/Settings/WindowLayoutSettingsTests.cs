using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Time.Testing;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Core.Tests.Settings;

/// <summary>Grid size and compact mode survive restarts.</summary>
public sealed class WindowLayoutSettingsTests : IDisposable
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
    public void Defaults_AreNoSavedGridAndExpanded()
    {
        Assert.Null(AppSettings.Default.GridSize);
        Assert.False(AppSettings.Default.IsCompact);
    }

    [Fact]
    public void GridSizeAndCompact_AreSavedAndLoaded()
    {
        CreateStore().Save(AppSettings.Default with { GridSize = new GridSize(Rows: 3, Columns: 4), IsCompact = true });

        var loaded = CreateStore().Load();

        Assert.Equal(new GridSize(3, 4), loaded.GridSize);
        Assert.True(loaded.IsCompact);
    }

    [Fact]
    public void OlderSettings_WithoutGridSize_LoadWithoutIt()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(Path.Combine(_directory, "settings.json"), """{ "isAlwaysOnTop": false }""");

        var loaded = CreateStore().Load();

        Assert.Null(loaded.GridSize);
        Assert.False(loaded.IsCompact);
    }
}
