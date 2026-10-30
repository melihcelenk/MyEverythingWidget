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

    /// <summary>Screen position of the window's client area top-left corner (what the user sees as the window corner).</summary>
    public static System.Drawing.Point ClientOrigin(nint window)
    {
        var point = new NativePoint();
        ClientToScreen(window, ref point);
        return new System.Drawing.Point(point.X, point.Y);
    }

    /// <summary>Client area in screen coordinates.</summary>
    public static System.Drawing.Rectangle ClientBounds(nint window)
    {
        GetClientRect(window, out var client);
        var origin = ClientOrigin(window);
        return new System.Drawing.Rectangle(origin.X, origin.Y, client.Right - client.Left, client.Bottom - client.Top);
    }

    /// <summary>Work area of the monitor that holds most of the window.</summary>
    public static System.Drawing.Rectangle WorkAreaOf(nint window)
    {
        var info = new MonitorInfo { Size = Marshal.SizeOf<MonitorInfo>() };
        GetMonitorInfoW(MonitorFromWindow(window, NearestMonitor), ref info);
        return System.Drawing.Rectangle.FromLTRB(info.Work.Left, info.Work.Top, info.Work.Right, info.Work.Bottom);
    }

    /// <summary>Gets a value indicating whether the mouse cursor currently shows the diagonal (NW-SE) resize arrows.</summary>
    public static bool CursorIsDiagonalResize()
    {
        var info = new CursorInfo { Size = Marshal.SizeOf<CursorInfo>() };
        GetCursorInfo(ref info);
        return info.Cursor == LoadCursorW(0, DiagonalResizeCursor);
    }

    private const uint NearestMonitor = 2;
    private const nint DiagonalResizeCursor = 32642;

    [StructLayout(LayoutKind.Sequential)]
    private struct NativePoint
    {
        public int X;
        public int Y;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MonitorInfo
    {
        public int Size;
        public Rect Monitor;
        public Rect Work;
        public uint Flags;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct CursorInfo
    {
        public int Size;
        public uint Flags;
        public nint Cursor;
        public NativePoint Position;
    }

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool ClientToScreen(nint window, ref NativePoint point);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool GetClientRect(nint window, out Rect rect);

    [LibraryImport("user32.dll")]
    private static partial nint MonitorFromWindow(nint window, uint flags);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool GetMonitorInfoW(nint monitor, ref MonitorInfo info);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool GetCursorInfo(ref CursorInfo info);

    [LibraryImport("user32.dll")]
    private static partial nint LoadCursorW(nint instance, nint name);

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
