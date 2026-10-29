using System.Runtime.InteropServices;

namespace MyEverythingWidget.App.Interop;

/// <summary>
/// Win32 functions that the Windows App SDK does not expose.
/// </summary>
internal static partial class NativeMethods
{
    [LibraryImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool AllowSetForegroundWindow(uint processId);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool SetForegroundWindow(nint windowHandle);

    [LibraryImport("user32.dll")]
    internal static partial uint GetDpiForWindow(nint windowHandle);
}
