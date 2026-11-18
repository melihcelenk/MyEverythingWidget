using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>An image card knows the image's pixel size, so the viewer can open at the right shape.</summary>
public sealed class ImageItemViewModelTests
{
    [Fact]
    public void ImageCard_ExposesPixelSize()
    {
        var item = new GridItemViewModel(new ImageItem("i1", "c1", new GridPlacement(0, 0, 2, 1), @"images\a.png", 1200, 600));

        Assert.Equal((1200, 600), (item.ImagePixelWidth, item.ImagePixelHeight));
    }
}
