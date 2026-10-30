using FlaUI.Core.AutomationElements;
using FlaUI.Core.Input;
using FlaUI.Core.WindowsAPI;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Category tabs (MEW-4 Faz 4): add, select, rename, delete, reorder, move a card to another category.
/// </summary>
public sealed class CategoryTests : IDisposable
{
    private const string GeneralId = "c1";
    private const string WorkId = "c2";
    private readonly AppDataFolder _data = new();

    public CategoryTests()
    {
        StateFiles.Save(_data, new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category(GeneralId, "General"), new Category(WorkId, "Work")],
            [
                StateFiles.Item("A1", GeneralId, new GridPlacement(0, 0, 1, 1)),
                StateFiles.Item("N1", WorkId, new GridPlacement(0, 0, 2, 1)),
                StateFiles.Item("N2", WorkId, new GridPlacement(1, 0, 2, 1)),
            ]));
    }

    public void Dispose() => _data.Dispose();

    /// <summary>A button of the delete dialog; searched inside the dialog because "CloseButton" also names the title bar button.</summary>
    private static Button DialogButton(AppSession app, string automationId)
    {
        var dialog = Wait.ForElement(() => app.FindInPopups("DeleteCategoryDialog"));
        return Wait.ForElement(() => dialog.FindFirstDescendant(condition => condition.ByAutomationId(automationId))).AsButton();
    }

    [Fact]
    public void PlusButton_CreatesNamedCategoryAndOpensIt()
    {
        using (var app = AppSession.Launch(_data))
        {
            app.Find("AddCategoryButton").AsButton().Invoke();
            var nameBox = Wait.ForElement(() => app.FindInPopups("CategoryNameBox")).AsTextBox();
            nameBox.Text = "Music";
            Keyboard.Press(VirtualKeyShort.ENTER);
            Assert.True(Wait.Until(() => app.TryFind("CategoryTabs")?.FindFirstDescendant(c => c.ByName("Music")) is not null));
            app.ClickCloseAndWaitForExit();
        }

        var state = StateFiles.ReadState(_data);
        Assert.Equal(["General", "Work", "Music"], state.Categories.Select(category => category.Name));
        Assert.Equal(state.Categories[2].Id, state.SelectedCategoryId);
    }

    [Fact]
    public void SelectingTab_ShowsOnlyItsCards()
    {
        using var app = AppSession.Launch(_data);
        Assert.NotNull(app.TryFind("Card_A1"));

        app.Find("Tab_" + WorkId).AsTabItem().Select();

        Assert.True(Wait.Until(() => app.TryFind("Card_N1") is not null && app.TryFind("Card_A1") is null));
    }

    [Fact]
    public void OpenTab_IsRestoredAfterRestart()
    {
        using (var app = AppSession.Launch(_data))
        {
            app.Find("Tab_" + WorkId).AsTabItem().Select();
            Assert.True(Wait.Until(() => app.TryFind("Card_N1") is not null));
            app.ClickCloseAndWaitForExit();
        }

        using var reopened = AppSession.Launch(_data);
        Assert.True(Wait.Until(() => reopened.TryFind("Card_N1") is not null));
        Assert.Null(reopened.TryFind("Card_A1"));
    }

    [Fact]
    public void RenameFromContextMenu_ChangesTabName()
    {
        using (var app = AppSession.Launch(_data))
        {
            RealMouse.RightClick(app.Find("Tab_" + WorkId).BoundingRectangle.Center());
            Wait.ForElement(() => app.FindInPopups("RenameCategoryMenuItem")).AsMenuItem().Invoke();
            var nameBox = Wait.ForElement(() => app.FindInPopups("CategoryNameBox")).AsTextBox();
            nameBox.Text = "Office";
            Keyboard.Press(VirtualKeyShort.ENTER);
            Assert.True(Wait.Until(() => app.Find("Tab_" + WorkId).Name == "Office"));
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal("Office", StateFiles.ReadState(_data).Categories.Single(category => category.Id == WorkId).Name);
    }

    [Fact]
    public void DeleteCategoryWithItems_AsksAndThenDeletesItAndItsItems()
    {
        using (var app = AppSession.Launch(_data))
        {
            RealMouse.RightClick(app.Find("Tab_" + WorkId).BoundingRectangle.Center());
            Wait.ForElement(() => app.FindInPopups("DeleteCategoryMenuItem")).AsMenuItem().Invoke();
            DialogButton(app, "PrimaryButton").Invoke();
            Assert.True(Wait.Until(() => app.TryFind("Tab_" + WorkId) is null));
            app.ClickCloseAndWaitForExit();
        }

        var state = StateFiles.ReadState(_data);
        Assert.Equal([GeneralId], state.Categories.Select(category => category.Id));
        Assert.Equal(["A1"], state.Items.Select(item => item.Id));
    }

    [Fact]
    public void DeleteCategory_Cancelled_KeepsEverything()
    {
        using (var app = AppSession.Launch(_data))
        {
            RealMouse.RightClick(app.Find("Tab_" + WorkId).BoundingRectangle.Center());
            Wait.ForElement(() => app.FindInPopups("DeleteCategoryMenuItem")).AsMenuItem().Invoke();
            DialogButton(app, "CloseButton").Invoke();
            Thread.Sleep(300);
            Assert.NotNull(app.TryFind("Tab_" + WorkId));
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal(3, StateFiles.ReadState(_data).Items.Count);
    }

    [Fact]
    public void MoveToFromCardMenu_MovesCardToOtherCategory()
    {
        using (var app = AppSession.Launch(_data))
        {
            RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
            var moveTo = Wait.ForElement(() => app.FindInPopups("MoveToMenuItem")).AsMenuItem();
            moveTo.Expand();
            Wait.ForElement(() => app.FindInPopups("MoveTo_" + WorkId)).AsMenuItem().Invoke();
            Assert.True(Wait.Until(() => app.TryFind("Card_A1") is null));
            app.ClickCloseAndWaitForExit();
        }

        var moved = StateFiles.ReadItem(_data, "A1")!;
        Assert.Equal(WorkId, moved.CategoryId);
        // Work holds two 2x1 notes in the first two rows, so the first free cell is R1C3.
        Assert.Equal(new GridPlacement(0, 2, 1, 1), moved.Placement);
    }

    [Fact]
    public void DraggingTab_ReordersCategories()
    {
        using (var app = AppSession.Launch(_data))
        {
            var first = app.Find("Tab_" + GeneralId).BoundingRectangle;
            var second = app.Find("Tab_" + WorkId).BoundingRectangle;
            var start = second.Center();
            var end = new System.Drawing.Point(first.Left + 4, first.Top + (first.Height / 2));

            GridDriver.Press(start);
            GridDriver.MoveSmoothly(start, end);
            GridDriver.WaitForUi();
            GridDriver.Release();
            Assert.True(Wait.Until(() => app.Find("Tab_" + WorkId).BoundingRectangle.Left < app.Find("Tab_" + GeneralId).BoundingRectangle.Left));
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal([WorkId, GeneralId], StateFiles.ReadState(_data).Categories.Select(category => category.Id));
    }
}
