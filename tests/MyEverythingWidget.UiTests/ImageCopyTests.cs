using System.Drawing;
using System.Drawing.Imaging;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Input;
using FlaUI.Core.WindowsAPI;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Copying an image card's picture to the clipboard (MEW-4 Faz 15: K1-K3).
/// </summary>
public sealed class ImageCopyTests : IDisposable
{
    private const string GeneralId = "c1";
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private AppSession LaunchWithImage()
    {
        var imagesFolder = Path.Combine(_data.Path, "images");
        Directory.CreateDirectory(imagesFolder);
        using (var bitmap = new Bitmap(400, 200))
        {
            using (var graphics = Graphics.FromImage(bitmap))
            {
                graphics.Clear(Color.SeaGreen);
            }

            bitmap.Save(Path.Combine(imagesFolder, "photo.png"), ImageFormat.Png);
        }

        StateFiles.Save(_data, new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category(GeneralId, "General")],
            [new ImageItem("I1", GeneralId, new GridPlacement(0, 0, 2, 1), @"images\photo.png", 400, 200)]));
        SandboxClipboard.SetText("nothing yet");
        return AppSession.Launch(_data);
    }

    [Fact]
    public void CopyButton_OnImageCard_PutsThePictureOnTheClipboard()
    {
        using var app = LaunchWithImage();
        var card = app.Find("Card_I1");
        RealMouse.MoveTo(card.BoundingRectangle.Center());
        GridDriver.WaitForUi();

        var copy = Wait.ForElement(() => card.FindFirstDescendant(c => c.ByAutomationId("CopyImageButton")));
        RealMouse.Click(copy.BoundingRectangle.Center());

        Assert.True(Wait.Until(SandboxClipboard.HasPicture), "The clipboard should hold the picture.");
        Assert.Null(app.FindWindow("photo.png"));
    }

    [Fact]
    public void CopyImageMenuItem_PutsThePictureOnTheClipboard()
    {
        using var app = LaunchWithImage();
        GridDriver.WaitForUi();
        RealMouse.RightClick(app.Find("Card_I1").BoundingRectangle.Center());

        Wait.ForElement(() => app.FindInPopups("CopyImageMenuItem")).AsMenuItem().Invoke();

        Assert.True(Wait.Until(SandboxClipboard.HasPicture), "The clipboard should hold the picture.");
    }

    [Fact]
    public void CtrlC_InTheViewer_PutsThePictureOnTheClipboard()
    {
        using var app = LaunchWithImage();
        RealMouse.Click(app.Find("Card_I1").BoundingRectangle.Center());
        Assert.True(Wait.Until(() => app.FindWindow("photo.png") is not null), "The viewer should open.");
        GridDriver.WaitForUi();

        Keyboard.TypeSimultaneously(VirtualKeyShort.CONTROL, VirtualKeyShort.KEY_C);

        Assert.True(Wait.Until(SandboxClipboard.HasPicture), "The clipboard should hold the picture.");
    }

    [Fact]
    public void CopyButton_ShowsThatTheImageWasCopied()
    {
        using var app = LaunchWithImage();
        var card = app.Find("Card_I1");
        RealMouse.MoveTo(card.BoundingRectangle.Center());
        GridDriver.WaitForUi();
        var copy = Wait.ForElement(() => card.FindFirstDescendant(c => c.ByAutomationId("CopyImageButton")));

        RealMouse.Click(copy.BoundingRectangle.Center());

        Assert.True(Wait.Until(() => copy.Name == "Copied", TimeSpan.FromSeconds(1)), $"The button should say it copied; it says '{copy.Name}'.");
        Assert.True(Wait.Until(() => copy.Name == "Copy image", TimeSpan.FromSeconds(4)), "The button should go back to normal after a moment.");
    }

    [Fact]
    public void CopyImageMenuItem_ShowsThatTheImageWasCopied()
    {
        using var app = LaunchWithImage();
        GridDriver.WaitForUi();
        RealMouse.RightClick(app.Find("Card_I1").BoundingRectangle.Center());

        Wait.ForElement(() => app.FindInPopups("CopyImageMenuItem")).AsMenuItem().Invoke();

        var copy = Wait.ForElement(() => app.Find("Card_I1").FindFirstDescendant(c => c.ByAutomationId("CopyImageButton")));
        Assert.True(Wait.Until(() => copy.Name == "Copied" && !copy.IsOffscreen, TimeSpan.FromSeconds(1)), "The card should show that the image was copied.");
    }

    [Fact]
    public void ViewerContextMenu_CopiesAndSaysSo()
    {
        using var app = LaunchWithImage();
        RealMouse.Click(app.Find("Card_I1").BoundingRectangle.Center());
        var viewer = Wait.ForElement(() => app.FindWindow("photo.png"));
        GridDriver.WaitForUi();

        RealMouse.RightClick(viewer.BoundingRectangle.Center());
        var copy = Wait.ForElement(() => viewer.FindFirstDescendant(c => c.ByAutomationId("ViewerCopyMenuItem")) ?? app.FindInPopups("ViewerCopyMenuItem"));
        Assert.NotNull(viewer.FindFirstDescendant(c => c.ByAutomationId("ViewerEditMenuItem")) ?? app.FindInPopups("ViewerEditMenuItem"));
        copy.AsMenuItem().Invoke();

        // The notice shows for 1.5 s; the clipboard check starts PowerShell, which can take longer in the sandbox.
        Assert.NotNull(Wait.ForElement(() => viewer.FindFirstDescendant(c => c.ByAutomationId("ViewerCopiedNotice"))));
        Assert.True(Wait.Until(SandboxClipboard.HasPicture), "The clipboard should hold the picture.");
        Assert.NotNull(app.FindWindow("photo.png"));
    }

    [Fact]
    public void ImageChangedOutside_IsShownWhenTheWidgetIsActivatedAgain()
    {
        using var app = LaunchWithImage();
        var card = app.Find("Card_I1").BoundingRectangle;
        Assert.True(Wait.Until(() => IsGreenish(PixelAt(card))), "The card should first show the green picture.");

        using (var bitmap = new Bitmap(400, 200))
        {
            using (var graphics = Graphics.FromImage(bitmap))
            {
                graphics.Clear(Color.Crimson);
            }

            bitmap.Save(Path.Combine(_data.Path, "images", "photo.png"), ImageFormat.Png);
        }

        var window = Win32.GetBounds(app.WindowHandle);
        RealMouse.Click(new Point(Math.Max(window.Left - 60, 5), window.Top + 60));
        GridDriver.WaitForUi();
        RealMouse.Click(new Point(window.Right - 120, window.Top + 18));
        card = app.Find("Card_I1").BoundingRectangle;

        Assert.True(Wait.Until(() => IsReddish(PixelAt(card)), TimeSpan.FromSeconds(5)), $"The card should show the edited picture, shows {PixelAt(card)}.");
    }

    [Fact]
    public void EditInPaint_IsOfferedForImageCards()
    {
        using var app = LaunchWithImage();
        GridDriver.WaitForUi();
        RealMouse.RightClick(app.Find("Card_I1").BoundingRectangle.Center());

        Assert.NotNull(Wait.ForElement(() => app.FindInPopups("EditImageMenuItem")));
    }

    private static Color PixelAt(Rectangle card)
    {
        using var screen = FlaUI.Core.Capturing.Capture.Screen().Bitmap;
        return screen.GetPixel(card.Left + (card.Width / 2), card.Top + (card.Height / 2));
    }

    private static bool IsGreenish(Color color) => color.G > color.R + 40;

    private static bool IsReddish(Color color) => color.R > color.G + 60;
}
