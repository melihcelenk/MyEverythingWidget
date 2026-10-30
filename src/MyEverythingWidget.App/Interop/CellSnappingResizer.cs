using System.Runtime.InteropServices;
using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Core.Grid;
using static MyEverythingWidget.App.Interop.NativeMethods;

namespace MyEverythingWidget.App.Interop;

/// <summary>
/// Makes the user's edge and corner drags resize the window by whole grid cells. The rectangle Windows proposes while
/// dragging (<c>WM_SIZING</c>) is snapped to the nearest grid size the board accepts, and the tracking limits
/// (<c>WM_GETMINMAXINFO</c>) follow the board's minimum and maximum grid.
/// </summary>
internal sealed class CellSnappingResizer
{
    private const int LeftEdge = 1;
    private const int TopEdge = 3;
    private const int TopLeftCorner = 4;
    private const int TopRightCorner = 5;
    private const int BottomLeftCorner = 7;

    private readonly nint _window;
    private readonly GridWindowSizing _sizing;
    private readonly Func<GridSize, GridSize> _resizeGrid;
    private readonly Func<GridSize> _minimumGrid;
    private readonly Func<PixelSize?> _fixedClientSize;
    private readonly Action _resizeEnded;
    private readonly SubclassProcedure _procedure;
    private readonly nint _procedurePointer;

    /// <summary>Starts snapping the window's resizing.</summary>
    /// <param name="window">Window handle.</param>
    /// <param name="sizing">Grid and chrome measures.</param>
    /// <param name="resizeGrid">Applies a requested grid size and returns the size actually applied.</param>
    /// <param name="minimumGrid">Smallest grid that holds every item.</param>
    /// <param name="fixedClientSize">Client size the window must keep (compact mode), or <see langword="null"/>.</param>
    /// <param name="resizeEnded">Called when the user lets go of the edge.</param>
    public CellSnappingResizer(
        nint window,
        GridWindowSizing sizing,
        Func<GridSize, GridSize> resizeGrid,
        Func<GridSize> minimumGrid,
        Func<PixelSize?> fixedClientSize,
        Action resizeEnded)
    {
        _window = window;
        _sizing = sizing;
        _resizeGrid = resizeGrid;
        _minimumGrid = minimumGrid;
        _fixedClientSize = fixedClientSize;
        _resizeEnded = resizeEnded;
        _procedure = WindowProcedure;
        _procedurePointer = Marshal.GetFunctionPointerForDelegate(_procedure);
        SetWindowSubclass(_window, _procedurePointer, 1, 0);
    }

    /// <summary>Gets the window's current DPI scale (DPI / 96).</summary>
    public double Scale => GetDpiForWindow(_window) / 96.0;

    /// <summary>Stops snapping; called when the window closes.</summary>
    public void Detach() => RemoveWindowSubclass(_window, _procedurePointer, 1);

    private nint WindowProcedure(nint window, uint message, nint wParam, nint lParam, nuint id, nuint data)
    {
        switch (message)
        {
            case GetMinMaxInfoMessage:
                var result = DefSubclassProc(window, message, wParam, lParam);
                LimitTracking(lParam);
                return result;
            case SizingMessage:
                SnapToCells((int)wParam, lParam);
                return 1;
            case ExitSizeMoveMessage:
                _resizeEnded();
                break;
        }

        return DefSubclassProc(window, message, wParam, lParam);
    }

    /// <summary>Size of the window frame around the client area, in pixels.</summary>
    private PixelSize FrameSize()
    {
        GetWindowRect(_window, out var windowRect);
        GetClientRect(_window, out var clientRect);
        return new PixelSize(
            (windowRect.Right - windowRect.Left) - (clientRect.Right - clientRect.Left),
            (windowRect.Bottom - windowRect.Top) - (clientRect.Bottom - clientRect.Top));
    }

    /// <summary>
    /// Gives the window <paramref name="client"/> as its client size, keeping its position. Unlike
    /// <c>AppWindow.ResizeClient</c>, this goes through <c>WM_GETMINMAXINFO</c>, so it can go below the usual
    /// minimum width of a window (needed by the one-cell compact mode).
    /// </summary>
    public void ResizeClient(PixelSize client)
    {
        var size = WindowSize(client);
        SetWindowPos(_window, 0, 0, 0, size.Width, size.Height, ResizeOnlyFlags);
    }

    /// <summary>Gets the client area in screen pixels: what the user sees as the window.</summary>
    public PixelRect ClientBounds()
    {
        var origin = new NativePoint();
        ClientToScreen(_window, ref origin);
        GetClientRect(_window, out var client);
        return new PixelRect(origin.X, origin.Y, client.Right - client.Left, client.Bottom - client.Top);
    }

    /// <summary>Moves the window so its client area's top-left corner is at (<paramref name="x"/>, <paramref name="y"/>).</summary>
    public void MoveClientTo(int x, int y)
    {
        GetWindowRect(_window, out var windowRect);
        var client = ClientBounds();
        SetWindowPos(_window, 0, x - (client.X - windowRect.Left), y - (client.Y - windowRect.Top), 0, 0, MoveOnlyFlags);
    }

    private PixelSize WindowSize(PixelSize client)
    {
        var frame = FrameSize();
        return new PixelSize(client.Width + frame.Width, client.Height + frame.Height);
    }

    private void LimitTracking(nint lParam)
    {
        var info = Marshal.PtrToStructure<MinMaxInfo>(lParam);
        var smallest = WindowSize(_fixedClientSize() ?? _sizing.ClientSize(_minimumGrid(), Scale));
        var largest = WindowSize(_fixedClientSize() ?? _sizing.ClientSize(GridSize.Maximum, Scale));
        info.MinTrackSize = new NativePoint { X = smallest.Width, Y = smallest.Height };
        info.MaxTrackSize = new NativePoint { X = largest.Width, Y = largest.Height };
        Marshal.StructureToPtr(info, lParam, fDeleteOld: false);
    }

    private void SnapToCells(int edge, nint lParam)
    {
        var rect = Marshal.PtrToStructure<NativeRect>(lParam);
        var frame = FrameSize();
        var scale = Scale;
        var proposedClient = new PixelSize(rect.Right - rect.Left - frame.Width, rect.Bottom - rect.Top - frame.Height);
        var client = _fixedClientSize() ?? _sizing.ClientSize(_resizeGrid(_sizing.GridSizeFor(proposedClient, scale)), scale);
        var width = client.Width + frame.Width;
        var height = client.Height + frame.Height;

        if (edge is LeftEdge or TopLeftCorner or BottomLeftCorner)
        {
            rect.Left = rect.Right - width;
        }
        else
        {
            rect.Right = rect.Left + width;
        }

        if (edge is TopEdge or TopLeftCorner or TopRightCorner)
        {
            rect.Top = rect.Bottom - height;
        }
        else
        {
            rect.Bottom = rect.Top + height;
        }

        Marshal.StructureToPtr(rect, lParam, fDeleteOld: false);
    }
}
