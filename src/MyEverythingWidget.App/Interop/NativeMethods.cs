using System.Runtime.InteropServices;

namespace MyEverythingWidget.App.Interop;

/// <summary>
/// Win32 functions that the Windows App SDK does not expose.
/// </summary>
internal static partial class NativeMethods
{
    /// <summary>A window is about to be given its minimum and maximum tracking size.</summary>
    internal const uint GetMinMaxInfoMessage = 0x0024;

    /// <summary>The user is dragging a window edge; the proposed rectangle can be changed.</summary>
    internal const uint SizingMessage = 0x0214;

    /// <summary>The user finished moving or resizing the window.</summary>
    internal const uint ExitSizeMoveMessage = 0x0232;

    /// <summary>MonitorFromWindow: the monitor nearest to the window when it is on none.</summary>
    internal const uint MonitorDefaultToNearest = 2;

    private const int ClassNameLength = 256;

    /// <summary>Signature of a window subclass procedure (comctl32).</summary>
    [UnmanagedFunctionPointer(CallingConvention.Winapi)]
    internal delegate nint SubclassProcedure(nint window, uint message, nint wParam, nint lParam, nuint id, nuint data);

    [StructLayout(LayoutKind.Sequential)]
    internal struct NativePoint
    {
        public int X;
        public int Y;
    }

    [StructLayout(LayoutKind.Sequential)]
    internal struct NativeRect
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [StructLayout(LayoutKind.Sequential)]
    internal struct MonitorInfo
    {
        public int Size;
        public NativeRect Monitor;
        public NativeRect Work;
        public uint Flags;
    }

    [StructLayout(LayoutKind.Sequential)]
    internal struct MinMaxInfo
    {
        public NativePoint Reserved;
        public NativePoint MaxSize;
        public NativePoint MaxPosition;
        public NativePoint MinTrackSize;
        public NativePoint MaxTrackSize;
    }

    [LibraryImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool AllowSetForegroundWindow(uint processId);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool SetForegroundWindow(nint windowHandle);

    [LibraryImport("user32.dll")]
    internal static partial uint GetDpiForWindow(nint windowHandle);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool GetWindowRect(nint windowHandle, out NativeRect rect);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool GetClientRect(nint windowHandle, out NativeRect rect);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool IsIconic(nint windowHandle);

    /// <summary>SetWindowPos flags: keep position and z-order, do not activate.</summary>
    internal const uint ResizeOnlyFlags = 0x0002 | 0x0004 | 0x0010;

    /// <summary>SetWindowPos flags: keep size and z-order, do not activate.</summary>
    internal const uint MoveOnlyFlags = 0x0001 | 0x0004 | 0x0010;

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool SetWindowPos(nint windowHandle, nint insertAfter, int x, int y, int width, int height, uint flags);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool ClientToScreen(nint windowHandle, ref NativePoint point);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool GetCursorPos(out NativePoint point);

    [LibraryImport("comctl32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool SetWindowSubclass(nint windowHandle, nint procedure, nuint id, nuint data);

    [LibraryImport("comctl32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool RemoveWindowSubclass(nint windowHandle, nint procedure, nuint id);

    [LibraryImport("comctl32.dll")]
    internal static partial nint DefSubclassProc(nint windowHandle, uint message, nint wParam, nint lParam);

    [LibraryImport("user32.dll")]
    internal static partial nint GetForegroundWindow();

    [LibraryImport("user32.dll")]
    internal static partial nint MonitorFromWindow(nint windowHandle, uint flags);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool GetMonitorInfoW(nint monitor, ref MonitorInfo info);

    [LibraryImport("user32.dll", StringMarshalling = StringMarshalling.Utf16)]
    private static partial int GetClassNameW(nint windowHandle, [Out] char[] name, int length);

    /// <summary>Returns the window class name of <paramref name="windowHandle"/>, or an empty string.</summary>
    internal static string ClassNameOf(nint windowHandle)
    {
        var name = new char[ClassNameLength];
        var length = GetClassNameW(windowHandle, name, name.Length);
        return length > 0 ? new string(name, 0, length) : "";
    }

    /// <summary>Returns the whole area of <paramref name="monitor"/> (taskbar included), or <see langword="null"/>.</summary>
    internal static Core.Geometry.PixelRect? MonitorBounds(nint monitor)
    {
        var info = new MonitorInfo { Size = Marshal.SizeOf<MonitorInfo>() };
        if (!GetMonitorInfoW(monitor, ref info))
        {
            return null;
        }

        var bounds = info.Monitor;
        return new Core.Geometry.PixelRect(bounds.Left, bounds.Top, bounds.Right - bounds.Left, bounds.Bottom - bounds.Top);
    }
}
