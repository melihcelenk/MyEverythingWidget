namespace MyEverythingWidget.Core.Geometry;

/// <summary>
/// An axis-aligned rectangle in physical screen pixels.
/// </summary>
/// <param name="X">Left edge.</param>
/// <param name="Y">Top edge.</param>
/// <param name="Width">Width; expected to be positive.</param>
/// <param name="Height">Height; expected to be positive.</param>
public readonly record struct PixelRect(int X, int Y, int Width, int Height)
{
    /// <summary>Gets the exclusive right edge.</summary>
    public int Right => X + Width;

    /// <summary>Gets the exclusive bottom edge.</summary>
    public int Bottom => Y + Height;

    /// <summary>Gets the size of the rectangle.</summary>
    public PixelSize Size => new(Width, Height);
}

/// <summary>
/// A size in physical screen pixels.
/// </summary>
/// <param name="Width">Width in pixels.</param>
/// <param name="Height">Height in pixels.</param>
public readonly record struct PixelSize(int Width, int Height);
