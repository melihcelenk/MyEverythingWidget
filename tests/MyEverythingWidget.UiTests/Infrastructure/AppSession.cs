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
    private static readonly TimeSpan ReadyDelay = TimeSpan.FromMilliseconds(500);

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

    public static AppSession Launch(AppDataFolder data, IReadOnlyDictionary<string, string>? environment = null) =>
        Launch(data, environment, waitUntilReady: true);

    /// <summary>Launches without waiting for the content to settle, to observe what the user sees while it opens.</summary>
    public static AppSession LaunchWithoutSettling(AppDataFolder data) => Launch(data, environment: null, waitUntilReady: false);

    private static AppSession Launch(AppDataFolder data, IReadOnlyDictionary<string, string>? environment, bool waitUntilReady)
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
        var session = new AppSession(application, automation, window);
        if (waitUntilReady)
        {
            session.WaitUntilReady();
        }

        return session;
    }

    /// <summary>
    /// Waits until the widget's content is laid out and accepts input. The window appears before its content is ready;
    /// a click in that moment is lost, which made tests that click right after launch fail on a cold start.
    /// </summary>
    private void WaitUntilReady()
    {
        Wait.Until(() => TryFind("WidgetGrid") is not null || TryFind("CompactIcon") is not null, StartTimeout);
        Thread.Sleep(ReadyDelay);
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

    /// <summary>
    /// Attaches to the process that replaced the one with <paramref name="previousProcessId"/> after the app restarted
    /// itself, once its window is ready.
    /// </summary>
    public static AppSession AttachToRestarted(int previousProcessId)
    {
        SandboxGuard.SkipUnlessAllowed();
        Process? next = null;
        var started = Wait.Until(
            () => (next = Process.GetProcessesByName(Path.GetFileNameWithoutExtension(AppPaths.Executable()))
                .FirstOrDefault(process => process.Id != previousProcessId)) is not null,
            StartTimeout);
        if (!started)
        {
            throw new TimeoutException("The app did not start again.");
        }

        var application = Application.Attach(next!);
        var automation = new UIA3Automation();
        var window = application.GetMainWindow(automation, StartTimeout)
            ?? throw new TimeoutException("The restarted app did not show its main window.");
        var session = new AppSession(application, automation, window);
        session.WaitUntilReady();
        return session;
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

    /// <summary>
    /// Returns another top-level window by its title, or <see langword="null"/>. Searched by title only: in the sandbox
    /// the desktop's children do not match the launched process id.
    /// </summary>
    public AutomationElement? FindWindow(string title) =>
        _automation.GetDesktop().FindFirstChild(condition => condition.ByName(title));

    /// <summary>Lists the desktop's top-level windows, for failure messages.</summary>
    public string DescribeWindows() => string.Join(", ", _automation.GetDesktop()
        .FindAllChildren()
        .Select(window => $"'{window.Name}' ({window.ControlType}, pid {window.Properties.ProcessId.ValueOrDefault})"));

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

        // The sandbox has the host's display language; the tests read the English texts.
        startInfo.Environment["MEW_SYSTEM_LANGUAGE"] = "en-US";
        return startInfo;
    }
}
