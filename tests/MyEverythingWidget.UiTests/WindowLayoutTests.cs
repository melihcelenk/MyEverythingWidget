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
    private const string ResetIconText = "Reset to original";
    private const string CancelText = "Cancel";

    private void SeedCmd() =>
        Seed(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Cmd", Path.Combine(Environment.SystemDirectory, "cmd.exe"), LaunchKind.Executable, null));

    private static AutomationElement OpenIconDialog(AppSession app)
    {
        GridDriver.WaitForUi();
        RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
        Wait.ForElement(() => app.FindInPopups("ChangeIconMenuItem")).AsMenuItem().Invoke();
        var dialog = Wait.ForElement(() => app.FindInPopups("IconPickerDialog"));
        GridDriver.WaitForUi();
        return dialog;
    }

    private static AutomationElement In(AutomationElement parent, Func<FlaUI.Core.Conditions.ConditionFactory, FlaUI.Core.Conditions.ConditionBase> condition) =>
        Wait.ForElement(() => parent.FindFirstDescendant(condition));

    private static void PressCtrlV()
    {
        FlaUI.Core.Input.Keyboard.TypeSimultaneously(FlaUI.Core.WindowsAPI.VirtualKeyShort.CONTROL, FlaUI.Core.WindowsAPI.VirtualKeyShort.KEY_V);
    }
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
    public void EmojiPickedInIconDialog_ReplacesCardIcon()
    {
        Seed(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Cmd", Path.Combine(Environment.SystemDirectory, "cmd.exe"), LaunchKind.Executable, null));
        using (var app = AppSession.Launch(_data))
        {
            GridDriver.WaitForUi();
            RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
            var menuItem = Wait.ForElement(() => app.FindInPopups("ChangeIconMenuItem"));
            Assert.Null(app.FindInPopups("SetEmojiMenuItem"));
            Assert.Null(app.FindInPopups("ResetIconMenuItem"));
            menuItem.AsMenuItem().Invoke();

            var dialog = Wait.ForElement(() => app.FindInPopups("IconPickerDialog"));
            Assert.NotNull(dialog.FindFirstDescendant(c => c.ByAutomationId("SelectIconTab")));
            Assert.NotNull(dialog.FindFirstDescendant(c => c.ByAutomationId("SelectImageTab")));
            RealMouse.Click(Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("Emoji_🚀"))).BoundingRectangle.Center());

            Assert.True(Wait.Until(() => app.FindInPopups("IconPickerDialog") is null), "Picking an emoji should close the dialog.");
            Assert.True(Wait.Until(() => app.Find("Card_A1").FindFirstDescendant(c => c.ByAutomationId("AppEmoji"))?.Name == "🚀"));
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal("🚀", Assert.IsType<AppItem>(StateFiles.ReadItem(_data, "A1")).Emoji);
    }

    [Fact]
    public void IconDialog_InSmallestWindow_KeepsTabsResetAndCancelVisible()
    {
        SeedCmd();
        using (var app = AppSession.Launch(_data))
        {
            var pitch = Pitch(app);
            DragCorner(app, -(int)(5 * pitch), -(int)(5 * pitch));
            Assert.True(Wait.Until(() => GridIs(app, pitch, rows: 2, columns: 2)));

            var dialog = OpenIconDialog(app);
            var window = app.MainWindow.BoundingRectangle;
            var parts = new[]
            {
                In(dialog, c => c.ByAutomationId("SelectIconTab")),
                In(dialog, c => c.ByAutomationId("SelectImageTab")),
                In(dialog, c => c.ByName(ResetIconText)),
                In(dialog, c => c.ByName(CancelText)),
            };
            foreach (var part in parts)
            {
                Assert.False(part.IsOffscreen, $"'{part.Name}' should be on screen.");
                Assert.True(window.Contains(part.BoundingRectangle.Center()), $"'{part.Name}' {part.BoundingRectangle} should be inside the window {window}.");
            }

            Assert.True(parts[2].BoundingRectangle.Right <= parts[3].BoundingRectangle.Left, "Reset to original should be left of Cancel.");

            RealMouse.Click(parts[2].BoundingRectangle.Center());
            Assert.True(Wait.Until(() => StateFiles.ReadItem(_data, "A1") is AppItem { IconPath: not null }), "Clicking Reset should give the card its program icon.");
            app.ClickCloseAndWaitForExit();
        }
    }

    [Fact]
    public void SelectImageTab_OffersBrowseAndDropArea()
    {
        SeedCmd();
        using var app = AppSession.Launch(_data);
        var dialog = OpenIconDialog(app);

        RealMouse.Click(In(dialog, c => c.ByAutomationId("SelectImageTab")).BoundingRectangle.Center());

        Assert.False(In(dialog, c => c.ByAutomationId("BrowseImageButton")).IsOffscreen);
        Assert.False(In(dialog, c => c.ByAutomationId("ImageDropArea")).IsOffscreen);
        Assert.True(Wait.Until(() => dialog.FindFirstDescendant(c => c.ByAutomationId("Emoji_🚀")) is not { IsOffscreen: false }), "The emoji grid belongs to the other tab.");

        RealMouse.Click(In(dialog, c => c.ByAutomationId("SelectIconTab")).BoundingRectangle.Center());
        Assert.False(In(dialog, c => c.ByAutomationId("Emoji_🚀")).IsOffscreen);
    }

    [Fact]
    public void PastedPicture_InSelectImageTab_BecomesTheIcon()
    {
        SeedCmd();
        using (var app = AppSession.Launch(_data))
        {
            var dialog = OpenIconDialog(app);
            RealMouse.Click(In(dialog, c => c.ByAutomationId("SelectImageTab")).BoundingRectangle.Center());
            GridDriver.WaitForUi();
            SandboxClipboard.SetPicture(64, 64);

            PressCtrlV();

            Assert.True(Wait.Until(() => app.FindInPopups("IconPickerDialog") is null), "Pasting a picture should apply it and close the dialog.");
            Assert.True(Wait.Until(() => StateFiles.ReadItem(_data, "A1") is AppItem { IconPath: not null, Emoji: null }));
            Assert.Single(StateFiles.ReadState(_data).Items);
            app.ClickCloseAndWaitForExit();
        }
    }

    [Fact]
    public void PastedImageFile_InSelectImageTab_BecomesTheIcon()
    {
        SeedCmd();
        var imageFile = Path.Combine(_data.Path, "icon-source.png");
        Directory.CreateDirectory(_data.Path);
        using (var bitmap = new Bitmap(48, 48))
        {
            bitmap.Save(imageFile, System.Drawing.Imaging.ImageFormat.Png);
        }

        using (var app = AppSession.Launch(_data))
        {
            var dialog = OpenIconDialog(app);
            RealMouse.Click(In(dialog, c => c.ByAutomationId("SelectImageTab")).BoundingRectangle.Center());
            GridDriver.WaitForUi();
            SandboxClipboard.SetFile(imageFile);

            PressCtrlV();

            Assert.True(Wait.Until(() => app.FindInPopups("IconPickerDialog") is null), "Pasting an image file should apply it and close the dialog.");
            Assert.True(Wait.Until(() => StateFiles.ReadItem(_data, "A1") is AppItem { IconPath: not null }));
            app.ClickCloseAndWaitForExit();
        }
    }

    [Theory]
    [InlineData(5)]
    [InlineData(2)]
    public void SettingsDialog_KeepsAGapToTheWindowEdges(int columns)
    {
        Seed();
        using var app = AppSession.Launch(_data);
        var pitch = Pitch(app);
        if (columns < 5)
        {
            DragCorner(app, -(int)((5 - columns) * pitch), 0);
            Assert.True(Wait.Until(() => GridIs(app, pitch, rows: 5, columns: columns)));
        }

        RealMouse.Click(app.Find("SettingsButton").BoundingRectangle.Center());
        var dialog = Wait.ForElement(() => app.FindInPopups("SettingsDialog"));
        GridDriver.WaitForUi();
        var window = Win32.ClientBounds(app.WindowHandle);
        var scale = pitch / 80;

        // A 12 px gap to the window plus the dialog's padding: 24 px normally, 12 px when the dialog is narrower than
        // its usual 320 px.
        var narrow = window.Width / scale - 24 < 320;
        var inset = (int)Math.Floor((narrow ? 22 : 34) * scale);
        var theme = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("ThemeSystem"))).BoundingRectangle;
        var close = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByName("Close").And(c.ByControlType(FlaUI.Core.Definitions.ControlType.Button)))).BoundingRectangle;
        Assert.True(theme.Left - window.Left >= inset, $"The dialog content {theme} should start at least {inset} px inside the window {window}.");
        Assert.True(window.Right - close.Right >= inset, $"The dialog buttons {close} should end at least {inset} px inside the window {window}.");

        var about = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("AboutCard"))).BoundingRectangle;
        Assert.True(about.Right <= close.Right + 1, $"The about text {about} should wrap inside the dialog (buttons end at {close.Right}).");
        FlaUI.Core.Capturing.Capture.Rectangle(window).ToFile(Artifacts.PathOf($"settings-{columns}-columns"));
    }

    [Fact]
    public void SettingsDialog_KeepsAGapAboveAndBelow_AndShowsItAll()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        var scale = Pitch(app) / 80;

        RealMouse.Click(app.Find("SettingsButton").BoundingRectangle.Center());
        var dialog = Wait.ForElement(() => app.FindInPopups("SettingsDialog"));
        GridDriver.WaitForUi();
        var window = Win32.ClientBounds(app.WindowHandle);
        var close = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByName("Close").And(c.ByControlType(FlaUI.Core.Definitions.ControlType.Button)))).BoundingRectangle;
        var title = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByName("Settings").And(c.ByControlType(FlaUI.Core.Definitions.ControlType.Text)))).BoundingRectangle;

        // A 12 px gap to the window plus the dialog's 24 px padding.
        var inset = (int)Math.Floor(34 * scale);
        Assert.True(title.Top - window.Top >= inset, $"The dialog title {title} should start at least {inset} px below the window top {window}.");
        Assert.True(window.Bottom - close.Bottom >= inset, $"The dialog buttons {close} should end at least {inset} px above the window bottom {window}.");

        // At the default size everything fits without scrolling: the whole About card is above the buttons.
        var card = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("AboutCard"))).BoundingRectangle;
        var scroller = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("SettingsScroller")));
        Assert.False(scroller.Patterns.Scroll.Pattern.VerticallyScrollable.Value,
            "At the default size the settings should fit without scrolling.");
        Assert.True(card.Height > 0 && card.Bottom <= close.Top, $"The About card {card} should be above the buttons {close}.");
        FlaUI.Core.Capturing.Capture.Rectangle(window).ToFile(Artifacts.PathOf("settings-default-size"));
    }

    [Theory]
    [InlineData(4)]
    [InlineData(3)]
    public void SettingsDialog_ContentLinesUpWithItsTitle_InANarrowerWidget(int columns)
    {
        Seed();
        using var app = AppSession.Launch(_data);
        var pitch = Pitch(app);
        DragCorner(app, -(int)((5 - columns) * pitch), 0);
        Assert.True(Wait.Until(() => GridIs(app, pitch, rows: 5, columns: columns)));

        RealMouse.Click(app.Find("SettingsButton").BoundingRectangle.Center());
        var dialog = Wait.ForElement(() => app.FindInPopups("SettingsDialog"));
        GridDriver.WaitForUi();
        var title = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByName("Settings").And(c.ByControlType(FlaUI.Core.Definitions.ControlType.Text)))).BoundingRectangle;
        var theme = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("ThemeChoices"))).BoundingRectangle;
        FlaUI.Core.Capturing.Capture.Rectangle(Win32.ClientBounds(app.WindowHandle)).ToFile(Artifacts.PathOf($"settings-{columns}-columns-aligned"));

        // The content starts where the title starts; shifted content is cut off on the right.
        Assert.True(Math.Abs(theme.Left - title.Left) <= 4, $"The content {theme} should start below the title {title}.");
    }
}
