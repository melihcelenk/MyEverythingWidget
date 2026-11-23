using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.UIA3;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>Reads the taskbar's app buttons through UI Automation.</summary>
internal static class Taskbar
{
    private const string TaskbarClass = "Shell_TrayWnd";

    /// <summary>The names of the taskbar's buttons (for example "Task Timer Widget - 1 running window").</summary>
    public static IReadOnlyList<string> ButtonNames()
    {
        using var automation = new UIA3Automation();
        var taskbar = automation.GetDesktop().FindFirstChild(condition => condition.ByClassName(TaskbarClass));
        if (taskbar is null)
        {
            return [];
        }

        return taskbar.FindAllDescendants(condition => condition.ByControlType(ControlType.Button))
            .Select(button => button.Properties.Name.ValueOrDefault ?? string.Empty)
            .Where(name => name.Length > 0)
            .ToList();
    }

    /// <summary>Whether the taskbar shows a button whose name starts with <paramref name="appName"/>.</summary>
    public static bool HasButtonFor(string appName) =>
        ButtonNames().Any(name => name.StartsWith(appName, StringComparison.OrdinalIgnoreCase));
}
