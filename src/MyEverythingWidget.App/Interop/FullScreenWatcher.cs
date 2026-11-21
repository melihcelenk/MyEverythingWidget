using Microsoft.UI.Dispatching;
using MyEverythingWidget.Core.Geometry;

namespace MyEverythingWidget.App.Interop;

/// <summary>
/// Watches whether the foreground window is full screen (a video, a game or a presentation) on the monitor of a given
/// window, and reports each change. The compact icon stays on top of other windows but gives way to these.
/// </summary>
internal sealed class FullScreenWatcher
{
    private static readonly TimeSpan Interval = TimeSpan.FromMilliseconds(500);

    /// <summary>Window classes of the desktop and the taskbar, which cover the screen without being full-screen apps.</summary>
    private static readonly HashSet<string> ShellClasses = ["Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"];

    private readonly nint _window;
    private readonly DispatcherQueueTimer _timer;
    private bool _isCovered;

    /// <summary>Creates the watcher for <paramref name="window"/>; it reports on <paramref name="queue"/>'s thread.</summary>
    public FullScreenWatcher(nint window, DispatcherQueue queue)
    {
        ArgumentNullException.ThrowIfNull(queue);

        _window = window;
        _timer = queue.CreateTimer();
        _timer.Interval = Interval;
        _timer.IsRepeating = true;
        _timer.Tick += (_, _) => Check();
    }

    /// <summary>Raised when a full-screen window appears on the monitor (<see langword="true"/>) or goes away.</summary>
    public event EventHandler<bool>? CoveredChanged;

    /// <summary>Starts watching.</summary>
    public void Start()
    {
        _isCovered = false;
        _timer.Start();
    }

    /// <summary>Stops watching; a covered state is reported as gone.</summary>
    public void Stop()
    {
        _timer.Stop();
        if (_isCovered)
        {
            _isCovered = false;
            CoveredChanged?.Invoke(this, false);
        }
    }

    private void Check()
    {
        var covered = IsForegroundFullScreen();
        if (covered != _isCovered)
        {
            _isCovered = covered;
            CoveredChanged?.Invoke(this, covered);
        }
    }

    private bool IsForegroundFullScreen()
    {
        var foreground = NativeMethods.GetForegroundWindow();
        if (foreground == 0 || foreground == _window || ShellClasses.Contains(NativeMethods.ClassNameOf(foreground)))
        {
            return false;
        }

        var monitor = NativeMethods.MonitorFromWindow(foreground, NativeMethods.MonitorDefaultToNearest);
        if (monitor != NativeMethods.MonitorFromWindow(_window, NativeMethods.MonitorDefaultToNearest)
            || !NativeMethods.GetWindowRect(foreground, out var rect)
            || NativeMethods.MonitorBounds(monitor) is not { } bounds)
        {
            return false;
        }

        return FullScreen.Covers(new PixelRect(rect.Left, rect.Top, rect.Right - rect.Left, rect.Bottom - rect.Top), bounds);
    }
}
