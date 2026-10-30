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

    /// <summary>Mouse button pressed over the non-client area.</summary>
    internal const uint NonClientLeftButtonDownMessage = 0x00A1;

    /// <summary>Hit-test value of the caption, which moves the window.</summary>
    internal const int CaptionHitTest = 2;

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
    internal static partial bool ReleaseCapture();

    /// <summary>SetWindowPos flags: keep position and z-order, do not activate.</summary>
    internal const uint ResizeOnlyFlags = 0x0002 | 0x0004 | 0x0010;

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool SetWindowPos(nint windowHandle, nint insertAfter, int x, int y, int width, int height, uint flags);

    [LibraryImport("user32.dll", EntryPoint = "SendMessageW")]
    internal static partial nint SendMessage(nint windowHandle, uint message, nint wParam, nint lParam);

    [LibraryImport("comctl32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool SetWindowSubclass(nint windowHandle, nint procedure, nuint id, nuint data);

    [LibraryImport("comctl32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    internal static partial bool RemoveWindowSubclass(nint windowHandle, nint procedure, nuint id);

    [LibraryImport("comctl32.dll")]
    internal static partial nint DefSubclassProc(nint windowHandle, uint message, nint wParam, nint lParam);
}
