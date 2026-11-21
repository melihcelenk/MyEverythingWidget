using System.Drawing;
using FlaUI.Core.AutomationElements;
using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// MEW-4 Faz 18: language choice, the compact Settings window, the compact icon's frame and the title bar buttons.
/// </summary>
public sealed class LanguageAndSettingsTests : IDisposable
{
    private const double CellSize = 80;

    private static readonly string[] ThemeChoices = ["ThemeSystem", "ThemeLight", "ThemeDark"];

    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private JsonSettingsStore SettingsStore() => new(_data.Path, TimeProvider.System, NullLogger<JsonSettingsStore>.Instance);

    private AppSession Launch(string? language = null)
    {
        StateFiles.Seed(_data, new Dictionary<string, GridPlacement>());
        if (language is not null)
        {
            SettingsStore().Save(AppSettings.Default with { Language = language });
        }

        return AppSession.Launch(_data);
    }

    private static double Scale(AppSession app) => app.Find("WidgetGrid").BoundingRectangle.Width / 5.0 / CellSize;

    private static AutomationElement OpenSettings(AppSession app)
    {
        RealMouse.Click(app.Find("SettingsButton").BoundingRectangle.Center());
        var dialog = Wait.ForElement(() => app.FindInPopups("SettingsDialog"));
        GridDriver.WaitForUi();
        return dialog;
    }

    private static AutomationElement In(AutomationElement parent, string automationId) =>
        Wait.ForElement(() => parent.FindFirstDescendant(condition => condition.ByAutomationId(automationId)));

    [Fact]
    public void Settings_HasACrossAtTheTopRight_AndNoCloseButtonAtTheBottom()
    {
        using var app = Launch();
        var dialog = OpenSettings(app);
        var scale = Scale(app);

        // The dialog's UI Automation element covers the whole window; its visible edges are found on screen.
        var cross = In(dialog, "SettingsCloseButton").BoundingRectangle;
        var top = DialogBox.TopEdgeAbove(new Point(cross.Left - 3, cross.Top + 2));
        var right = DialogBox.RightEdgeOf(new Point(cross.Left + 2, cross.Bottom + 2));
        Assert.InRange(right - cross.Right, 0, 16 * scale);
        Assert.InRange(cross.Top - top, 0, 16 * scale);
        Assert.Null(dialog.FindFirstDescendant(condition => condition.ByAutomationId("CloseButton")));

        In(dialog, "SettingsCloseButton").AsButton().Invoke();
        Assert.True(Wait.Until(() => app.FindInPopups("SettingsDialog") is null), "The cross should close Settings.");
    }

    [Fact]
    public void Settings_TitleTakesLittleRoom()
    {
        using var app = Launch();
        var dialog = OpenSettings(app);
        var scale = Scale(app);

        var firstSetting = In(dialog, "LanguageChoice").BoundingRectangle;
        var cross = In(dialog, "SettingsCloseButton").BoundingRectangle;
        var top = DialogBox.TopEdgeAbove(new Point(cross.Left - 3, cross.Top + 2));

        Assert.InRange(firstSetting.Top - top, 0, 64 * scale);
    }

    [Fact]
    public void Settings_ClosesWhenClickingTheAppOutsideIt()
    {
        using var app = Launch();
        var dialog = OpenSettings(app);
        var window = app.MainWindow.BoundingRectangle;
        var cross = In(dialog, "SettingsCloseButton").BoundingRectangle;
        var top = DialogBox.TopEdgeAbove(new Point(cross.Left - 3, cross.Top + 2));

        // Above the dialog when there is room there, otherwise in the gap at the window's left edge.
        var outside = top - window.Top > 24
            ? new Point(window.Left + (window.Width / 2), window.Top + ((top - window.Top) / 2))
            : new Point(window.Left + 4, window.Top + (window.Height / 2));
        RealMouse.Click(outside);

        Assert.True(Wait.Until(() => app.FindInPopups("SettingsDialog") is null), "A click outside Settings should close it.");
    }

    /// <summary>Opens the language list (a popup of its own) and returns it.</summary>
    private static AutomationElement OpenLanguageList(AppSession app, AutomationElement dialog)
    {
        RealMouse.Click(In(dialog, "LanguageChoice").BoundingRectangle.Center());
        var list = Wait.ForElement(() => app.FindInPopups("LanguageList"));
        GridDriver.WaitForUi();
        return list;
    }

    [Fact]
    public void LanguageList_StartsWithTheSystemLanguage_WhichIsTheDefault()
    {
        using var app = Launch();
        var dialog = OpenSettings(app);

        Assert.Equal("System language", In(dialog, "LanguageText").Name);

        var items = OpenLanguageList(app, dialog).FindAllChildren();
        Assert.Equal("System language", items[0].Name);
        Assert.Equal(16, items.Length);
        Assert.Contains(items, item => item.Name == "Türkçe");
        Assert.Contains(items, item => item.Name == "English");
    }

    [Fact]
    public void LanguageList_OpensDownwards_ToTheBottomOfTheAboutCard()
    {
        // S20 → A: the list starts under the box and ends where the green About card ends.
        using var app = Launch();
        var dialog = OpenSettings(app);
        var scale = Scale(app);
        var box = In(dialog, "LanguageChoice").BoundingRectangle;
        var card = In(dialog, "AboutCard").BoundingRectangle;

        var list = OpenLanguageList(app, dialog).BoundingRectangle;
        Artifacts.CaptureScreen("language-list-open");

        Assert.InRange(list.Top - box.Bottom, 0, 8 * scale);
        Assert.InRange(Math.Abs(list.Bottom - card.Bottom), 0, 8 * scale);
        Assert.InRange(Math.Abs(list.Left - box.Left), 0, 4 * scale);
        Assert.InRange(list.Right, box.Left, box.Right + 1);
    }

    [Fact]
    public void ChoosingALanguage_RestartsTheAppInIt_AndKeepsTheChoice()
    {
        var app = Launch();
        try
        {
            var dialog = OpenSettings(app);
            var list = OpenLanguageList(app, dialog);
            Wait.ForElement(() => list.FindFirstChild(condition => condition.ByName("Türkçe"))).AsListBoxItem().Select();

            var previous = app.ProcessId;
            Assert.True(Wait.Until(() => app.HasExited, TimeSpan.FromSeconds(15)), "Choosing a language should restart the app.");
            app.Dispose();
            app = AppSession.AttachToRestarted(previous);

            Assert.Equal("Ekle", app.Find("AddItemButton").Name);
            Assert.Equal("tr", SettingsStore().Load().Language);
        }
        finally
        {
            app.Dispose();
        }
    }

    public static TheoryData<string> Languages() =>
        ["en", "tr", "uk", "pl", "de", "es", "hi", "fil", "fr", "pt", "id", "it", "ru", "ko", "sv"];

    [Theory]
    [MemberData(nameof(Languages))]
    public void Settings_FitsTheWidget_InEveryLanguage(string language)
    {
        using var app = Launch(language);
        var dialog = OpenSettings(app);
        var cross = In(dialog, "SettingsCloseButton").BoundingRectangle;
        var right = DialogBox.RightEdgeOf(new Point(cross.Left + 2, cross.Bottom + 2));
        var bounds = Rectangle.FromLTRB(app.MainWindow.BoundingRectangle.Left, cross.Top, right, app.MainWindow.BoundingRectangle.Bottom);

        Artifacts.CaptureScreen("settings-" + language);
        var themes = ThemeChoices.Select(id => In(dialog, id).BoundingRectangle).ToList();
        Assert.All(themes, theme => Assert.Equal(themes[0].Top, theme.Top));
        Assert.All(themes, theme => Assert.InRange(theme.Right, bounds.Left, bounds.Right));
        Assert.InRange(In(dialog, "LanguageChoice").BoundingRectangle.Right, bounds.Left, bounds.Right);
        Assert.InRange(In(dialog, "AlwaysOnTopSwitch").BoundingRectangle.Right, bounds.Left, bounds.Right);
        Assert.InRange(In(dialog, "AboutCard").BoundingRectangle.Right, bounds.Left, bounds.Right);
    }

    [Fact]
    public void CompactIcon_HasOnlyAThinFrameAroundTheLogo()
    {
        using var app = Launch();
        var scale = Scale(app);
        RealMouse.Click(app.Find("CompactButton").BoundingRectangle.Center());
        var icon = Wait.ForElement(() => app.TryFind("CompactIcon"));
        GridDriver.WaitForUi();

        var logo = In(icon, "CompactLogo").BoundingRectangle;
        var frame = (icon.BoundingRectangle.Width - logo.Width) / 2.0;

        Assert.InRange(frame, 0, (8 * scale) + 1);
    }

    [Fact]
    public void CompactIcon_HidesWhileAWindowIsFullScreen_AndComesBackAfterwards()
    {
        // T132: the icon stays on top of other windows, but not of a full-screen video or game.
        using var app = Launch();
        RealMouse.Click(app.Find("CompactButton").BoundingRectangle.Center());
        Wait.ForElement(() => app.TryFind("CompactIcon"));
        GridDriver.WaitForUi();
        Assert.True(Win32.IsVisible(app.WindowHandle), "The compact icon should be shown.");

        using var fullScreen = System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(
            "powershell.exe",
            "-NoProfile -Command \"Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.Form; "
            + "$f.Text = 'MEW full screen'; $f.FormBorderStyle = 'None'; $f.WindowState = 'Maximized'; $f.BackColor = 'Black'; "
            + "[System.Windows.Forms.Application]::Run($f)\"")
        { UseShellExecute = false, CreateNoWindow = true })!;
        try
        {
            Assert.True(Wait.Until(() => !Win32.IsVisible(app.WindowHandle), TimeSpan.FromSeconds(20)), "A full-screen window should hide the icon.");
        }
        finally
        {
            fullScreen.Kill();
        }

        Assert.True(Wait.Until(() => Win32.IsVisible(app.WindowHandle), TimeSpan.FromSeconds(10)), "The icon should come back when the full-screen window is gone.");
        Assert.True(Win32.IsTopmost(app.WindowHandle), "The icon should be on top again.");
    }

    [Fact]
    public void PinIsOnTheLeft_AndCompactButtonIsNextToClose()
    {
        using var app = Launch();
        var scale = Scale(app);
        var window = app.MainWindow.BoundingRectangle;
        var pin = app.Find("PinButton").BoundingRectangle;
        var compact = app.Find("CompactButton").BoundingRectangle;
        var close = app.Find("CloseButton").BoundingRectangle;

        Assert.InRange(pin.Left - window.Left, 0, 24 * scale);
        Assert.True(pin.Right < compact.Left, "The pin button should be left of the compact button.");
        Assert.InRange(close.Left - compact.Right, 0, 8 * scale);
    }
}
