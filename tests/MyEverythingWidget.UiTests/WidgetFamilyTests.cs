using System.Diagnostics;
using FlaUI.Core.AutomationElements;
using FlaUI.UIA3;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// MEW-5: My Everything Widget as the widget family hub with Task Timer Widget as a member. Both MSIX packages must be
/// installed (the sandbox runner installs them and sets <see cref="AppUserModelIdVariable"/> and
/// <see cref="MemberUserModelIdVariable"/>); elsewhere the tests are skipped.
/// </summary>
public sealed class WidgetFamilyTests
{
    private const string AppUserModelIdVariable = "MEW_APP_AUMID";
    private const string MemberUserModelIdVariable = "MEW_MEMBER_AUMID";
    private const string MemberName = "Task Timer Widget";
    private const string MemberProcess = "TaskTimerWidget";

    /// <summary>The member looks for the hub every 2 seconds; this leaves room for a slow sandbox.</summary>
    private static readonly TimeSpan HubNoticed = TimeSpan.FromSeconds(15);

    private static (string Hub, string Member) Packages()
    {
        var hub = Environment.GetEnvironmentVariable(AppUserModelIdVariable);
        var member = Environment.GetEnvironmentVariable(MemberUserModelIdVariable);
        Assert.SkipWhen(
            string.IsNullOrWhiteSpace(hub) || string.IsNullOrWhiteSpace(member),
            "The hub and member MSIX packages are not installed here.");
        return (hub!, member!);
    }

    /// <summary>
    /// The packaged hub keeps its settings in the package folder, shared with <see cref="PackagedAppTests"/>; these
    /// tests leave it in compact mode, so its settings are removed afterwards.
    /// </summary>
    private static void ResetHubSettings(string hubUserModelId)
    {
        var settings = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Packages", hubUserModelId.Split('!')[0], "LocalState", "settings.json");
        foreach (var process in Process.GetProcessesByName("MyEverythingWidget"))
        {
            process.Kill();
            process.WaitForExit(5000);
        }

        File.Delete(settings);
    }

    private static void StopMember()
    {
        foreach (var process in Process.GetProcessesByName(MemberProcess))
        {
            process.Kill();
            process.WaitForExit(5000);
        }
    }

    private static Window LaunchMember(string appUserModelId, UIA3Automation automation)
    {
        var member = FlaUI.Core.Application.LaunchStoreApp(appUserModelId);
        return member.GetMainWindow(automation, TimeSpan.FromSeconds(30))
            ?? throw new TimeoutException("Task Timer Widget did not show its window.");
    }

    private static AutomationElement EnterCompactMode(AppSession hub)
    {
        if (hub.TryFind("CompactIcon") is not { IsOffscreen: false })
        {
            RealMouse.Click(hub.Find("CompactButton").BoundingRectangle.Center());
        }

        var icon = Wait.ForElement(() => hub.TryFind("CompactIcon"));
        GridDriver.WaitForUi();
        return icon;
    }

    /// <summary>Moves the compact icon so that its left edge is at <paramref name="left"/> and it is centred vertically.</summary>
    private static void MoveIconTo(AppSession hub, int left)
    {
        var workArea = Win32.WorkAreaOf(hub.WindowHandle);
        var bounds = Win32.GetBounds(hub.WindowHandle);
        Win32.MoveTo(hub.WindowHandle, left, workArea.Top + ((workArea.Height - (bounds.Bottom - bounds.Top)) / 2));
        GridDriver.WaitForUi();
    }

    private static nint WaitForMemberWindow()
    {
        nint handle = 0;
        Assert.True(
            Wait.Until(
                () => (handle = Process.GetProcessesByName(MemberProcess).Select(process => process.MainWindowHandle).FirstOrDefault(window => window != 0)) != 0,
                TimeSpan.FromSeconds(30)),
            "Task Timer Widget did not open.");
        return handle;
    }

    private static bool Inside(System.Drawing.Rectangle area, System.Drawing.Rectangle bounds) =>
        bounds.Left >= area.Left && bounds.Top >= area.Top && bounds.Right <= area.Right && bounds.Bottom <= area.Bottom;

    [Fact]
    public void Member_LeavesTheTaskbarWhileTheHubRuns_OpensNextToItsIcon_AndComesBackWhenTheHubCrashes()
    {
        var (hubId, memberId) = Packages();
        StopMember();
        using var automation = new UIA3Automation();
        try
        {
            // Alone, the member has its own taskbar button (this also shows the taskbar is readable here).
            var memberWindow = LaunchMember(memberId, automation);
            Assert.True(
                Wait.Until(() => Taskbar.HasButtonFor(MemberName), TimeSpan.FromSeconds(10)),
                "Task Timer Widget alone should be on the taskbar. Buttons: " + string.Join(" | ", Taskbar.ButtonNames()));

            using var hub = AppSession.LaunchPackaged(hubId);
            Assert.True(
                Wait.Until(() => !Taskbar.HasButtonFor(MemberName), HubNoticed),
                "With the hub running, Task Timer Widget should leave the taskbar. Buttons: " + string.Join(" | ", Taskbar.ButtonNames()));

            // Right-click on the compact icon shows the member on its preferred side; clicking it places it there.
            var icon = EnterCompactMode(hub);
            var workArea = Win32.WorkAreaOf(hub.WindowHandle);
            MoveIconTo(hub, workArea.Left + (workArea.Width / 2));
            RealMouse.RightClick(icon.BoundingRectangle.Center());
            var slot = Wait.ForElement(() => hub.FindInPopups("FamilySlot_Right"));
            Artifacts.CaptureScreen("family-menu");
            Assert.Equal(MemberName, slot.Name);
            RealMouse.Click(slot.BoundingRectangle.Center());

            var iconBounds = Win32.GetBounds(hub.WindowHandle);
            var memberHandle = memberWindow.Properties.NativeWindowHandle.Value;
            Assert.True(
                Wait.Until(() =>
                {
                    var placed = Win32.GetBounds(memberHandle);
                    return placed.Left >= iconBounds.Right && placed.Left - iconBounds.Right <= 40;
                }, TimeSpan.FromSeconds(10)),
                $"Task Timer Widget should open right of the icon {iconBounds.Left},{iconBounds.Top}-{iconBounds.Right},{iconBounds.Bottom}; it is at {Win32.GetBounds(memberHandle).Left},{Win32.GetBounds(memberHandle).Top}.");
            Artifacts.CaptureScreen("family-member-placed");

            // Faz 4: dragging the icon moves the member along.
            var start = Win32.GetBounds(hub.WindowHandle);
            RealMouse.MoveTo(new System.Drawing.Point(start.Left + 32, start.Top + 32));
            RealMouse.LeftDown();
            for (var step = 1; step <= 10; step++)
            {
                RealMouse.MoveTo(new System.Drawing.Point(start.Left + 32 - (step * 20), start.Top + 32 + (step * 10)));
                Thread.Sleep(30);
            }

            RealMouse.LeftUp();
            var moved = Win32.GetBounds(hub.WindowHandle);
            Assert.True(moved.Left < start.Left, "The drag should have moved the icon.");
            Assert.True(
                Wait.Until(() =>
                {
                    var placed = Win32.GetBounds(memberHandle);
                    return placed.Left >= moved.Right && placed.Left - moved.Right <= 40;
                }, TimeSpan.FromSeconds(10)),
                $"Task Timer Widget should follow the icon to {moved.Right}; it is at {Win32.GetBounds(memberHandle).Left}.");

            // S04 → A: the hub crashing leaves the member open, back on the taskbar.
            Process.GetProcessById(hub.ProcessId).Kill();
            Assert.True(
                Wait.Until(() => Taskbar.HasButtonFor(MemberName), HubNoticed),
                "After the hub is gone, Task Timer Widget should be back on the taskbar. Buttons: " + string.Join(" | ", Taskbar.ButtonNames()));
            Assert.True(Win32.IsVisible(memberHandle), "Task Timer Widget should stay open.");
        }
        finally
        {
            StopMember();
            ResetHubSettings(hubId);
        }
    }

    [Fact]
    public void SecondStartOfTheMember_DoesNotOpenASecondWindow()
    {
        var (_, memberId) = Packages();
        StopMember();
        using var automation = new UIA3Automation();
        try
        {
            LaunchMember(memberId, automation);
            Process.Start(new ProcessStartInfo("explorer.exe", $"shell:AppsFolder\\{memberId}") { UseShellExecute = false });

            Thread.Sleep(TimeSpan.FromSeconds(5));
            Assert.Single(Process.GetProcessesByName(MemberProcess));
        }
        finally
        {
            StopMember();
        }
    }

    [Fact]
    public void IconAtTheRightEdgeOfTheScreen_ShowsTheMenuOnTheScreen_AndOpensTheMemberOnTheLeft()
    {
        var (hubId, _) = Packages();
        StopMember();
        try
        {
            using var hub = AppSession.LaunchPackaged(hubId);
            var icon = EnterCompactMode(hub);
            var workArea = Win32.WorkAreaOf(hub.WindowHandle);
            var iconBounds = Win32.GetBounds(hub.WindowHandle);
            MoveIconTo(hub, workArea.Right - (iconBounds.Right - iconBounds.Left) - 4);

            RealMouse.RightClick(icon.BoundingRectangle.Center());
            var slot = Wait.ForElement(() => hub.FindInPopups("FamilySlot_Right"));
            GridDriver.WaitForUi();
            Artifacts.CaptureScreen("family-menu-at-edge");
            Assert.True(Inside(workArea, slot.BoundingRectangle), $"The menu should stay on the screen {workArea}; it is at {slot.BoundingRectangle}.");

            RealMouse.Click(slot.BoundingRectangle.Center());
            var member = WaitForMemberWindow();
            var placedIcon = Win32.GetBounds(hub.WindowHandle);
            Assert.True(
                Wait.Until(() => Win32.GetBounds(member).Right <= placedIcon.Left + 16, TimeSpan.FromSeconds(10)),
                $"With no room on the right, Task Timer Widget should open left of the icon at {placedIcon.Left}; it ends at {Win32.GetBounds(member).Right}.");
        }
        finally
        {
            StopMember();
            ResetHubSettings(hubId);
        }
    }
}
