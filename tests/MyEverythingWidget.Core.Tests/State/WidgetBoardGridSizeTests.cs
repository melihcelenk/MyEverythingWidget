using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

/// <summary>The grid follows the window size: at least 2x2, never smaller than the items need.</summary>
public sealed class WidgetBoardGridSizeTests
{
    private static WidgetBoard CreateBoard(GridSize size, params WidgetItem[] items) => new(
        new InMemoryWidgetStateStore(new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category("c1", "General"), new Category("c2", "Work")],
            items)),
        () => "new",
        size,
        NullLogger<WidgetBoard>.Instance);

    private static AppItem App(string id, string categoryId, int row, int column) =>
        new(id, categoryId, new GridPlacement(row, column, 1, 1), id, "a.exe", LaunchKind.Executable, null);

    [Fact]
    public void Limits_Are2x2And10x10()
    {
        Assert.Equal(new GridSize(2, 2), GridSize.Minimum);
        Assert.Equal(new GridSize(10, 10), GridSize.Maximum);
    }

    [Fact]
    public void MinimumGridSize_OfEmptyBoard_Is2x2()
    {
        Assert.Equal(GridSize.Minimum, CreateBoard(GridSize.Default).MinimumGridSize);
    }

    [Fact]
    public void MinimumGridSize_CoversItemsOfEveryCategory()
    {
        var board = CreateBoard(
            GridSize.Default,
            App("a1", "c1", row: 0, column: 3),
            new NoteItem("n1", "c2", new GridPlacement(2, 0, 2, 2), "x"));

        Assert.Equal(new GridSize(Rows: 4, Columns: 4), board.MinimumGridSize);
    }

    [Fact]
    public void ResizeGrid_SetsSizeAndRaisesChanged()
    {
        var board = CreateBoard(GridSize.Default);
        var changed = 0;
        board.Changed += (_, _) => changed++;

        var applied = board.ResizeGrid(new GridSize(3, 4));

        Assert.Equal(new GridSize(3, 4), applied);
        Assert.Equal(new GridSize(3, 4), board.GridSize);
        Assert.Equal(1, changed);
    }

    [Fact]
    public void ResizeGrid_ToSameSize_DoesNotRaiseChanged()
    {
        var board = CreateBoard(GridSize.Default);
        var changed = 0;
        board.Changed += (_, _) => changed++;

        board.ResizeGrid(GridSize.Default);

        Assert.Equal(0, changed);
    }

    [Fact]
    public void ResizeGrid_IsClampedBetweenMinimumAndMaximum()
    {
        var board = CreateBoard(GridSize.Default, App("a1", "c2", row: 2, column: 1));

        Assert.Equal(new GridSize(Rows: 3, Columns: 2), board.ResizeGrid(new GridSize(1, 1)));
        Assert.Equal(GridSize.Maximum, board.ResizeGrid(new GridSize(30, 40)));
    }

    [Fact]
    public void ResizeGrid_Larger_MakesRoomForNewItems()
    {
        var board = CreateBoard(
            GridSize.Minimum,
            App("a1", "c1", 0, 0), App("a2", "c1", 0, 1), App("a3", "c1", 1, 0), App("a4", "c1", 1, 1));
        Assert.Equal(GridOutcome.GridFull, board.AddApp("c1", "X", "x.exe", LaunchKind.Executable, null).Outcome);

        board.ResizeGrid(new GridSize(Rows: 2, Columns: 3));
        var added = board.AddApp("c1", "X", "x.exe", LaunchKind.Executable, null);

        Assert.Equal(GridOutcome.Success, added.Outcome);
        Assert.Equal(new GridPlacement(0, 2, 1, 1), added.Item!.Placement);
    }

    [Fact]
    public void NewBoard_SmallerThanItsItems_GrowsToFitThem()
    {
        var board = CreateBoard(GridSize.Minimum, App("a1", "c1", row: 4, column: 4));

        Assert.Equal(GridSize.Default, board.GridSize);
    }
}
