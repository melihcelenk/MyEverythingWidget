using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

public sealed class BoardViewModelCategoryTests
{
    private const string GeneralId = "c1";
    private const string WorkId = "c2";

    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category(GeneralId, "General"), new Category(WorkId, "Work")],
        [
            new AppItem("a1", GeneralId, new GridPlacement(0, 0, 1, 1), "Notepad", "notepad.exe", LaunchKind.Executable, null),
            new AppItem("a2", GeneralId, new GridPlacement(0, 1, 1, 1), "Paint", "mspaint.exe", LaunchKind.Executable, null),
            new NoteItem("n1", WorkId, new GridPlacement(0, 0, 2, 1), "Standup"),
        ]));

    private int _nextId;

    private BoardViewModel CreateViewModel(GridSize? size = null) =>
        new(new WidgetBoard(_store, () => $"new{++_nextId}", size ?? GridSize.Default, NullLogger<WidgetBoard>.Instance));

    [Fact]
    public void Categories_AreListedInOrderWithItemCounts()
    {
        var viewModel = CreateViewModel();

        Assert.Equal(["General", "Work"], viewModel.Categories.Select(category => category.Name));
        Assert.Equal([2, 1], viewModel.Categories.Select(category => category.ItemCount));
        Assert.True(viewModel.Categories[0].IsSelected);
    }

    [Fact]
    public void SelectCategory_ShowsItsItemsAndIsRemembered()
    {
        var viewModel = CreateViewModel();

        viewModel.SelectCategory(WorkId);

        Assert.Equal(WorkId, viewModel.SelectedCategoryId);
        Assert.Equal(["n1"], viewModel.Items.Select(item => item.Id));
        Assert.True(viewModel.Categories[1].IsSelected);
        Assert.False(viewModel.Categories[0].IsSelected);
        Assert.Equal(WorkId, _store.Current!.SelectedCategoryId);
    }

    [Fact]
    public void AddCategory_AppendsAndSelectsIt()
    {
        var viewModel = CreateViewModel();

        var added = viewModel.AddCategory(BoardViewModel.NewCategoryName);

        Assert.Equal(BoardViewModel.NewCategoryName, viewModel.Categories[^1].Name);
        Assert.Equal(added.Id, viewModel.SelectedCategoryId);
        Assert.Empty(viewModel.Items);
    }

    [Fact]
    public void RenameCategory_UpdatesExistingTabViewModel()
    {
        var viewModel = CreateViewModel();
        var work = viewModel.Categories[1];

        Assert.True(viewModel.RenameCategory(WorkId, "Office"));

        Assert.Same(work, viewModel.Categories[1]);
        Assert.Equal("Office", work.Name);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void RenameCategory_WithBlankName_KeepsOldName(string name)
    {
        var viewModel = CreateViewModel();

        Assert.False(viewModel.RenameCategory(WorkId, name));

        Assert.Equal("Work", viewModel.Categories[1].Name);
    }

    [Fact]
    public void DeleteCategory_RemovesTabAndSelectsNeighbour()
    {
        var viewModel = CreateViewModel();
        viewModel.SelectCategory(WorkId);

        Assert.True(viewModel.DeleteCategory(WorkId));

        Assert.Equal(["General"], viewModel.Categories.Select(category => category.Name));
        Assert.Equal(GeneralId, viewModel.SelectedCategoryId);
        Assert.Equal(2, viewModel.Items.Count);
    }

    [Fact]
    public void CanDeleteCategory_IsFalseForTheLastOne()
    {
        var viewModel = CreateViewModel();
        Assert.True(viewModel.CanDeleteCategory);

        viewModel.DeleteCategory(WorkId);

        Assert.False(viewModel.CanDeleteCategory);
        Assert.False(viewModel.DeleteCategory(GeneralId));
    }

    [Fact]
    public void ReorderCategories_ReordersTabs()
    {
        var viewModel = CreateViewModel();

        viewModel.ReorderCategories([WorkId, GeneralId]);

        Assert.Equal(["Work", "General"], viewModel.Categories.Select(category => category.Name));
    }

    [Fact]
    public void MoveItemToCategory_RemovesCardFromOpenTab()
    {
        var viewModel = CreateViewModel();

        Assert.True(viewModel.MoveItemToCategory("a2", WorkId));

        Assert.Equal(["a1"], viewModel.Items.Select(item => item.Id));
        Assert.Equal([1, 2], viewModel.Categories.Select(category => category.ItemCount));
    }

    [Fact]
    public void MoveItemToCategory_WhenTargetFull_ShowsWarning()
    {
        var viewModel = CreateViewModel(new GridSize(1, 2));

        Assert.False(viewModel.MoveItemToCategory("a1", WorkId));

        Assert.Equal(StatusSeverity.Warning, viewModel.StatusSeverity);
        Assert.Equal("There is no room in Work.", viewModel.StatusMessage);
        Assert.Contains(viewModel.Items, item => item.Id == "a1");
    }

    [Fact]
    public void OtherCategories_ExcludesOpenTab()
    {
        var viewModel = CreateViewModel();

        Assert.Equal([WorkId], viewModel.OtherCategories().Select(category => category.Id));
    }
}
