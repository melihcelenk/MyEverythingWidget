using System.Text.Json;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using MyEverythingWidget.UiTests.Infrastructure;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// End-to-end checks of the widget window (MEW-4 Faz 1 acceptance criteria F1.1-F1.9).
/// </summary>
public sealed class MainWindowTests : IDisposable
{
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    [Fact]
    public void Launch_ShowsTitledWindowWithPinAndCloseButtons()
    {
        using var app = AppSession.Launch(_data);

        Assert.Equal(AppSession.WindowTitle, app.MainWindow.Title);
        Assert.Equal(ControlType.Button, app.Find("PinButton").ControlType);
        Assert.Equal(ControlType.Button, app.Find("CloseButton").ControlType);
    }

    [Fact]
    public void PinButton_TogglesAlwaysOnTop()
    {
        using var app = AppSession.Launch(_data);
        Assert.False(Win32.IsTopmost(app.WindowHandle));

        app.Find("PinButton").AsToggleButton().Toggle();
        Assert.True(Wait.Until(() => Win32.IsTopmost(app.WindowHandle)), "Window should become topmost after pin.");

        app.Find("PinButton").AsToggleButton().Toggle();
        Assert.True(Wait.Until(() => !Win32.IsTopmost(app.WindowHandle)), "Window should stop being topmost after unpin.");
    }

    [Fact]
    public void Pinned_StaysPinnedAfterRestart()
    {
        using (var first = AppSession.Launch(_data))
        {
            first.Find("PinButton").AsToggleButton().Toggle();
            Assert.True(Wait.Until(() => Win32.IsTopmost(first.WindowHandle)));
            first.ClickCloseAndWaitForExit();
        }

        using var second = AppSession.Launch(_data);

        Assert.True(Win32.IsTopmost(second.WindowHandle));
        Assert.Equal(ToggleState.On, second.Find("PinButton").AsToggleButton().ToggleState);
    }

    [Fact]
    public void MovedWindow_ReopensAtSamePosition()
    {
        using (var first = AppSession.Launch(_data))
        {
            Win32.MoveTo(first.WindowHandle, 300, 200);
            Assert.True(Wait.Until(() => Win32.GetBounds(first.WindowHandle).Left == 300));
            first.ClickCloseAndWaitForExit();
        }

        using var second = AppSession.Launch(_data);
        var bounds = Win32.GetBounds(second.WindowHandle);

        Assert.Equal(300, bounds.Left);
        Assert.Equal(200, bounds.Top);
    }

    [Fact]
    public void SecondLaunch_ExitsAndBringsExistingWindowToFront()
    {
        using var app = AppSession.Launch(_data);

        using var second = AppSession.StartSecondProcess(_data);
        Assert.True(second.WaitForExit(15_000), "Second process should exit after redirecting.");

        Assert.Equal(0, second.ExitCode);
        Assert.False(app.HasExited);
        Assert.True(Wait.Until(() => Win32.ForegroundWindow() == app.WindowHandle), "Existing window should come to the front.");
    }

    [Fact]
    public void CloseButton_ExitsAndSavesSettings()
    {
        using var app = AppSession.Launch(_data);

        app.ClickCloseAndWaitForExit();

        Assert.True(File.Exists(_data.SettingsFile));
        using var settings = JsonDocument.Parse(File.ReadAllText(_data.SettingsFile));
        Assert.Equal(JsonValueKind.Object, settings.RootElement.GetProperty("windowBounds").ValueKind);
    }

    [Fact]
    public void CorruptSettings_OpensWithDefaultsAndKeepsCorruptCopy()
    {
        Directory.CreateDirectory(_data.Path);
        File.WriteAllText(_data.SettingsFile, "{ not json");

        using var app = AppSession.Launch(_data);

        Assert.False(Win32.IsTopmost(app.WindowHandle));
        Assert.Single(Directory.GetFiles(_data.Path, "settings.corrupt-*.json"));
    }
}
