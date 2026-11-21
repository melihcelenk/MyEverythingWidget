using System.Text.Json;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>
/// The About card shows the version the Store package carries. Its single source is
/// <c>src/MyEverythingWidget.App/StoreIdentity.json</c>; raising the version there is enough for every build.
/// </summary>
public sealed class AppVersionTests
{
    private static string StoreVersion()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "MyEverythingWidget.slnx")))
        {
            directory = directory.Parent;
        }

        var identity = Path.Combine(directory!.FullName, "src", "MyEverythingWidget.App", "StoreIdentity.json");
        using var json = JsonDocument.Parse(File.ReadAllText(identity));
        return json.RootElement.GetProperty("version").GetString()!;
    }

    [Fact]
    public void AboutVersion_IsTheStorePackageVersion()
    {
        var store = Version.Parse(StoreVersion());

        var shown = new MainViewModel(new InMemorySettingsStore(AppSettings.Default)).Version;

        Assert.Equal(store.ToString(3), shown);
    }
}
