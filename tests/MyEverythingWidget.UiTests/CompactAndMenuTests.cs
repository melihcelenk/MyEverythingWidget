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
    public void CompactIcon_AppearsAtTheWidgetCornerNearestTheScreenCorner()
    {
        // The widget opens at the top right of the screen, so the icon takes the widget's top-right corner
        // (PHASE17 17.7, S11 → B).
        Seed();
        using var app = AppSession.Launch(_data);
        var widget = Win32.ClientBounds(app.WindowHandle);

        EnterCompact(app);
        var icon = Win32.ClientBounds(app.WindowHandle);

        Assert.Equal(widget.Right, icon.Right);
        Assert.Equal(widget.Top, icon.Top);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void IconOnTheRight_OpensWithTheRightEdgesLinedUp_AndShrinksBackToTheSamePlace(bool bottom)
    {
        Seed();
        using var app = AppSession.Launch(_data);
        EnterCompact(app);
        var work = Win32.WorkAreaOf(app.WindowHandle);
        var size = Win32.GetBounds(app.WindowHandle);
        var iconWidth = size.Right - size.Left;
        var iconHeight = size.Bottom - size.Top;
        Win32.MoveTo(app.WindowHandle, work.Right - iconWidth - 40, bottom ? work.Bottom - iconHeight - 40 : work.Top + 40);
        GridDriver.WaitForUi();
        var icon = Win32.ClientBounds(app.WindowHandle);

        RealMouse.Click(app.Find("CompactIcon").BoundingRectangle.Center());
        Assert.True(Wait.Until(() => app.TryFind("WidgetGrid") is not null));
        GridDriver.WaitForUi();
        var widget = Win32.ClientBounds(app.WindowHandle);

        Assert.Equal(icon.Right, widget.Right);
        Assert.Equal(bottom ? icon.Bottom : icon.Top, bottom ? widget.Bottom : widget.Top);

        EnterCompact(app);
        Assert.Equal(icon, Win32.ClientBounds(app.WindowHandle));
    }

    [Fact]
    public void CompactIcon_KeepsItsSize_AfterMinimizeAndRestoreFromTheTaskbar()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        EnterCompact(app);
        var before = Win32.ClientBounds(app.WindowHandle);

        // What a taskbar click sends: minimize, then restore.
        PostMessageW(app.WindowHandle, SystemCommand, MinimizeCommand, 0);
        Assert.True(Wait.Until(() => IsIconic(app.WindowHandle)), "The icon should minimize.");
        PostMessageW(app.WindowHandle, SystemCommand, RestoreCommand, 0);
        Assert.True(Wait.Until(() => !IsIconic(app.WindowHandle)), "The icon should come back.");
        GridDriver.WaitForUi();

        Assert.Equal(before, Win32.ClientBounds(app.WindowHandle));
    }

    private const uint SystemCommand = 0x0112;
    private const nint MinimizeCommand = 0xF020;
    private const nint RestoreCommand = 0xF120;

    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern bool PostMessageW(nint window, uint message, nint wParam, nint lParam);

    [System.Runtime.InteropServices.DllImport("user32.dll")]
    private static extern bool IsIconic(nint window);

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
        var icon = Win32.ClientBounds(app.WindowHandle);

        RealMouse.Click(app.Find("CompactIcon").BoundingRectangle.Center());

        Assert.True(Wait.Until(() => app.TryFind("WidgetGrid") is not null));
        GridDriver.WaitForUi();
        var client = Win32.ClientBounds(app.WindowHandle);
        Assert.True(work.Contains(client), $"The widget {client} should fit inside the work area {work}.");

        // The icon is in the bottom-right corner, so the widget opens from the icon's bottom-right corner
        // (PHASE17 17.7, S11 → B); before that decision it was pushed against the work-area corner.
        Assert.Equal((icon.Right, icon.Bottom), (client.Right, client.Bottom));
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
