using System.Drawing;
using System.Drawing.Imaging;
using FlaUI.Core.Input;
using FlaUI.Core.WindowsAPI;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Clicking an image card shows the image large (MEW-4 Faz 12: V1-V3).
/// </summary>
public sealed class ImageViewerTests : IDisposable
{
    private const string GeneralId = "c1";
    private const int ImageWidth = 1200;
    private const int ImageHeight = 600;
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    /// <summary>The viewer is its own window, titled with the file name; elements are searched inside it.</summary>
    private static FlaUI.Core.AutomationElements.AutomationElement Viewer(AppSession app, string automationId)
    {
        FlaUI.Core.AutomationElements.AutomationElement? found = null;
        var appeared = Wait.Until(() => (found = app.FindWindow("wide.png")?.FindFirstDescendant(c => c.ByAutomationId(automationId))) is not null);
        Assert.True(appeared, $"'{automationId}' not found in the viewer; windows: {app.DescribeWindows()}");
        return found!;
    }

    private AppSession LaunchWithImage()
    {
        var imagesFolder = Path.Combine(_data.Path, "images");
        Directory.CreateDirectory(imagesFolder);
        using (var bitmap = new Bitmap(ImageWidth, ImageHeight))
        {
            using (var graphics = Graphics.FromImage(bitmap))
            {
                graphics.Clear(Color.SteelBlue);
            }

            bitmap.Save(Path.Combine(imagesFolder, "wide.png"), ImageFormat.Png);
        }

        StateFiles.Save(_data, new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category(GeneralId, "General")],
            [new ImageItem("I1", GeneralId, new GridPlacement(0, 0, 2, 1), @"images\wide.png", ImageWidth, ImageHeight)]));
        return AppSession.Launch(_data);
    }

    [Fact]
    public void ClickingImageCard_ShowsTheImageLarge()
    {
        using var app = LaunchWithImage();
        var card = app.Find("Card_I1").BoundingRectangle;

        RealMouse.Click(card.Center());
        GridDriver.WaitForUi();
        Artifacts.CaptureScreen("image-viewer");

        var viewerImage = Viewer(app, "ViewerImage");
        Assert.True(Wait.Until(() => viewerImage.BoundingRectangle.Width > card.Width * 2), $"The image {viewerImage.BoundingRectangle} should be much larger than the card {card}.");
        var shown = viewerImage.BoundingRectangle;
        Assert.InRange(shown.Width / (double)shown.Height, 1.9, 2.1);
    }

    [Fact]
    public void Viewer_FitsOnTheScreen()
    {
        using var app = LaunchWithImage();
        RealMouse.Click(app.Find("Card_I1").BoundingRectangle.Center());

        var viewer = Viewer(app, "ImageViewer");
        var work = Win32.WorkAreaOf(app.WindowHandle);

        Assert.True(Wait.Until(() => work.Contains(viewer.BoundingRectangle)), $"The viewer {viewer.BoundingRectangle} should fit in {work}.");
    }

    [Fact]
    public void Escape_ClosesTheViewer()
    {
        using var app = LaunchWithImage();
        RealMouse.Click(app.Find("Card_I1").BoundingRectangle.Center());
        Viewer(app, "ViewerImage");
        GridDriver.WaitForUi();

        Keyboard.Press(VirtualKeyShort.ESCAPE);

        Assert.True(Wait.Until(() => app.FindWindow("wide.png") is null), "Escape should close the viewer.");
        Assert.False(app.HasExited, "Closing the viewer should not close the widget.");
    }
}
