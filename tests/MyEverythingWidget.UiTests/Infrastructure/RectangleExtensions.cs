using System.Drawing;

namespace MyEverythingWidget.UiTests.Infrastructure;

internal static class RectangleExtensions
{
    public static Point Center(this Rectangle rectangle) =>
        new(rectangle.Left + (rectangle.Width / 2), rectangle.Top + (rectangle.Height / 2));
}
