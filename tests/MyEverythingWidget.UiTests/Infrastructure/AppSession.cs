using System.Diagnostics;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.UIA3;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// One running instance of the app, launched against an <see cref="AppDataFolder"/>.
/// </summary>
internal sealed class AppSession : IDisposable
{
    public const string WindowTitle = "My Everything Widget";

    private static readonly TimeSpan StartTimeout = TimeSpan.FromSeconds(30);
    private static readonly TimeSpan ExitTimeout = TimeSpan.FromSeconds(15);

    private readonly Application _application;
    private readonly UIA3Automation _automation;

    private AppSession(Application application, UIA3Automation automation, Window mainWindow)
    {
        _application = application;
        _automation = automation;
        MainWindow = mainWindow;
    }

    public Window MainWindow { get; }

    public nint WindowHandle => MainWindow.Properties.NativeWindowHandle.Value;

    public int ProcessId => _application.ProcessId;

    public bool HasExited => _application.HasExited;

    public static AppSession Launch(AppDataFolder data, IReadOnlyDictionary<string, string>? environment = null)
    {
        SandboxGuard.SkipUnlessAllowed();
        var startInfo = CreateStartInfo(data);
        foreach (var (name, value) in environment ?? new Dictionary<string, string>())
        {
            startInfo.Environment[name] = value;
        }

        var application = Application.Launch(startInfo);
        var automation = new UIA3Automation();
        var window = application.GetMainWindow(automation, StartTimeout)
            ?? throw new TimeoutException("The app did not show its main window.");
        return new AppSession(application, automation, window);
    }

    /// <summary>Launches the installed MSIX package by its Application User Model ID.</summary>
    public static AppSession LaunchPackaged(string appUserModelId)
    {
        SandboxGuard.SkipUnlessAllowed();
        var application = Application.LaunchStoreApp(appUserModelId);
        var automation = new UIA3Automation();
        var window = application.GetMainWindow(automation, StartTimeout)
            ?? throw new TimeoutException("The packaged app did not show its main window.");
        return new AppSession(application, automation, window);
    }

    /// <summary>Starts another process of the app without attaching to it.</summary>
    public static Process StartSecondProcess(AppDataFolder data)
    {
        SandboxGuard.SkipUnlessAllowed();
        return Process.Start(CreateStartInfo(data)) ?? throw new InvalidOperationException("Second process did not start.");
    }

    public AutomationElement Find(string automationId) =>
        TryFind(automationId) ?? throw new InvalidOperationException($"Element '{automationId}' not found.");

    public AutomationElement? TryFind(string automationId) =>
        MainWindow.FindFirstDescendant(condition => condition.ByAutomationId(automationId));

    /// <summary>
    /// Finds an element of this app anywhere on the desktop; menus and flyouts live in their own popup windows.
    /// </summary>
    public AutomationElement? FindInPopups(string automationId) =>
        TryFind(automationId)
        ?? _automation.GetDesktop().FindFirstDescendant(condition =>
            condition.ByAutomationId(automationId).And(condition.ByProcessId(_application.ProcessId)));

    public void ClickCloseAndWaitForExit()
    {
        Find("CloseButton").AsButton().Invoke();
        if (!WaitForExit())
        {
            throw new TimeoutException("The app did not exit after Close.");
        }
    }

    public bool WaitForExit()
    {
        var deadline = DateTime.UtcNow + ExitTimeout;
        while (!_application.HasExited && DateTime.UtcNow < deadline)
        {
            Thread.Sleep(100);
        }

        return _application.HasExited;
    }

    public void Dispose()
    {
        if (!_application.HasExited)
        {
            _application.Kill();
        }

        _application.Dispose();
        _automation.Dispose();
    }

    private static ProcessStartInfo CreateStartInfo(AppDataFolder data)
    {
        var startInfo = new ProcessStartInfo(AppPaths.Executable()) { UseShellExecute = false };
        startInfo.Environment["MEW_DATA_DIR"] = data.Path;
        return startInfo;
    }
}
