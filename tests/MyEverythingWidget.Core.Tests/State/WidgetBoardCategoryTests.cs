using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

public sealed class WidgetBoardCategoryTests
{
    private const string GeneralId = "c1";
    private const string WorkId = "c2";

    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category(GeneralId, "General"), new Category(WorkId, "Work")],
        [
            new AppItem("a1", GeneralId, new GridPlacement(0, 0, 1, 1), "Notepad", "notepad.exe", LaunchKind.Executable, null),
            new NoteItem("n1", WorkId, new GridPlacement(0, 0, 2, 1), "Standup"),
        ]));

    private int _nextId;

    private WidgetBoard CreateBoard(GridSize? size = null) =>
        new(_store, () => $"new{++_nextId}", size ?? GridSize.Default, NullLogger<WidgetBoard>.Instance);

    [Fact]
    public void AddCategory_AppendsTrimmedNameAndSaves()
    {
        var board = CreateBoard();

        var added = board.AddCategory("  Music  ");

        Assert.Equal("Music", added.Name);
        Assert.Equal([GeneralId, WorkId, added.Id], board.Categories.Select(category => category.Id));
        Assert.Equal(3, _store.Current!.Categories.Count);
    }

    [Theory]
    [InlineData("")]
    [InlineData("  ")]
    public void AddCategory_WithBlankName_Throws(string name)
    {
        Assert.Throws<ArgumentException>(() => CreateBoard().AddCategory(name));
    }

    [Fact]
    public void AddCategory_LongName_IsCutToMaximumLength()
    {
        var added = CreateBoard().AddCategory(new string('x', 60));

        Assert.Equal(WidgetBoard.MaxCategoryNameLength, added.Name.Length);
    }

    [Fact]
    public void RenameCategory_ChangesNameOnly()
    {
        var board = CreateBoard();

        Assert.True(board.RenameCategory(WorkId, " Office "));

        Assert.Equal("Office", board.Categories[1].Name);
        Assert.Equal(WorkId, board.Categories[1].Id);
        Assert.Equal("Office", _store.Current!.Categories[1].Name);
    }

    [Fact]
    public void RenameCategory_Unknown_ReturnsFalse()
    {
        Assert.False(CreateBoard().RenameCategory("missing", "x"));
    }

    [Fact]
    public void DeleteCategory_RemovesItsItemsOnly()
    {
        var board = CreateBoard();

        Assert.True(board.DeleteCategory(WorkId));

        Assert.Equal([GeneralId], board.Categories.Select(category => category.Id));
        Assert.Null(board.Find("n1"));
        Assert.NotNull(board.Find("a1"));
    }

    [Fact]
    public void DeleteCategory_LastOne_IsRefused()
    {
        var board = CreateBoard();
        board.DeleteCategory(WorkId);

        Assert.False(board.DeleteCategory(GeneralId));

        Assert.Single(board.Categories);
    }

    [Fact]
    public void DeleteCategory_Selected_SelectsNeighbour()
    {
        var board = CreateBoard();
        board.SelectCategory(WorkId);

        board.DeleteCategory(WorkId);

        Assert.Equal(GeneralId, board.SelectedCategoryId);
    }

    [Fact]
    public void ReorderCategories_AppliesGivenOrder()
    {
        var board = CreateBoard();
        var music = board.AddCategory("Music");

        board.ReorderCategories([music.Id, GeneralId, WorkId]);

        Assert.Equal([music.Id, GeneralId, WorkId], board.Categories.Select(category => category.Id));
        Assert.Equal([music.Id, GeneralId, WorkId], _store.Current!.Categories.Select(category => category.Id));
    }

    [Fact]
    public void ReorderCategories_WithDifferentSet_Throws()
    {
        var board = CreateBoard();

        Assert.Throws<ArgumentException>(() => board.ReorderCategories([WorkId]));
    }

    [Fact]
    public void MoveItemToCategory_TakesFirstFreeCellThere()
    {
        var board = CreateBoard();

        var outcome = board.MoveItemToCategory("a1", WorkId);

        Assert.Equal(GridOutcome.Success, outcome);
        var moved = board.Find("a1")!;
        Assert.Equal(WorkId, moved.CategoryId);
        Assert.Equal(new GridPlacement(0, 2, 1, 1), moved.Placement);
        Assert.Empty(board.ItemsIn(GeneralId));
    }

    [Fact]
    public void MoveItemToCategory_WhenTargetFull_KeepsItem()
    {
        var board = CreateBoard(new GridSize(1, 2));

        var outcome = board.MoveItemToCategory("a1", WorkId);

        Assert.Equal(GridOutcome.GridFull, outcome);
        Assert.Equal(GeneralId, board.Find("a1")!.CategoryId);
    }

    [Fact]
    public void MoveItemToCategory_SameCategory_DoesNothing()
    {
        var board = CreateBoard();
        var savesBefore = _store.SaveCount;

        Assert.Equal(GridOutcome.Success, board.MoveItemToCategory("a1", GeneralId));

        Assert.Equal(savesBefore, _store.SaveCount);
    }

    [Fact]
    public void SelectCategory_IsSavedAndRestored()
    {
        CreateBoard().SelectCategory(WorkId);

        var reopened = CreateBoard();

        Assert.Equal(WorkId, reopened.SelectedCategoryId);
    }

    [Fact]
    public void SelectedCategory_DefaultsToFirst()
    {
        Assert.Equal(GeneralId, CreateBoard().SelectedCategoryId);
    }

    [Fact]
    public void SelectedCategory_PointingToDeletedCategory_FallsBackToFirst()
    {
        var store = new InMemoryWidgetStateStore(new WidgetState(
            WidgetState.CurrentSchemaVersion, [new Category(GeneralId, "General")], []) { SelectedCategoryId = "gone" });

        var board = new WidgetBoard(store, () => "x", GridSize.Default, NullLogger<WidgetBoard>.Instance);

        Assert.Equal(GeneralId, board.SelectedCategoryId);
    }
}
