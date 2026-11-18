namespace MyEverythingWidget.Core.Geometry;

/// <summary>
/// One of the four corners of a rectangle.
/// </summary>
/// <param name="Right">The right-hand corner; otherwise the left-hand one.</param>
/// <param name="Bottom">The bottom corner; otherwise the top one.</param>
public readonly record struct WindowCorner(bool Right, bool Bottom);
