using Windows.Foundation;
using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Sizes of the grid in device-independent pixels and conversions between cells and points.
/// </summary>
internal static class GridMetrics
{
    /// <summary>Distance between the top-left corners of two neighbouring cells.</summary>
    public const double CellSize = 80;

    /// <summary>Gap kept between a card and its cell edges.</summary>
    public const double CardInset = 3;

    /// <summary>Pointer travel that turns a press into a drag.</summary>
    public const double DragThreshold = 6;

    /// <summary>Top-left point of a cell.</summary>
    public static Point ToPoint(GridCell cell) => new(cell.Column * CellSize, cell.Row * CellSize);

    /// <summary>Area of a placement, without the card inset.</summary>
    public static Rect ToRect(GridPlacement placement) => new(
        placement.Anchor.Column * CellSize,
        placement.Anchor.Row * CellSize,
        placement.Span.Columns * CellSize,
        placement.Span.Rows * CellSize);

    /// <summary>Nearest cell to a top-left point; may be outside the grid.</summary>
    public static GridCell NearestCell(Point topLeft) =>
        new((int)Math.Round(topLeft.Y / CellSize), (int)Math.Round(topLeft.X / CellSize));

    /// <summary>Span whose size is nearest to <paramref name="width"/> x <paramref name="height"/>, clamped to 1..3.</summary>
    public static GridSpan NearestSpan(double width, double height) => new(
        Math.Clamp((int)Math.Round(width / CellSize), GridSpan.Min, GridSpan.Max),
        Math.Clamp((int)Math.Round(height / CellSize), GridSpan.Min, GridSpan.Max));
}
