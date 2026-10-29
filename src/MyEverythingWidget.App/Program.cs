using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.Windows.AppLifecycle;
using MyEverythingWidget.App.Interop;

namespace MyEverythingWidget.App;

/// <summary>
/// Entry point. Keeps the app single-instance: a second launch hands its activation to the running
/// instance, which brings its window to the front, and then exits.
/// </summary>
public static class Program
{
    private const string InstanceKey = "MyEverythingWidget.Main";

    /// <summary>Starts the app, or forwards the launch to the instance that is already running.</summary>
    [STAThread]
    public static int Main()
    {
        WinRT.ComWrappersSupport.InitializeComWrappers();

        var mainInstance = AppInstance.FindOrRegisterForKey(InstanceKey);
        if (!mainInstance.IsCurrent)
        {
            RedirectToMainInstance(mainInstance);
            return 0;
        }

        mainInstance.Activated += (_, _) => App.BringMainWindowToFront();

        Application.Start(startParams =>
        {
            var context = new DispatcherQueueSynchronizationContext(DispatcherQueue.GetForCurrentThread());
            SynchronizationContext.SetSynchronizationContext(context);
            _ = new App();
        });
        return 0;
    }

    private static void RedirectToMainInstance(AppInstance mainInstance)
    {
        // Only the foreground process may hand the foreground to another one.
        NativeMethods.AllowSetForegroundWindow(mainInstance.ProcessId);

        var activationArgs = AppInstance.GetCurrent().GetActivatedEventArgs();

        // Redirect on a worker thread: blocking the STA thread on this call can deadlock.
        Task.Run(() => mainInstance.RedirectActivationToAsync(activationArgs).AsTask()).Wait();
    }
}
