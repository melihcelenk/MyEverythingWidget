using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Time.Testing;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

/// <summary>Saved state of a grid larger than 5x5, and emoji icons.</summary>
public sealed class LayoutPersistenceTests : IDisposable
{
    private readonly string _directory = Path.Combine(Path.GetTempPath(), "mew-tests", Guid.NewGuid().ToString("N"));

    private JsonWidgetStateStore CreateStore() => new(_directory, new FakeTimeProvider(), NullLogger<JsonWidgetStateStore>.Instance);

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, recursive: true);
        }
    }

    [Fact]
    public void ItemsBeyondFiveByFive_AreLoaded()
    {
        var state = new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category("c1", "General")],
            [new NoteItem("n1", "c1", new GridPlacement(8, 7, 2, 2), "far away")]);

        CreateStore().Save(state);

        Assert.Equal(state.Items, CreateStore().Load().State!.Items);
    }

    [Fact]
    public void ItemsBeyondMaximumGrid_AreRejected()
    {
        CreateStore().Save(new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category("c1", "General")],
            [new NoteItem("n1", "c1", new GridPlacement(9, 9, 2, 1), "outside")]));

        var result = CreateStore().Load();

        Assert.Null(result.State);
        Assert.NotNull(result.CorruptBackupPath);
    }

    [Fact]
    public void AppEmoji_IsSavedAndLoaded()
    {
        var app = new AppItem("a1", "c1", new GridPlacement(0, 0, 1, 1), "Rocket", "r.exe", LaunchKind.Executable, null) { Emoji = "🚀" };
        CreateStore().Save(new WidgetState(WidgetState.CurrentSchemaVersion, [new Category("c1", "General")], [app]));

        var loaded = Assert.IsType<AppItem>(Assert.Single(CreateStore().Load().State!.Items));

        Assert.Equal("🚀", loaded.Emoji);
    }
}
