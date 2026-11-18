using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>First-run import of the Python version's data (MEW-4 D1).</summary>
public sealed class LegacyMigratorTests : IDisposable
{
    private readonly string _legacyDirectory = Path.Combine(Path.GetTempPath(), "mew-legacy", Guid.NewGuid().ToString("N"));
    private readonly FakeAppServices _apps = new();
    private readonly RecordingImageStore _images = new();

    public LegacyMigratorTests() => Directory.CreateDirectory(Path.Combine(_legacyDirectory, "data", "images"));

    public void Dispose() => Directory.Delete(_legacyDirectory, recursive: true);

    private string LegacyFile => Path.Combine(_legacyDirectory, "app_state.json");

    private int _nextId;

    private LegacyMigrator CreateMigrator(InMemoryWidgetStateStore store) =>
        new(store, _apps, _images, () => $"id{++_nextId}", GridSize.Default);

    private void WriteLegacy(string imagePath)
    {
        var json = $$"""
            { "categories": [{ "name": "Work" }],
              "apps": [{ "name": "Notepad", "target": "C:\\Windows\\notepad.exe", "category": "Work", "type": "exe",
                         "grid_row": 0, "grid_col": 0, "col_span": 1, "row_span": 1 }],
              "notes": [{ "content": "Buy milk", "type": "text", "category": "Work", "grid_row": 1, "grid_col": 0, "col_span": 2, "row_span": 1 },
                        { "content": "{{imagePath.Replace("\\", "\\\\", StringComparison.Ordinal)}}", "type": "image", "category": "Work",
                          "grid_row": 2, "grid_col": 0, "col_span": 2, "row_span": 2 }] }
            """;
        File.WriteAllText(LegacyFile, json);
    }

    [Fact]
    public async Task NoLegacyFile_DoesNothing()
    {
        var store = new InMemoryWidgetStateStore(null);

        var result = await CreateMigrator(store).MigrateAsync(LegacyFile, TestContext.Current.CancellationToken);

        Assert.Equal(MigrationOutcome.NoLegacyData, result.Outcome);
        Assert.Null(store.Current);
    }

    [Fact]
    public async Task ExistingState_IsNeverOverwritten()
    {
        WriteLegacy(@"C:\nowhere.png");
        var existing = WidgetState.CreateDefault("c1");
        var store = new InMemoryWidgetStateStore(existing);

        var result = await CreateMigrator(store).MigrateAsync(LegacyFile, TestContext.Current.CancellationToken);

        Assert.Equal(MigrationOutcome.NotNeeded, result.Outcome);
        Assert.Same(existing, store.Current);
    }

    [Fact]
    public async Task FirstRun_ImportsItemsWithIconsAndImages()
    {
        var image = Path.Combine(_legacyDirectory, "data", "images", "shot.png");
        File.WriteAllBytes(image, [1, 2, 3]);
        WriteLegacy(image);
        var store = new InMemoryWidgetStateStore(null);

        var result = await CreateMigrator(store).MigrateAsync(LegacyFile, TestContext.Current.CancellationToken);

        Assert.Equal(MigrationOutcome.Imported, result.Outcome);
        Assert.Equal(3, result.ImportedItems);
        Assert.Equal(0, result.MissingImages);
        var state = store.Current!;
        Assert.Equal("Work", Assert.Single(state.Categories).Name);
        Assert.Equal("icons/fake.png", state.Items.OfType<AppItem>().Single().IconPath);
        var imported = state.Items.OfType<ImageItem>().Single();
        Assert.Equal(new GridPlacement(2, 0, 2, 2), imported.Placement);
        Assert.Equal(_images.SavedPath, imported.ImagePath);
    }

    [Fact]
    public async Task RelativeImagePath_IsLookedUpNextToLegacyFile()
    {
        File.WriteAllBytes(Path.Combine(_legacyDirectory, "data", "images", "shot.png"), [1]);
        WriteLegacy(@"data\images\shot.png");
        var store = new InMemoryWidgetStateStore(null);

        var result = await CreateMigrator(store).MigrateAsync(LegacyFile, TestContext.Current.CancellationToken);

        Assert.Equal(0, result.MissingImages);
        Assert.Single(store.Current!.Items.OfType<ImageItem>());
    }

    [Fact]
    public async Task MissingImage_IsSkippedAndCounted()
    {
        WriteLegacy(@"C:\gone\shot.png");
        var store = new InMemoryWidgetStateStore(null);

        var result = await CreateMigrator(store).MigrateAsync(LegacyFile, TestContext.Current.CancellationToken);

        Assert.Equal(MigrationOutcome.Imported, result.Outcome);
        Assert.Equal(2, result.ImportedItems);
        Assert.Equal(1, result.MissingImages);
        Assert.Empty(store.Current!.Items.OfType<ImageItem>());
    }

    [Fact]
    public async Task UnreadableLegacyFile_ReportsFailureAndWritesNothing()
    {
        File.WriteAllText(LegacyFile, "{ broken");
        var store = new InMemoryWidgetStateStore(null);

        var result = await CreateMigrator(store).MigrateAsync(LegacyFile, TestContext.Current.CancellationToken);

        Assert.Equal(MigrationOutcome.Failed, result.Outcome);
        Assert.Null(store.Current);
    }

    [Fact]
    public void Message_DescribesResult()
    {
        Assert.Equal(
            "Imported 3 items from the previous version of My Everything Widget.",
            new MigrationResult(MigrationOutcome.Imported, 3, 0).Message);
        Assert.Equal(
            "Imported 2 items from the previous version of My Everything Widget. 1 image could not be found.",
            new MigrationResult(MigrationOutcome.Imported, 2, 1).Message);
        Assert.Null(new MigrationResult(MigrationOutcome.NoLegacyData, 0, 0).Message);
    }

    private sealed class RecordingImageStore : IImageStore
    {
        public string? SavedPath { get; private set; }

        public Task<StoredImage?> ImportAsync(Stream image, CancellationToken cancellationToken)
        {
            SavedPath = @"images\imported.png";
            return Task.FromResult<StoredImage?>(new StoredImage(SavedPath, 800, 800));
        }

        public void Delete(string relativePath)
        {
            // Nothing to delete in this fake.
        }
    }
}
