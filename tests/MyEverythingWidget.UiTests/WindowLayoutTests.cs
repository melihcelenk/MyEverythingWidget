using System.Drawing;
using FlaUI.Core.AutomationElements;
using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// One-row title bar, resizing the window by whole cells, the one-cell compact mode, whole images and emoji icons
/// (MEW-4 Faz 9: W1-W5).
/// </summary>
public sealed class WindowLayoutTests : IDisposable
{
    private const string GeneralId = "c1";
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private void Seed(params WidgetItem[] items) =>
        StateFiles.Save(_data, new WidgetState(WidgetState.CurrentSchemaVersion, [new Category(GeneralId, "General")], items));

    private AppSettings SavedSettings() =>
        new JsonSettingsStore(_data.Path, TimeProvider.System, NullLogger<JsonSettingsStore>.Instance).Load();

    private static Rectangle GridBounds(AppSession app) => app.Find("WidgetGrid").BoundingRectangle;

    /// <summary>Size of one cell in screen pixels, from the default 5x5 grid.</summary>
    private static double Pitch(AppSession app) => GridBounds(app).Width / 5.0;

    /// <summary>Drags the bottom-right resize corner of the window by (<paramref name="dx"/>, <paramref name="dy"/>).</summary>
    private static void DragCorner(AppSession app, int dx, int dy)
    {
        var bounds = Win32.GetBounds(app.WindowHandle);
        var corner = new Point(bounds.Right - 3, bounds.Bottom - 3);
        GridDriver.Press(corner);
        GridDriver.MoveSmoothly(corner, new Point(corner.X + dx, corner.Y + dy));
        GridDriver.Release();
    }

    private static bool GridIs(AppSession app, double pitch, int rows, int columns)
    {
        var grid = GridBounds(app);
        return Math.Abs(grid.Width - (columns * pitch)) <= 2 && Math.Abs(grid.Height - (rows * pitch)) <= 2;
    }

    [Fact]
    public void TitleBar_IsOneRowWithTabsAndButtons()
    {
        Seed();
        using var app = AppSession.Launch(_data);

        var tab = app.Find("Tab_" + GeneralId).BoundingRectangle;
        var close = app.Find("CloseButton").BoundingRectangle;
        var client = app.MainWindow.BoundingRectangle;
        var pitch = Pitch(app);

        Assert.InRange(Math.Abs(tab.Center().Y - close.Center().Y), 0, pitch / 8);
        Assert.InRange(GridBounds(app).Top - client.Top, 0, pitch * 0.75);
    }

    [Fact]
    public void DraggingWindowCorner_ResizesGridByWholeCellsDownTo2x2AndIsRemembered()
    {
        Seed();
        using (var app = AppSession.Launch(_data))
        {
            var pitch = Pitch(app);

            DragCorner(app, -(int)(2.2 * pitch), -(int)(1.9 * pitch));
            Assert.True(Wait.Until(() => GridIs(app, pitch, rows: 3, columns: 3)), $"Expected a 3x3 grid, got {GridBounds(app)}.");

            DragCorner(app, -(int)(5 * pitch), -(int)(5 * pitch));
            Assert.True(Wait.Until(() => GridIs(app, pitch, rows: 2, columns: 2)), $"Expected the 2x2 minimum, got {GridBounds(app)}.");

            DragCorner(app, (int)(3.1 * pitch), (int)(1.1 * pitch));
            Assert.True(Wait.Until(() => GridIs(app, pitch, rows: 3, columns: 5)), $"Expected a 3x5 grid, got {GridBounds(app)}.");
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal(new GridSize(Rows: 3, Columns: 5), SavedSettings().GridSize);
        using var second = AppSession.Launch(_data);
        var secondPitch = GridBounds(second).Height / 3.0;
        Assert.True(GridIs(second, secondPitch, rows: 3, columns: 5), $"The grid should reopen as 3x5, got {GridBounds(second)}.");
    }

    [Fact]
    public void ShrinkingWindow_StopsAtTheItems()
    {
        Seed(new NoteItem("N1", GeneralId, new GridPlacement(3, 2, 2, 1), "far"));
        using var app = AppSession.Launch(_data);
        var pitch = Pitch(app);

        DragCorner(app, -(int)(5 * pitch), -(int)(5 * pitch));

        Assert.True(Wait.Until(() => GridIs(app, pitch, rows: 4, columns: 4)), $"Expected a 4x4 grid, got {GridBounds(app)}.");
        Assert.NotNull(app.TryFind("Card_N1"));
    }

    [Fact]
    public void CompactMode_ShrinksToOneCellIconAndClickingItOpensTheWidget()
    {
        Seed();
        using (var app = AppSession.Launch(_data))
        {
            var pitch = Pitch(app);
            var expanded = Win32.GetBounds(app.WindowHandle);

            RealMouse.Click(app.Find("CompactButton").BoundingRectangle.Center());

            var icon = Wait.ForElement(() => app.TryFind("CompactIcon"));
            Assert.True(Wait.Until(() => app.MainWindow.BoundingRectangle.Width <= pitch * 1.3), $"The compact window should be about one cell wide; window {app.MainWindow.BoundingRectangle}, Win32 {Win32.GetBounds(app.WindowHandle).Right - Win32.GetBounds(app.WindowHandle).Left}, icon {icon.BoundingRectangle}, cell {pitch}.");
            Assert.True(app.MainWindow.BoundingRectangle.Height <= pitch * 1.3, "The compact window should be about one cell high.");
            Assert.True(SavedSettings().IsCompact);

            RealMouse.Click(icon.BoundingRectangle.Center());

            Assert.True(Wait.Until(() => app.TryFind("CompactIcon") is null && app.TryFind("WidgetGrid") is not null), "Clicking the icon should open the widget.");
            var reopened = Win32.GetBounds(app.WindowHandle);
            Assert.Equal((expanded.Right - expanded.Left, expanded.Bottom - expanded.Top), (reopened.Right - reopened.Left, reopened.Bottom - reopened.Top));

            RealMouse.Click(app.Find("CompactButton").BoundingRectangle.Center());
            Wait.ForElement(() => app.TryFind("CompactIcon"));
            app.MainWindow.Close();
            Assert.True(app.WaitForExit(), "The app should exit when its compact window is closed.");
        }

        using var second = AppSession.Launch(_data);
        Assert.NotNull(Wait.ForElement(() => second.TryFind("CompactIcon")));
    }

    [Fact]
    public void WideImage_IsShownWhole()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        SandboxClipboard.SetPicture(1600, 400);

        app.MainWindow.Focus();
        Thread.Sleep(200);
        FlaUI.Core.Input.Keyboard.TypeSimultaneously(FlaUI.Core.WindowsAPI.VirtualKeyShort.CONTROL, FlaUI.Core.WindowsAPI.VirtualKeyShort.KEY_V);

        var image = Wait.ForElement(() => app.TryFind("ImageContent"));
        Assert.True(Wait.Until(() => image.BoundingRectangle.Height > 0));
        var bounds = image.BoundingRectangle;
        Assert.InRange(bounds.Width / (double)bounds.Height, 3.7, 4.3);
    }

    [Fact]
    public void EmojiFromMenu_ReplacesCardIcon()
    {
        Seed(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Cmd", Path.Combine(Environment.SystemDirectory, "cmd.exe"), LaunchKind.Executable, null));
        using (var app = AppSession.Launch(_data))
        {
            RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
            Wait.ForElement(() => app.FindInPopups("SetEmojiMenuItem")).AsMenuItem().Invoke();
            Wait.ForElement(() => app.FindInPopups("TextEditorBox")).AsTextBox().Text = "🚀";
            var dialog = Wait.ForElement(() => app.FindInPopups("TextEditorDialog"));
            Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("PrimaryButton"))).AsButton().Invoke();

            Assert.True(Wait.Until(() => app.Find("Card_A1").FindFirstDescendant(c => c.ByAutomationId("AppEmoji"))?.Name == "🚀"));
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal("🚀", Assert.IsType<AppItem>(StateFiles.ReadItem(_data, "A1")).Emoji);
    }
}
