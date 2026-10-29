using System.Runtime.InteropServices;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Win32 calls used to observe window state that UI Automation does not report.
/// </summary>
internal static partial class Win32
{
    private const int ExtendedStyleIndex = -20;
    private const long TopmostStyle = 0x00000008;
    private const uint NoSizeNoZOrderNoActivate = 0x0001 | 0x0004 | 0x0010;

    [StructLayout(LayoutKind.Sequential)]
    internal struct Rect
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    public static bool IsTopmost(nint window) => (GetWindowLongPtrW(window, ExtendedStyleIndex) & TopmostStyle) != 0;

    public static Rect GetBounds(nint window)
    {
        GetWindowRect(window, out var rect);
        return rect;
    }

    public static void MoveTo(nint window, int x, int y) => SetWindowPos(window, 0, x, y, 0, 0, NoSizeNoZOrderNoActivate);

    public static nint ForegroundWindow() => GetForegroundWindow();

    [LibraryImport("user32.dll")]
    private static partial long GetWindowLongPtrW(nint window, int index);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool GetWindowRect(nint window, out Rect rect);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool SetWindowPos(nint window, nint insertAfter, int x, int y, int width, int height, uint flags);

    [LibraryImport("user32.dll")]
    private static partial nint GetForegroundWindow();
}
