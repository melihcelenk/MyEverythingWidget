using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

public sealed class WidgetBoardTests
{
    private int _nextId;

    private string NewId() => $"id{++_nextId}";

    private WidgetBoard CreateBoard(InMemoryWidgetStateStore store, GridSize? size = null) =>
        new(store, NewId, size ?? GridSize.Default, NullLogger<WidgetBoard>.Instance);

    private static string GeneralId(WidgetBoard board) => board.Categories[0].Id;

    [Fact]
    public void NewBoard_WithoutStoredState_CreatesGeneralCategoryAndSaves()
    {
        var store = new InMemoryWidgetStateStore();

        var board = CreateBoard(store);

        Assert.Equal("General", Assert.Single(board.Categories).Name);
        Assert.Empty(board.State.Items);
        Assert.Equal(1, store.SaveCount);
    }

    [Fact]
    public void NewBoard_AfterCorruptFile_ReportsBackupPath()
    {
        var store = new InMemoryWidgetStateStore { CorruptBackupPath = @"C:\data\state.corrupt-1.json" };

        var board = CreateBoard(store);

        Assert.Equal(@"C:\data\state.corrupt-1.json", board.CorruptBackupPath);
        Assert.Single(board.Categories);
    }

    [Fact]
    public void AddApp_PlacesAtFirstFreeCellAndSaves()
    {
        var store = new InMemoryWidgetStateStore();
        var board = CreateBoard(store);

        var result = board.AddApp(GeneralId(board), "Notepad", @"C:\Windows\notepad.exe", LaunchKind.Executable, iconPath: null);

        Assert.Equal(GridOutcome.Success, result.Outcome);
        var app = Assert.IsType<AppItem>(result.Item);
        Assert.Equal(new GridPlacement(0, 0, 1, 1), app.Placement);
        Assert.Equal("Notepad", app.Name);
        Assert.Same(app, Assert.Single(store.Current!.Items));
    }

    [Fact]
    public void AddNote_Is2x1AfterExistingApp()
    {
        var board = CreateBoard(new InMemoryWidgetStateStore());
        board.AddApp(GeneralId(board), "A", "a.exe", LaunchKind.Executable, iconPath: null);

        var note = Assert.IsType<NoteItem>(board.AddNote(GeneralId(board), "Buy milk").Item);

        Assert.Equal(new GridPlacement(0, 1, 2, 1), note.Placement);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void AddNote_WithBlankText_Throws(string text)
    {
        var board = CreateBoard(new InMemoryWidgetStateStore());

        Assert.Throws<ArgumentException>(() => board.AddNote(GeneralId(board), text));
    }

    [Fact]
    public void AddImage_UsesGivenSpan()
    {
        var board = CreateBoard(new InMemoryWidgetStateStore());

        var image = Assert.IsType<ImageItem>(board.AddImage(GeneralId(board), "images/a.png", 1600, 900, new GridSpan(3, 2)).Item);

        Assert.Equal(new GridPlacement(0, 0, 3, 2), image.Placement);
        Assert.Equal(1600, image.PixelWidth);
    }

    [Fact]
    public void Add_WhenCategoryIsFull_ReturnsGridFullAndDoesNotSave()
    {
        var store = new InMemoryWidgetStateStore();
        var board = CreateBoard(store, new GridSize(1, 1));
        board.AddApp(GeneralId(board), "A", "a.exe", LaunchKind.Executable, iconPath: null);
        var savesBefore = store.SaveCount;

        var result = board.AddApp(GeneralId(board), "B", "b.exe", LaunchKind.Executable, iconPath: null);

        Assert.Equal(GridOutcome.GridFull, result.Outcome);
        Assert.Null(result.Item);
        Assert.Single(board.State.Items);
        Assert.Equal(savesBefore, store.SaveCount);
    }

    [Fact]
    public void Add_ToUnknownCategory_Throws()
    {
        var board = CreateBoard(new InMemoryWidgetStateStore());

        Assert.Throws<ArgumentException>(() => board.AddNote("missing", "x"));
    }

    [Fact]
    public void Move_OntoOtherApp_SwapsBothAndSaves()
    {
        var store = new InMemoryWidgetStateStore();
        var board = CreateBoard(store);
        var first = board.AddApp(GeneralId(board), "A", "a.exe", LaunchKind.Executable, iconPath: null).Item!;
        var second = board.AddApp(GeneralId(board), "B", "b.exe", LaunchKind.Executable, iconPath: null).Item!;

        var outcome = board.Move(first.Id, new GridCell(0, 1));

        Assert.Equal(GridOutcome.Success, outcome);
        Assert.Equal(new GridCell(0, 1), board.Find(first.Id)!.Placement.Anchor);
        Assert.Equal(new GridCell(0, 0), board.Find(second.Id)!.Placement.Anchor);
        Assert.Equal(new GridCell(0, 0), store.Current!.Items.Single(item => item.Id == second.Id).Placement.Anchor);
    }

    [Fact]
    public void Move_Rejected_KeepsStateAndDoesNotSave()
    {
        var store = new InMemoryWidgetStateStore();
        var board = CreateBoard(store);
        var note = board.AddNote(GeneralId(board), "x").Item!;
        var savesBefore = store.SaveCount;

        var outcome = board.Move(note.Id, new GridCell(0, 4));

        Assert.Equal(GridOutcome.OutOfBounds, outcome);
        Assert.Equal(new GridCell(0, 0), board.Find(note.Id)!.Placement.Anchor);
        Assert.Equal(savesBefore, store.SaveCount);
    }

    [Fact]
    public void Move_UnknownItem_ReturnsUnknownItem()
    {
        var board = CreateBoard(new InMemoryWidgetStateStore());

        Assert.Equal(GridOutcome.UnknownItem, board.Move("missing", new GridCell(0, 0)));
    }

    [Fact]
    public void Resize_ChangesSpanAndSaves()
    {
        var store = new InMemoryWidgetStateStore();
        var board = CreateBoard(store);
        var note = board.AddNote(GeneralId(board), "x").Item!;

        var outcome = board.Resize(note.Id, new GridSpan(3, 2));

        Assert.Equal(GridOutcome.Success, outcome);
        Assert.Equal(new GridSpan(3, 2), store.Current!.Items.Single().Placement.Span);
    }

    [Fact]
    public void Delete_RemovesOnlyThatItem()
    {
        var board = CreateBoard(new InMemoryWidgetStateStore());
        var first = board.AddApp(GeneralId(board), "A", "a.exe", LaunchKind.Executable, iconPath: null).Item!;
        var second = board.AddApp(GeneralId(board), "B", "b.exe", LaunchKind.Executable, iconPath: null).Item!;

        Assert.True(board.Delete(first.Id));

        Assert.Null(board.Find(first.Id));
        Assert.Equal(new GridCell(0, 1), board.Find(second.Id)!.Placement.Anchor);
        Assert.False(board.Delete(first.Id));
    }

    [Fact]
    public void Layouts_AreIndependentPerCategory()
    {
        var general = new Category("c1", "General");
        var work = new Category("c2", "Work");
        var store = new InMemoryWidgetStateStore(new WidgetState(WidgetState.CurrentSchemaVersion, [general, work], []));
        var board = CreateBoard(store);

        var inGeneral = board.AddApp(general.Id, "A", "a.exe", LaunchKind.Executable, iconPath: null).Item!;
        var inWork = board.AddApp(work.Id, "B", "b.exe", LaunchKind.Executable, iconPath: null).Item!;

        Assert.Equal(new GridCell(0, 0), inGeneral.Placement.Anchor);
        Assert.Equal(new GridCell(0, 0), inWork.Placement.Anchor);
        Assert.Equal([inWork.Id], board.LayoutOf(work.Id).Items.Keys);
    }

    [Fact]
    public void Board_RestoresStoredState()
    {
        var store = new InMemoryWidgetStateStore(new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category("c1", "General")],
            [new NoteItem("n1", "c1", new GridPlacement(2, 1, 2, 1), "Saved")]));

        var board = CreateBoard(store);

        Assert.Equal("Saved", Assert.IsType<NoteItem>(board.Find("n1")).Text);
        Assert.Equal(0, store.SaveCount);
    }

    [Fact]
    public void Changed_IsRaisedAfterSuccessfulChangeOnly()
    {
        var board = CreateBoard(new InMemoryWidgetStateStore());
        var raised = 0;
        board.Changed += (_, _) => raised++;

        board.AddNote(GeneralId(board), "x");
        board.Move("missing", new GridCell(0, 0));

        Assert.Equal(1, raised);
    }

    [Fact]
    public void SaveFailure_KeepsChangeInMemoryAndRaisesSaveFailed()
    {
        var store = new InMemoryWidgetStateStore();
        var board = CreateBoard(store);
        Exception? reported = null;
        board.SaveFailed += (_, e) => reported = e.Exception;
        store.FailNextSaveWith = new IOException("disk full");

        var result = board.AddNote(GeneralId(board), "x");

        Assert.Equal(GridOutcome.Success, result.Outcome);
        Assert.Single(board.State.Items);
        Assert.IsType<IOException>(reported);
    }
}
