using System.Drawing;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Capturing;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>Settings (theme W1, always on top, about) and first-run import of the Python version (D1).</summary>
public sealed class SettingsAndMigrationTests : IDisposable
{
    private readonly AppDataFolder _data = new();
    private readonly string _legacyFile = Path.Combine(Path.GetTempPath(), $"mew-legacy-{Guid.NewGuid():N}.json");

    public void Dispose()
    {
        _data.Dispose();
        File.Delete(_legacyFile);
    }

    private static AutomationElement OpenSettings(AppSession app)
    {
        app.Find("SettingsButton").AsButton().Invoke();
        return Wait.ForElement(() => app.FindInPopups("SettingsDialog"));
    }

    private static AutomationElement In(AutomationElement parent, string automationId) =>
        Wait.ForElement(() => parent.FindFirstDescendant(condition => condition.ByAutomationId(automationId)));

    private static void CloseDialog(AppSession app, AutomationElement dialog)
    {
        In(dialog, "CloseButton").AsButton().Invoke();
        Wait.Until(() => app.FindInPopups("SettingsDialog") is null);
        GridDriver.WaitForUi();
    }

    /// <summary>Average brightness (0-255) of the empty grid surface.</summary>
    private static double SurfaceBrightness(AppSession app)
    {
        var grid = app.Find("WidgetGrid").BoundingRectangle;
        using var screen = Capture.Screen().Bitmap;
        var samples = new[] { new Point(grid.Left + 20, grid.Bottom - 20), new Point(grid.Right - 20, grid.Bottom - 20), grid.Center() };
        return samples.Select(point => screen.GetPixel(point.X, point.Y)).Average(color => (color.R + color.G + color.B) / 3.0);
    }

    [Fact]
    public void ThemeChoices_AreOneRowOfOneWordButtons()
    {
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using var app = AppSession.Launch(_data);
        var dialog = OpenSettings(app);

        var system = In(dialog, "ThemeSystem");
        var light = In(dialog, "ThemeLight");
        var dark = In(dialog, "ThemeDark");

        Assert.Equal(["System", "Light", "Dark"], new[] { system.Name, light.Name, dark.Name });
        Assert.Equal(system.BoundingRectangle.Top, light.BoundingRectangle.Top);
        Assert.Equal(system.BoundingRectangle.Top, dark.BoundingRectangle.Top);
        Assert.True(light.BoundingRectangle.Left - system.BoundingRectangle.Right <= 2, "The buttons should touch.");
        Assert.True(dark.BoundingRectangle.Left - light.BoundingRectangle.Right <= 2, "The buttons should touch.");
    }

    [Fact]
    public void AboutEmail_CopiesTheAddressAndSaysSo()
    {
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using var app = AppSession.Launch(_data);
        var dialog = OpenSettings(app);
        var email = In(dialog, "AboutEmailButton");

        // The About section is at the bottom of the dialog; the user scrolls down to it with the mouse wheel.
        RealMouse.MoveTo(In(dialog, "AppNameText").BoundingRectangle.Center());
        FlaUI.Core.Input.Mouse.Scroll(-10);
        Assert.True(Wait.Until(() => email.BoundingRectangle.Height > 0), "Scrolling should bring the e-mail button into view.");
        GridDriver.WaitForUi();
        RealMouse.Click(email.BoundingRectangle.Center());

        // "Copied" shows for 1.5 s; reading the clipboard starts a process and takes about as long, so it comes second.
        Assert.True(Wait.Until(() => email.Name == "Copied"), $"The e-mail button should say Copied, it says '{email.Name}'.");
        Assert.True(Wait.Until(() => SandboxClipboard.GetText() == "info@melihcelenk.com"), "The e-mail address should be on the clipboard.");
        Assert.True(Wait.Until(() => email.Name == "info@melihcelenk.com", TimeSpan.FromSeconds(5)), "The e-mail button should show the address again.");
    }

    [Fact]
    public void AboutCard_IsTaskTimerWidgetsGreenCard_AsWideAsTheContent()
    {
        // PHASE17 17.12 (S17): the About card of TaskTimerWidget, in a narrower Settings dialog.
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using var app = AppSession.Launch(_data);
        var dialog = OpenSettings(app);
        GridDriver.WaitForUi();

        var card = In(dialog, "AboutCard").BoundingRectangle;
        var theme = In(dialog, "ThemeChoices").BoundingRectangle;
        var close = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByName("Close").And(c.ByControlType(FlaUI.Core.Definitions.ControlType.Button)))).BoundingRectangle;
        var scale = app.Find("WidgetGrid").BoundingRectangle.Width / 5.0 / 80;

        Assert.True(Math.Abs(card.Left - theme.Left) <= 2, $"The card {card} should start where the content starts {theme}.");
        Assert.True(Math.Abs(card.Right - close.Right) <= 2, $"The card {card} should reach the right edge of the content {close}.");
        Assert.True(close.Right - theme.Left <= 256 * scale, $"The content should be about 252 px wide, it is {close.Right - theme.Left}.");

        using var screen = Capture.Screen().Bitmap;
        var inside = screen.GetPixel(card.Left + 6, card.Top + 6);
        Assert.True(Math.Abs(inside.R - 0xC8) <= 8 && Math.Abs(inside.G - 0xE6) <= 8 && Math.Abs(inside.B - 0xC0) <= 8,
            $"The card should be TaskTimerWidget's green #C8E6C0, it is {inside}.");
    }

    [Theory]
    [InlineData("AboutEmailButton", "Copy info@melihcelenk.com")]
    [InlineData("AboutPersonalLink", "https://melihcelenk.com/")]
    [InlineData("AboutWebsiteLink", "https://melihcelenk.github.io/MyEverythingWidget/")]
    [InlineData("AboutRateLink", "https://apps.microsoft.com/search/publisher?name=Melih%20Celenk")]
    public void AboutLinks_TellWhereTheyGo(string automationId, string target)
    {
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using var app = AppSession.Launch(_data);
        var dialog = OpenSettings(app);

        Assert.Equal(target, In(dialog, automationId).HelpText);
    }

    [Fact]
    public void Theme_DarkAndLight_RepaintWithoutRestartAndArePersisted()
    {
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using (var app = AppSession.Launch(_data))
        {
            var dialog = OpenSettings(app);
            In(dialog, "ThemeDark").AsRadioButton().IsChecked = true;
            CloseDialog(app, dialog);
            Capture.Element(app.MainWindow).ToFile(Artifacts.PathOf("theme-dark"));
            var dark = SurfaceBrightness(app);

            dialog = OpenSettings(app);
            In(dialog, "ThemeLight").AsRadioButton().IsChecked = true;
            CloseDialog(app, dialog);
            Capture.Element(app.MainWindow).ToFile(Artifacts.PathOf("theme-light"));
            var light = SurfaceBrightness(app);

            Assert.True(dark < 80, $"Dark theme surface brightness was {dark:F0}.");
            Assert.True(light > 170, $"Light theme surface brightness was {light:F0}.");
            app.ClickCloseAndWaitForExit();
        }

        using var reopened = AppSession.Launch(_data);
        GridDriver.WaitForUi();
        Assert.True(SurfaceBrightness(reopened) > 170, "The light theme should be restored after restart.");
        var settingsDialog = OpenSettings(reopened);
        Assert.True(In(settingsDialog, "ThemeLight").AsRadioButton().IsChecked);
    }

    [Theory]
    [InlineData("ThemeDark")]
    [InlineData("ThemeLight")]
    public void SelectedTab_MatchesGridSurface_AfterThemeChange(string theme)
    {
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using var app = AppSession.Launch(_data);
        var dialog = OpenSettings(app);
        In(dialog, theme == "ThemeDark" ? "ThemeLight" : "ThemeDark").AsRadioButton().IsChecked = true;
        In(dialog, theme).AsRadioButton().IsChecked = true;
        CloseDialog(app, dialog);

        var tab = app.Find("Tab_" + StateFiles.CategoryId).BoundingRectangle;
        using var screen = Capture.Screen().Bitmap;
        var tabColor = screen.GetPixel(tab.Left + 4, tab.Top + (tab.Height / 2));
        var tabBrightness = (tabColor.R + tabColor.G + tabColor.B) / 3.0;
        var surface = SurfaceBrightness(app);

        Assert.True(Math.Abs(tabBrightness - surface) < 25, $"Open tab brightness {tabBrightness:F0} should match the surface {surface:F0}.");
    }

    [Fact]
    public void AlwaysOnTopSwitch_PinsTheWindow()
    {
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using var app = AppSession.Launch(_data);
        var dialog = OpenSettings(app);

        In(dialog, "AlwaysOnTopSwitch").AsToggleButton().Toggle();

        Assert.True(Wait.Until(() => Win32.IsTopmost(app.WindowHandle)));
    }

    [Fact]
    public void About_ShowsVersion()
    {
        StateFiles.Seed(_data, new Dictionary<string, Core.Grid.GridPlacement>());
        using var app = AppSession.Launch(_data);

        var version = In(OpenSettings(app), "VersionText").Name;

        // Name and version are on separate lines, as in TaskTimerWidget's About (PHASE17 17.10).
        Assert.Matches(@"^Version \d+\.\d+\.\d+$", version);
    }

    [Fact]
    public void PreviousVersionData_IsImportedOnFirstStartOnly()
    {
        File.WriteAllText(_legacyFile, """
            { "categories": [{ "id": "x", "name": "Work", "icon": "W" }],
              "apps": [{ "id": "a", "name": "Command Prompt", "icon_path": "C", "target": "C:\\Windows\\System32\\cmd.exe",
                         "category": "Work", "type": "exe", "grid_row": 0, "grid_col": 0, "col_span": 1, "row_span": 1 }],
              "notes": [{ "id": "n", "content": "From Python", "type": "text", "category": "Work",
                          "created_at": "2025-11-20T10:00:00+00:00", "updated_at": "2025-11-20T10:00:00+00:00",
                          "grid_row": 1, "grid_col": 0, "col_span": 2, "row_span": 1 }] }
            """);
        var environment = new Dictionary<string, string> { ["MEW_LEGACY_STATE"] = _legacyFile };

        using (var app = AppSession.Launch(_data, environment))
        {
            var statusBar = app.Find("StatusInfoBar");
            Assert.True(Wait.Until(() => statusBar.FindAllDescendants().Any(element =>
                (element.Properties.Name.ValueOrDefault ?? "").Contains("Imported 2 items", StringComparison.Ordinal))));
            app.ClickCloseAndWaitForExit();
        }

        var first = StateFiles.ReadState(_data);
        Assert.Equal("Work", Assert.Single(first.Categories).Name);
        Assert.Equal(2, first.Items.Count);
        Assert.NotNull(first.Items.OfType<AppItem>().Single().IconPath);

        using (var app = AppSession.Launch(_data, environment))
        {
            GridDriver.WaitForUi();
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal(2, StateFiles.ReadState(_data).Items.Count);
    }
}
