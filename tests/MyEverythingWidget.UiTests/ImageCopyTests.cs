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
}
