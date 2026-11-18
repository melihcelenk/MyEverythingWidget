using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Makes the test process per-monitor DPI aware before any test runs. UI Automation reports physical pixels; a
/// DPI-unaware process would capture and click in scaled coordinates, so on a display scaled above 100% screenshots
/// and colour checks would read the wrong place.
/// </summary>
internal static partial class DpiAwareness
{
    private static readonly nint PerMonitorAwareV2 = -4;

    [ModuleInitializer]
    internal static void Initialize() => SetProcessDpiAwarenessContext(PerMonitorAwareV2);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool SetProcessDpiAwarenessContext(nint context);
}
