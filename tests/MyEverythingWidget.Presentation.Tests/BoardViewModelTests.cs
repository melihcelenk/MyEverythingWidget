using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

public sealed class BoardViewModelTests
{
    private const string GeneralId = "c1";
    private const string WorkId = "c2";

    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category(GeneralId, "General"), new Category(WorkId, "Work")],
        [
            new AppItem("a1", GeneralId, new GridPlacement(0, 0, 1, 1), "Notepad", "notepad.exe", LaunchKind.Executable, null),
            new AppItem("a2", GeneralId, new GridPlacement(0, 2, 1, 1), "Paint", "mspaint.exe", LaunchKind.Executable, null),
            new NoteItem("n1", GeneralId, new GridPlacement(1, 0, 2, 1), "Buy milk"),
            new NoteItem("n2", WorkId, new GridPlacement(0, 0, 2, 1), "Standup 10:00"),
        ]));

    private int _nextId;

    private WidgetBoard CreateBoard() =>
        new(_store, () => $"new{++_nextId}", GridSize.Default, NullLogger<WidgetBoard>.Instance);

    private static GridItemViewModel Item(BoardViewModel viewModel, string id) => viewModel.Items.Single(item => item.Id == id);

    [Fact]
    public void Items_ShowFirstCategoryWithPositions()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        Assert.Equal(GeneralId, viewModel.SelectedCategoryId);
        Assert.Equal(["a1", "a2", "n1"], viewModel.Items.Select(item => item.Id).Order());
        var note = Item(viewModel, "n1");
        Assert.Equal((1, 0, 2, 1), (note.Row, note.Column, note.ColumnSpan, note.RowSpan));
        Assert.Equal(ItemKind.Note, note.Kind);
        Assert.Equal("Buy milk", note.Text);
        Assert.Equal("Notepad", Item(viewModel, "a1").Title);
    }

    [Fact]
    public void GridSize_ComesFromBoard()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        Assert.Equal(GridSize.Default, viewModel.GridSize);
    }

    [Fact]
    public void Drop_OntoOtherItem_UpdatesExistingItemViewModelsInPlace()
    {
        var viewModel = new BoardViewModel(CreateBoard());
        var first = Item(viewModel, "a1");
        var second = Item(viewModel, "a2");

        var dropped = viewModel.Drop("a1", new GridCell(0, 2));

        Assert.True(dropped);
        Assert.Same(first, Item(viewModel, "a1"));
        Assert.Equal((0, 2), (first.Row, first.Column));
        Assert.Equal((0, 0), (second.Row, second.Column));
        Assert.Null(viewModel.StatusMessage);
    }

    [Fact]
    public void Drop_OutsideGrid_KeepsPositionsWithoutMessage()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        var dropped = viewModel.Drop("n1", new GridCell(1, 4));

        Assert.False(dropped);
        Assert.Equal((1, 0), (Item(viewModel, "n1").Row, Item(viewModel, "n1").Column));
        Assert.Null(viewModel.StatusMessage);
    }

    [Fact]
    public void Drop_WithoutRoomForDisplacedItems_ShowsWarning()
    {
        var store = new InMemoryWidgetStateStore(FullRowState());
        var viewModel = new BoardViewModel(new WidgetBoard(store, () => "x", new GridSize(2, 3), NullLogger<WidgetBoard>.Instance));

        var dropped = viewModel.Drop("a1", new GridCell(0, 1));

        Assert.False(dropped);
        Assert.Equal(StatusSeverity.Warning, viewModel.StatusSeverity);
        Assert.Equal(BoardViewModel.NoRoomMessage, viewModel.StatusMessage);
    }

    [Fact]
    public void PreviewDrop_OnFreeCells_IsDroppableAndCoversSpan()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        var preview = viewModel.PreviewDrop("n1", new GridCell(3, 2));

        Assert.True(preview.CanDrop);
        Assert.Equal(new GridPlacement(3, 2, 2, 1), preview.Placement);
    }

    [Fact]
    public void PreviewDrop_PastEdge_IsNotDroppable()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        var preview = viewModel.PreviewDrop("n1", new GridCell(1, 4));

        Assert.False(preview.CanDrop);
        Assert.Equal(new GridPlacement(1, 4, 2, 1), preview.Placement);
    }

    [Fact]
    public void PreviewDrop_DoesNotChangeOrSaveState()
    {
        var board = CreateBoard();
        var viewModel = new BoardViewModel(board);
        var savesBefore = _store.SaveCount;

        _ = viewModel.PreviewDrop("a1", new GridCell(4, 4));

        Assert.Equal(savesBefore, _store.SaveCount);
        Assert.Equal(new GridCell(0, 0), board.Find("a1")!.Placement.Anchor);
    }

    [Fact]
    public void Resize_IntoFreeCells_UpdatesSpan()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        Assert.True(viewModel.Resize("n1", new GridSpan(3, 2)));

        Assert.Equal((3, 2), (Item(viewModel, "n1").ColumnSpan, Item(viewModel, "n1").RowSpan));
    }

    [Fact]
    public void PreviewResize_BlockedByItem_IsNotDroppable()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        var preview = viewModel.PreviewResize("a1", new GridSpan(3, 1));

        Assert.False(preview.CanDrop);
        Assert.Equal(new GridPlacement(0, 0, 3, 1), preview.Placement);
    }

    [Fact]
    public void Delete_RemovesItemViewModel()
    {
        var viewModel = new BoardViewModel(CreateBoard());

        viewModel.DeleteCommand.Execute("a2");

        Assert.DoesNotContain(viewModel.Items, item => item.Id == "a2");
        Assert.Equal((0, 0), (Item(viewModel, "a1").Row, Item(viewModel, "a1").Column));
    }

    [Fact]
    public void BoardChange_AddsItemViewModel()
    {
        var board = CreateBoard();
        var viewModel = new BoardViewModel(board);

        var added = board.AddNote(GeneralId, "New").Item!;

        Assert.Contains(viewModel.Items, item => item.Id == added.Id);
    }

    [Fact]
    public void CorruptStateOnStartup_ShowsWarningWithBackupPath()
    {
        var store = new InMemoryWidgetStateStore(null) { CorruptBackupPath = @"C:\data\state.corrupt-1.json" };

        var viewModel = new BoardViewModel(new WidgetBoard(store, () => "c", GridSize.Default, NullLogger<WidgetBoard>.Instance));

        Assert.Equal(StatusSeverity.Warning, viewModel.StatusSeverity);
        Assert.Contains(@"C:\data\state.corrupt-1.json", viewModel.StatusMessage, StringComparison.Ordinal);
    }

    [Fact]
    public void SaveFailure_ShowsError()
    {
        var viewModel = new BoardViewModel(CreateBoard());
        _store.FailNextSaveWith = new IOException("disk full");

        viewModel.Drop("a1", new GridCell(4, 4));

        Assert.Equal(StatusSeverity.Error, viewModel.StatusSeverity);
        Assert.Contains("disk full", viewModel.StatusMessage, StringComparison.Ordinal);
    }

    [Fact]
    public void DismissStatus_ClearsMessage()
    {
        var store = new InMemoryWidgetStateStore(FullRowState());
        var viewModel = new BoardViewModel(new WidgetBoard(store, () => "x", new GridSize(2, 3), NullLogger<WidgetBoard>.Instance));
        viewModel.Drop("a1", new GridCell(0, 1));

        viewModel.DismissStatusCommand.Execute(null);

        Assert.Null(viewModel.StatusMessage);
    }

    private static WidgetState FullRowState() => new(
        WidgetState.CurrentSchemaVersion,
        [new Category(GeneralId, "General")],
        [
            new AppItem("a1", GeneralId, new GridPlacement(0, 0, 1, 1), "A1", "a1.exe", LaunchKind.Executable, null),
            new NoteItem("n1", GeneralId, new GridPlacement(0, 1, 2, 1), "N1"),
            new AppItem("a2", GeneralId, new GridPlacement(1, 0, 1, 1), "A2", "a2.exe", LaunchKind.Executable, null),
            new AppItem("a3", GeneralId, new GridPlacement(1, 1, 1, 1), "A3", "a3.exe", LaunchKind.Executable, null),
            new AppItem("a4", GeneralId, new GridPlacement(1, 2, 1, 1), "A4", "a4.exe", LaunchKind.Executable, null),
        ]);
}
