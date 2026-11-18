namespace MyEverythingWidget.Core.Grid;

/// <summary>
/// Chooses how many cells an image card covers from the image's aspect ratio (width / height).
/// </summary>
public static class ImageSpan
{
    private const double PanoramaRatio = 2.5;
    private const double WideRatio = 1.5;
    private const double LandscapeRatio = 1.1;
    private const double SquareRatio = 0.9;
    private const double PortraitRatio = 0.5;

    /// <summary>
    /// Returns 3x1 for panoramas (≥ 2.5), 3x2 for wide images such as 16:9 (≥ 1.5), 2x1 for 4:3 (≥ 1.1),
    /// 2x2 for squares (≥ 0.9), 1x2 for portraits (≥ 0.5) and 1x3 for very tall images. Unknown sizes get 1x1.
    /// </summary>
    public static GridSpan FromPixelSize(int width, int height)
    {
        if (width <= 0 || height <= 0)
        {
            return GridSpan.One;
        }

        var ratio = (double)width / height;
        return ratio switch
        {
            >= PanoramaRatio => new GridSpan(3, 1),
            >= WideRatio => new GridSpan(3, 2),
            >= LandscapeRatio => new GridSpan(2, 1),
            >= SquareRatio => new GridSpan(2, 2),
            >= PortraitRatio => new GridSpan(1, 2),
            _ => new GridSpan(1, 3),
        };
    }
}
