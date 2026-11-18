using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.Core.Geometry;

/// <summary>
/// Converts between the grid and the window's client area. Cell and chrome sizes are device-independent pixels;
/// client sizes are physical pixels at <c>scale</c> (DPI / 96).
/// </summary>
/// <param name="CellSize">Size of one grid cell.</param>
/// <param name="ChromeWidth">Client width that is not grid (margins).</param>
/// <param name="ChromeHeight">Client height that is not grid (title bar, bottom bar, margins).</param>
public sealed record GridWindowSizing(double CellSize, double ChromeWidth, double ChromeHeight)
{
    /// <summary>Returns the client size that shows exactly <paramref name="grid"/>.</summary>
    public PixelSize ClientSize(GridSize grid, double scale) => new(
        (int)Math.Round(((grid.Columns * CellSize) + ChromeWidth) * scale),
        (int)Math.Round(((grid.Rows * CellSize) + ChromeHeight) * scale));

    /// <summary>Returns the grid size nearest to what fits in <paramref name="client"/>; never negative.</summary>
    public GridSize GridSizeFor(PixelSize client, double scale) => new(
        Cells(client.Height / scale, ChromeHeight),
        Cells(client.Width / scale, ChromeWidth));

    private int Cells(double length, double chrome) =>
        Math.Max(0, (int)Math.Round((length - chrome) / CellSize, MidpointRounding.AwayFromZero));
}
