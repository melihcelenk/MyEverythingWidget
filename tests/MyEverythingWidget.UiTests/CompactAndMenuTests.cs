using System.Drawing;
using FlaUI.Core.AutomationElements;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Compact icon behaviour, the grid's own right-click menu and the resize grip cursor (MEW-4 Faz 10: C1-C7).
/// </summary>
public sealed class CompactAndMenuTests : IDisposable
{
    private const string GeneralId = "c1";
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private void Seed(params WidgetItem[] items) =>
        StateFiles.Save(_data, new WidgetState(WidgetState.CurrentSchemaVersion, [new Category(GeneralId, "General")], items));

    private static AutomationElement EnterCompact(AppSession app)
    {
        GridDriver.WaitForUi();
        RealMouse.Click(app.Find("CompactButton").BoundingRectangle.Center());
        var icon = Wait.ForElement(() => app.TryFind("CompactIcon"));
        GridDriver.WaitForUi();
        return icon;
    }

    [Fact]
    public void CompactIcon_StaysOnTop_AndWidgetReturnsToItsPinSetting()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        Assert.False(Win32.IsTopmost(app.WindowHandle));

        var icon = EnterCompact(app);
        Assert.True(Wait.Until(() => Win32.IsTopmost(app.WindowHandle)), "The compact icon should always be on top.");

        RealMouse.Click(icon.BoundingRectangle.Center());
        Assert.True(Wait.Until(() => app.TryFind("WidgetGrid") is not null && !Win32.IsTopmost(app.WindowHandle)), "The unpinned widget should not stay on top.");
    }

    [Fact]
    public void CompactIcon_AppearsExactlyAtTheWidgetCorner()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        var widgetCorner = Win32.ClientOrigin(app.WindowHandle);

        EnterCompact(app);

        Assert.Equal(widgetCorner, Win32.ClientOrigin(app.WindowHandle));
    }

    [Fact]
    public void DraggingCompactIcon_FollowsTheMouseAndStopsOnRelease()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        var icon = EnterCompact(app);
        var before = Win32.ClientOrigin(app.WindowHandle);
        var start = icon.BoundingRectangle.Center();
        var end = new Point(start.X - 150, start.Y + 60);

        GridDriver.Press(start);
        GridDriver.MoveSmoothly(start, end);
        var whileHeld = Win32.ClientOrigin(app.WindowHandle);
        GridDriver.Release();
        GridDriver.MoveSmoothly(end, new Point(end.X - 100, end.Y + 80));
        GridDriver.WaitForUi();
        var afterRelease = Win32.ClientOrigin(app.WindowHandle);

        Assert.InRange(whileHeld.X - before.X, -155, -145);
        Assert.InRange(whileHeld.Y - before.Y, 55, 65);
        Assert.Equal(whileHeld, afterRelease);
        Assert.NotNull(app.TryFind("CompactIcon"));
    }

    [Fact]
    public void OpeningIconNearScreenEdge_KeepsWidgetOnThatMonitor()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        EnterCompact(app);
        var work = Win32.WorkAreaOf(app.WindowHandle);
        Win32.MoveTo(app.WindowHandle, work.Right - 90, work.Bottom - 90);
        GridDriver.WaitForUi();

        RealMouse.Click(app.Find("CompactIcon").BoundingRectangle.Center());

        Assert.True(Wait.Until(() => app.TryFind("WidgetGrid") is not null));
        GridDriver.WaitForUi();
        var client = Win32.ClientBounds(app.WindowHandle);
        Assert.True(work.Contains(client), $"The widget {client} should fit inside the work area {work}.");
        Assert.Equal((work.Right, work.Bottom), (client.Right, client.Bottom));
    }

    [Fact]
    public void RightClickOnEmptyGrid_OffersAddMenu()
    {
        Seed();
        using (var app = AppSession.Launch(_data))
        {
            GridDriver.WaitForUi();
            RealMouse.RightClick(app.Find("WidgetGrid").BoundingRectangle.Center());

            Assert.NotNull(Wait.ForElement(() => app.FindInPopups("GridAddAppMenuItem")));
            Assert.NotNull(app.FindInPopups("GridAddImageMenuItem"));
            Wait.ForElement(() => app.FindInPopups("GridAddNoteMenuItem")).AsMenuItem().Invoke();
            Wait.ForElement(() => app.FindInPopups("TextEditorBox")).AsTextBox().Text = "From the grid menu";
            var dialog = Wait.ForElement(() => app.FindInPopups("TextEditorDialog"));
            Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("PrimaryButton"))).AsButton().Invoke();
            Assert.True(Wait.Until(() => app.Find("WidgetGrid").FindAllChildren().Length >= 1));
            app.ClickCloseAndWaitForExit();
        }

        var note = Assert.IsType<NoteItem>(Assert.Single(StateFiles.ReadState(_data).Items));
        Assert.Equal("From the grid menu", note.Text);
    }

    [Fact]
    public void ResizeGrip_ShowsTheDiagonalResizeCursor()
    {
        Seed(new NoteItem("N1", GeneralId, new GridPlacement(0, 0, 2, 2), "note"));
        using var app = AppSession.Launch(_data);
        var card = app.Find("Card_N1");
        RealMouse.MoveTo(card.BoundingRectangle.Center());
        GridDriver.WaitForUi();

        var grip = Wait.ForElement(() => card.FindFirstDescendant(c => c.ByAutomationId("ResizeHandle")));
        GridDriver.MoveSmoothly(card.BoundingRectangle.Center(), grip.BoundingRectangle.Center());
        GridDriver.WaitForUi();

        Assert.True(Win32.CursorIsDiagonalResize(), "Over the resize grip the cursor should be the diagonal resize arrow.");
    }
}
