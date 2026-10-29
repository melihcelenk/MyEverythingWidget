using System.Text;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Time.Testing;
using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Core.Tests.Settings;

public sealed class JsonSettingsStoreTests : IDisposable
{
    private readonly string _directory = Path.Combine(Path.GetTempPath(), "mew-tests", Guid.NewGuid().ToString("N"));
    private readonly FakeTimeProvider _time = new(new DateTimeOffset(2026, 10, 30, 14, 5, 9, TimeSpan.Zero));

    private string SettingsPath => Path.Combine(_directory, "settings.json");

    private JsonSettingsStore CreateStore() => new(_directory, _time, NullLogger<JsonSettingsStore>.Instance);

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, recursive: true);
        }
    }

    [Fact]
    public void Load_WhenFileIsMissing_ReturnsDefaults()
    {
        var settings = CreateStore().Load();

        Assert.Equal(AppSettings.Default, settings);
        Assert.False(settings.IsAlwaysOnTop);
        Assert.Null(settings.WindowBounds);
    }

    [Fact]
    public void Save_ThenLoad_ReturnsSameSettings()
    {
        var expected = new AppSettings(IsAlwaysOnTop: true, WindowBounds: new PixelRect(300, 200, 404, 480));

        CreateStore().Save(expected);
        var actual = CreateStore().Load();

        Assert.Equal(expected, actual);
    }

    [Fact]
    public void Save_CreatesMissingDirectory()
    {
        CreateStore().Save(AppSettings.Default);

        Assert.True(File.Exists(SettingsPath));
    }

    [Fact]
    public void Save_ReplacesExistingFileAndLeavesNoTemporaryFile()
    {
        var store = CreateStore();
        store.Save(new AppSettings(false, new PixelRect(1, 2, 3, 4)));

        store.Save(new AppSettings(true, new PixelRect(5, 6, 7, 8)));

        Assert.Equal(new AppSettings(true, new PixelRect(5, 6, 7, 8)), CreateStore().Load());
        Assert.Equal(["settings.json"], Directory.GetFiles(_directory).Select(Path.GetFileName));
    }

    [Fact]
    public void Load_WhenFileIsCorrupt_ReturnsDefaultsAndKeepsCorruptCopy()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(SettingsPath, "{ not json", Encoding.UTF8);

        var settings = CreateStore().Load();

        Assert.Equal(AppSettings.Default, settings);
        Assert.False(File.Exists(SettingsPath));
        var backup = Path.Combine(_directory, "settings.corrupt-20261030-140509.json");
        Assert.True(File.Exists(backup));
        Assert.Equal("{ not json", File.ReadAllText(backup));
    }

    [Fact]
    public void Load_WhenFileHasUnknownFields_IgnoresThem()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(SettingsPath, """{ "isAlwaysOnTop": true, "futureField": 42 }""", Encoding.UTF8);

        var settings = CreateStore().Load();

        Assert.True(settings.IsAlwaysOnTop);
        Assert.Null(settings.WindowBounds);
    }
}
