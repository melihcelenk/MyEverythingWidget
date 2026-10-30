using System.Diagnostics;
using FlaUI.Core.AutomationElements;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Adding and opening app cards (MEW-4 Faz 5: U1-U6).
/// </summary>
public sealed class AppItemTests : IDisposable
{
    private const string GeneralId = "c1";
    private static readonly string CommandPrompt = Path.Combine(Environment.SystemDirectory, "cmd.exe");
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private void SeedApps(params AppItem[] apps) =>
        StateFiles.Save(_data, new WidgetState(WidgetState.CurrentSchemaVersion, [new Category(GeneralId, "General")], apps));

    private static AutomationElement OpenAddAppDialog(AppSession app)
    {
        RealMouse.Click(app.Find("AddItemButton").BoundingRectangle.Center());
        Wait.ForElement(() => app.FindInPopups("AddAppMenuItem")).AsMenuItem().Invoke();
        return Wait.ForElement(() => app.FindInPopups("AddAppDialog"));
    }

    private static AutomationElement In(AutomationElement parent, string automationId) =>
        Wait.ForElement(() => parent.FindFirstDescendant(condition => condition.ByAutomationId(automationId)));

    [Fact]
    public void InstalledApp_PickedFromList_IsAddedWithItsIcon()
    {
        SeedApps();
        string pickedName;
        using (var app = AppSession.Launch(_data))
        {
            var dialog = OpenAddAppDialog(app);
            var list = In(dialog, "InstalledAppsList");
            Assert.True(Wait.Until(() => list.FindAllChildren().Length > 0, TimeSpan.FromSeconds(30)), "The installed apps list stayed empty.");

            var item = list.FindAllChildren()[0];
            pickedName = item.Name;
            item.AsListBoxItem().Select();
            In(dialog, "PrimaryButton").AsButton().Invoke();

            // The list in the dialog also shows the name: wait for the dialog to close and the card to appear in the grid.
            Assert.True(Wait.Until(() => app.FindInPopups("AddAppDialog") is null), "The dialog should close.");
            Assert.True(Wait.Until(() => app.Find("WidgetGrid").FindAllDescendants(c => c.ByName(pickedName)).Length > 0));
            app.ClickCloseAndWaitForExit();
        }

        var added = Assert.IsType<AppItem>(Assert.Single(StateFiles.ReadState(_data).Items));
        Assert.Equal(pickedName, added.Name);
        Assert.StartsWith(@"shell:AppsFolder\", added.Target, StringComparison.Ordinal);
        Assert.NotNull(added.IconPath);
        Assert.True(File.Exists(Path.Combine(_data.Path, added.IconPath)), "The icon file should exist.");
    }

    [Fact]
    public void TypedPath_IsAddedWithSuggestedName()
    {
        SeedApps();
        using (var app = AppSession.Launch(_data))
        {
            var dialog = OpenAddAppDialog(app);
            In(dialog, "ManualTargetBox").AsTextBox().Text = CommandPrompt;
            Assert.True(Wait.Until(() => In(dialog, "ManualNameBox").AsTextBox().Text == "Cmd"));
            In(dialog, "PrimaryButton").AsButton().Invoke();
            Assert.True(Wait.Until(() => app.FindInPopups("AddAppDialog") is null), "The dialog should close.");
            Assert.True(Wait.Until(() => app.Find("WidgetGrid").FindAllDescendants(c => c.ByName("Cmd")).Length > 0));
            app.ClickCloseAndWaitForExit();
        }

        var added = Assert.IsType<AppItem>(Assert.Single(StateFiles.ReadState(_data).Items));
        Assert.Equal(CommandPrompt, added.Target);
        Assert.Equal(LaunchKind.Executable, added.LaunchKind);
        Assert.NotNull(added.IconPath);
    }

    [Fact]
    public void ClickingAppCard_StartsTheProgram()
    {
        SeedApps(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Command Prompt", CommandPrompt, LaunchKind.Executable, null));
        var before = Process.GetProcessesByName("cmd").Select(process => process.Id).ToHashSet();
        using var app = AppSession.Launch(_data);
        GridDriver.WaitForUi();

        RealMouse.Click(app.Find("Card_A1").BoundingRectangle.Center());

        Process? started = null;
        var launched = Wait.Until(() => (started = Process.GetProcessesByName("cmd").FirstOrDefault(process => !before.Contains(process.Id))) is not null);
        if (!launched)
        {
            Artifacts.CaptureScreen("launch-failed");
        }

        Assert.True(launched, "Clicking the card should start cmd.exe.");
        started!.Kill();
    }

    [Fact]
    public void ResetIcon_GivesCardItsProgramIcon()
    {
        SeedApps(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Command Prompt", CommandPrompt, LaunchKind.Executable, null));
        using (var app = AppSession.Launch(_data))
        {
            RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
            Wait.ForElement(() => app.FindInPopups("ChangeIconMenuItem")).AsMenuItem().Invoke();
            var dialog = Wait.ForElement(() => app.FindInPopups("IconPickerDialog"));
            Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByName("Reset to original"))).AsButton().Invoke();
            Assert.True(Wait.Until(() => StateFiles.ReadItem(_data, "A1") is AppItem { IconPath: not null }));
            app.ClickCloseAndWaitForExit();
        }

        var iconPath = Assert.IsType<AppItem>(StateFiles.ReadItem(_data, "A1")).IconPath!;
        Assert.True(File.Exists(Path.Combine(_data.Path, iconPath)));
    }

    [Fact]
    public void ClickingCardOfRemovedProgram_ShowsWarning()
    {
        SeedApps(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Old tool", @"C:\removed\tool.exe", LaunchKind.Executable, null));
        using var app = AppSession.Launch(_data);

        RealMouse.Click(app.Find("Card_A1").BoundingRectangle.Center());

        var statusBar = app.Find("StatusInfoBar");
        Assert.True(Wait.Until(() => statusBar.FindAllDescendants().Any(element =>
            (element.Properties.Name.ValueOrDefault ?? "").Contains("could not be found", StringComparison.Ordinal))));
    }
}
