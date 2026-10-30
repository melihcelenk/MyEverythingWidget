using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Legacy;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.Legacy;

/// <summary>Reading and converting the Python version's <c>app_state.json</c> (MEW-4 D1).</summary>
public sealed class LegacyImportTests
{
    private const string Sample = """
        {
          "categories": [
            { "id": "0b6c-uuid", "name": "Work", "icon": "💼" },
            { "id": "77aa-uuid", "name": "Music", "icon": "🎵" }
          ],
          "apps": [
            { "id": "a1", "name": "Notepad", "icon_path": "📝", "target": "C:\\Windows\\notepad.exe", "category": "Work",
              "type": "exe", "order": 0, "grid_row": 0, "grid_col": 0, "col_span": 1, "row_span": 1 },
            { "id": "a2", "name": "GitHub", "icon_path": "C:\\icons\\gh.png", "target": "https://github.com", "category": "Work",
              "type": "url", "order": 1, "grid_row": 0, "grid_col": 0, "col_span": 1, "row_span": 1 },
            { "id": "a3", "name": "Projects", "icon_path": "📁", "target": "C:\\Projects", "category": "Gone",
              "type": "folder", "order": 2 }
          ],
          "notes": [
            { "id": "n1", "content": "Buy milk", "type": "text", "category": "Work", "created_at": "2025-11-20T10:00:00+00:00",
              "updated_at": "2025-11-20T10:00:00+00:00", "order": 0, "grid_row": 1, "grid_col": 3, "col_span": 2, "row_span": 1 },
            { "id": "n2", "content": "data\\images\\shot.png", "type": "image", "category": "Music", "created_at": "2025-11-20T10:00:00+00:00",
              "updated_at": "2025-11-20T10:00:00+00:00", "order": 1, "grid_row": 0, "grid_col": 0, "col_span": 2, "row_span": 2 },
            { "id": "n3", "content": "https://youtube.com", "type": "link", "category": "Music", "created_at": "2025-11-20T10:00:00+00:00",
              "updated_at": "2025-11-20T10:00:00+00:00", "order": 2, "grid_row": 4, "grid_col": 4, "col_span": 3, "row_span": 1 }
          ]
        }
        """;

    private int _nextId;

    private LegacyImport Import() =>
        LegacyImporter.Build(LegacyStateReader.Parse(Sample), () => $"id{++_nextId}", GridSize.Default);

    [Fact]
    public void Parse_ReadsCategoriesAppsAndNotes()
    {
        var data = LegacyStateReader.Parse(Sample);

        Assert.Equal(["Work", "Music"], data.Categories);
        Assert.Equal(3, data.Apps.Count);
        Assert.Equal(new LegacyApp("Notepad", @"C:\Windows\notepad.exe", LaunchKind.Executable, "Work", new GridPlacement(0, 0, 1, 1)), data.Apps[0]);
        Assert.Null(data.Apps[2].Placement);
        Assert.Equal(3, data.Notes.Count);
        Assert.Equal(new LegacyNote("Buy milk", LegacyNoteKind.Text, "Work", new GridPlacement(1, 3, 2, 1)), data.Notes[0]);
    }

    [Fact]
    public void Parse_NotJson_Throws()
    {
        Assert.ThrowsAny<System.Text.Json.JsonException>(() => LegacyStateReader.Parse("{ nope"));
    }

    [Fact]
    public void Build_KeepsCategoriesInOrder()
    {
        var import = Import();

        Assert.Equal(["Work", "Music"], import.State.Categories.Select(category => category.Name));
    }

    [Fact]
    public void Build_KeepsValidPlacements()
    {
        var import = Import();
        var work = import.State.Categories[0].Id;

        var notepad = import.State.Items.OfType<AppItem>().Single(app => app.Name == "Notepad");
        var note = import.State.Items.OfType<NoteItem>().Single();
        Assert.Equal((work, new GridPlacement(0, 0, 1, 1)), (notepad.CategoryId, notepad.Placement));
        Assert.Equal((work, new GridPlacement(1, 3, 2, 1)), (note.CategoryId, note.Placement));
    }

    [Fact]
    public void Build_OverlappingPlacement_MovesToFirstFreeCell()
    {
        var github = Import().State.Items.OfType<AppItem>().Single(app => app.Name == "GitHub");

        Assert.Equal(new GridPlacement(0, 1, 1, 1), github.Placement);
    }

    [Fact]
    public void Build_UnknownCategory_GoesToFirstCategory()
    {
        var import = Import();

        var projects = import.State.Items.OfType<AppItem>().Single(app => app.Name == "Projects");
        Assert.Equal(import.State.Categories[0].Id, projects.CategoryId);
        Assert.Equal(LaunchKind.Folder, projects.LaunchKind);
    }

    [Fact]
    public void Build_LinkNote_BecomesAppCardInItsOwnCell()
    {
        var import = Import();
        var music = import.State.Categories[1].Id;

        // The 3x1 link note becomes a 1x1 app card; as 1x1 it fits its own top-left cell, so it stays there.
        var link = import.State.Items.OfType<AppItem>().Single(app => app.Target == "https://youtube.com");
        Assert.Equal(music, link.CategoryId);
        Assert.Equal(LaunchKind.Url, link.LaunchKind);
        Assert.Equal(new GridPlacement(4, 4, 1, 1), link.Placement);
    }

    [Fact]
    public void Build_PlacementPastEdge_MovesToFirstFreeCell()
    {
        var data = LegacyStateReader.Parse("""
            { "categories": [{ "name": "Work" }], "apps": [],
              "notes": [{ "content": "wide", "type": "text", "category": "Work", "grid_row": 0, "grid_col": 4, "col_span": 2, "row_span": 1 }] }
            """);

        var note = Assert.Single(LegacyImporter.Build(data, () => $"id{++_nextId}", GridSize.Default).State.Items);

        Assert.Equal(new GridPlacement(0, 0, 2, 1), note.Placement);
    }

    [Fact]
    public void Build_AppsNeedNewIcons_EmojiAreDropped()
    {
        var import = Import();

        Assert.All(import.State.Items.OfType<AppItem>(), app => Assert.Null(app.IconPath));
        Assert.Equal(4, import.AppsNeedingIcons.Count);
    }

    [Fact]
    public void Build_ImageNotes_AreListedForCopying()
    {
        var import = Import();

        var image = Assert.Single(import.Images);
        Assert.Equal(@"data\images\shot.png", image.SourcePath);
        Assert.Equal(new GridPlacement(0, 0, 2, 2), image.Placement);
        Assert.Equal(import.State.Categories[1].Id, image.CategoryId);
        Assert.Empty(import.State.Items.OfType<ImageItem>());
    }

    [Fact]
    public void Build_WithoutCategories_CreatesGeneral()
    {
        var data = LegacyStateReader.Parse("""{ "categories": [], "apps": [], "notes": [{ "content": "x", "type": "text", "category": "?" }] }""");

        var import = LegacyImporter.Build(data, () => "c", GridSize.Default);

        Assert.Equal(WidgetState.DefaultCategoryName, Assert.Single(import.State.Categories).Name);
        Assert.Single(import.State.Items);
    }
}
