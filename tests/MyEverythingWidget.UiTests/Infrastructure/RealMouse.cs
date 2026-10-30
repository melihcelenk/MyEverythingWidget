using System.Drawing;
using System.Runtime.InteropServices;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Mouse input through <c>SendInput</c>, so applications see real move events with the button state.
/// FlaUI's <c>Mouse.MoveTo</c> jumps the cursor with <c>SetCursorPos</c>; WinUI does not treat that as a drag
/// (the pointer position stays stale and capture is lost), which a real user's mouse never causes.
/// </summary>
internal static partial class RealMouse
{
    private const uint InputMouse = 0;
    private const uint MoveFlag = 0x0001;
    private const uint LeftDownFlag = 0x0002;
    private const uint LeftUpFlag = 0x0004;
    private const uint RightDownFlag = 0x0008;
    private const uint RightUpFlag = 0x0010;
    private const uint VirtualDeskFlag = 0x4000;
    private const uint AbsoluteFlag = 0x8000;
    private const int VirtualScreenX = 76;
    private const int VirtualScreenY = 77;
    private const int VirtualScreenWidth = 78;
    private const int VirtualScreenHeight = 79;
    private const double NormalizedMax = 65535.0;

    public static void MoveTo(Point point)
    {
        var left = GetSystemMetrics(VirtualScreenX);
        var top = GetSystemMetrics(VirtualScreenY);
        var width = GetSystemMetrics(VirtualScreenWidth);
        var height = GetSystemMetrics(VirtualScreenHeight);
        var x = (int)Math.Round((point.X - left) * NormalizedMax / (width - 1));
        var y = (int)Math.Round((point.Y - top) * NormalizedMax / (height - 1));
        Send(MoveFlag | AbsoluteFlag | VirtualDeskFlag, x, y);
    }

    public static void LeftDown() => Send(LeftDownFlag, 0, 0);

    public static void LeftUp() => Send(LeftUpFlag, 0, 0);

    public static void Click(Point point)
    {
        MoveTo(point);
        Thread.Sleep(50);
        Send(LeftDownFlag, 0, 0);
        Send(LeftUpFlag, 0, 0);
    }

    public static void RightClick(Point point)
    {
        MoveTo(point);
        Thread.Sleep(50);
        Send(RightDownFlag, 0, 0);
        Send(RightUpFlag, 0, 0);
    }

    private static void Send(uint flags, int x, int y)
    {
        var input = new Input
        {
            Type = InputMouse,
            Mouse = new MouseInput { X = x, Y = y, Flags = flags },
        };
        if (SendInput(1, [input], Marshal.SizeOf<Input>()) != 1)
        {
            throw new InvalidOperationException($"SendInput failed with error {Marshal.GetLastPInvokeError()}.");
        }
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct MouseInput
    {
        public int X;
        public int Y;
        public uint MouseData;
        public uint Flags;
        public uint Time;
        public nint ExtraInfo;
    }

    [StructLayout(LayoutKind.Explicit)]
    private struct Input
    {
        [FieldOffset(0)]
        public uint Type;

        // The union starts at pointer alignment on 64-bit Windows.
        [FieldOffset(8)]
        public MouseInput Mouse;
    }

    [LibraryImport("user32.dll", SetLastError = true)]
    private static partial uint SendInput(uint count, [In] Input[] inputs, int size);

    [LibraryImport("user32.dll")]
    private static partial int GetSystemMetrics(int index);
}
