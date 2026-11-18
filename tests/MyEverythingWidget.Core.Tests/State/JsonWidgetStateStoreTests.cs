using System.Text.Json;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Time.Testing;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

public sealed class JsonWidgetStateStoreTests : IDisposable
{
    private readonly string _directory = Path.Combine(Path.GetTempPath(), "mew-tests", Guid.NewGuid().ToString("N"));
    private readonly FakeTimeProvider _time = new(new DateTimeOffset(2026, 10, 30, 3, 4, 5, TimeSpan.Zero));

    private string StatePath => Path.Combine(_directory, "state.json");

    private JsonWidgetStateStore CreateStore() => new(_directory, _time, NullLogger<JsonWidgetStateStore>.Instance);

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, recursive: true);
        }
    }

    [Fact]
    public void Load_WhenFileIsMissing_ReturnsNoState()
    {
        var result = CreateStore().Load();

        Assert.Null(result.State);
        Assert.Null(result.CorruptBackupPath);
    }

    [Fact]
    public void Save_ThenLoad_RestoresEveryItemKind()
    {
        var state = new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category("c1", "General"), new Category("c2", "Work")],
            [
                new AppItem("a1", "c1", new GridPlacement(0, 0, 1, 1), "Notepad", @"C:\Windows\notepad.exe", LaunchKind.Executable, IconPath: "icons/a1.png"),
                new NoteItem("n1", "c1", new GridPlacement(1, 2, 2, 1), "Buy milk"),
                new ImageItem("i1", "c2", new GridPlacement(2, 0, 3, 2), "images/i1.png", 1920, 1080),
            ]);

        CreateStore().Save(state);
        var loaded = CreateStore().Load().State;

        Assert.NotNull(loaded);
        Assert.Equal(state.SchemaVersion, loaded.SchemaVersion);
        Assert.Equal(state.Categories, loaded.Categories);
        Assert.Equal(state.Items, loaded.Items);
    }

    [Fact]
    public void Save_WritesVersionedReadableJson()
    {
        CreateStore().Save(new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category("c1", "General")],
            [new NoteItem("n1", "c1", new GridPlacement(1, 2, 2, 1), "Hello")]));

        using var json = JsonDocument.Parse(File.ReadAllText(StatePath));
        var root = json.RootElement;
        var item = root.GetProperty("items")[0];

        Assert.Equal(1, root.GetProperty("schemaVersion").GetInt32());
        Assert.Equal("note", item.GetProperty("kind").GetString());
        Assert.Equal(1, item.GetProperty("placement").GetProperty("row").GetInt32());
        Assert.Equal(2, item.GetProperty("placement").GetProperty("column").GetInt32());
        Assert.Equal(2, item.GetProperty("placement").GetProperty("columns").GetInt32());
        Assert.Equal(1, item.GetProperty("placement").GetProperty("rows").GetInt32());
    }

    [Fact]
    public void Load_WhenFileIsCorrupt_ReturnsNoStateAndBackupPath()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(StatePath, "{ \"items\": [");

        var result = CreateStore().Load();

        Assert.Null(result.State);
        Assert.Equal(Path.Combine(_directory, "state.corrupt-20261030-030405.json"), result.CorruptBackupPath);
        Assert.True(File.Exists(result.CorruptBackupPath));
        Assert.False(File.Exists(StatePath));
    }

    [Fact]
    public void Load_WhenPlacementIsInvalid_TreatsFileAsCorrupt()
    {
        Directory.CreateDirectory(_directory);
        File.WriteAllText(StatePath, """
            { "schemaVersion": 1, "categories": [], "items": [
              { "kind": "note", "id": "n1", "categoryId": "c1", "text": "x",
                "placement": { "row": 0, "column": 0, "columns": 9, "rows": 1 } } ] }
            """);

        var result = CreateStore().Load();

        Assert.Null(result.State);
        Assert.NotNull(result.CorruptBackupPath);
    }
}
