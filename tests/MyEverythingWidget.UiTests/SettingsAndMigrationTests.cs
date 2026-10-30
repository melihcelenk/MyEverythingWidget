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

        Assert.Matches(@"^My Everything Widget \d+\.\d+\.\d+$", version);
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
