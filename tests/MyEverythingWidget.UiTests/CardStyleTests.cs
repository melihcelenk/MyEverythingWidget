using System.Drawing;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Capturing;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// The resize grip's arrow and position, and card colours (MEW-4 Faz 11: R1-R4). Colours are read from the screen.
/// </summary>
public sealed class CardStyleTests : IDisposable
{
    private const string GeneralId = "c1";
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private AppSession LaunchWith(params WidgetItem[] items)
    {
        StateFiles.Save(_data, new WidgetState(WidgetState.CurrentSchemaVersion, [new Category(GeneralId, "General")], items));
        return AppSession.Launch(_data);
    }

    private static NoteItem Note() => new("N1", GeneralId, new GridPlacement(0, 0, 2, 2), "note");

    private static AutomationElement ShowGrip(AppSession app, AutomationElement card)
    {
        RealMouse.MoveTo(card.BoundingRectangle.Center());
        GridDriver.WaitForUi();
        var grip = Wait.ForElement(() => card.FindFirstDescendant(c => c.ByAutomationId("ResizeHandle")));
        GridDriver.WaitForUi();
        return grip;
    }

    private static double Brightness(Color color) => (color.R + color.G + color.B) / 3.0;

    private static Color Pixel(Bitmap screen, Rectangle box, double fx, double fy) =>
        screen.GetPixel((int)Math.Round(box.Left + (fx * (box.Width - 1))), (int)Math.Round(box.Top + (fy * (box.Height - 1))));

    /// <summary>
    /// Pixels of the grip that differ clearly from its most common colour (the badge) form the arrow; the sign of their
    /// x/y covariance tells the diagonal: positive for ↖↘ (screen y grows downwards), negative for ↗↙.
    /// </summary>
    private static (int Count, double Covariance) ArrowShape(Bitmap screen, Rectangle grip)
    {
        var pixels = new List<(int X, int Y, double Brightness)>();
        for (var y = grip.Top; y < grip.Bottom; y++)
        {
            for (var x = grip.Left; x < grip.Right; x++)
            {
                pixels.Add((x, y, Brightness(screen.GetPixel(x, y))));
            }
        }

        var badge = pixels.GroupBy(pixel => (int)(pixel.Brightness / 8)).MaxBy(group => group.Count())!.Average(pixel => pixel.Brightness);
        var arrow = pixels.Where(pixel => Math.Abs(pixel.Brightness - badge) > 60).ToList();
        if (arrow.Count == 0)
        {
            return (0, 0);
        }

        var meanX = arrow.Average(pixel => pixel.X);
        var meanY = arrow.Average(pixel => pixel.Y);
        return (arrow.Count, arrow.Average(pixel => (pixel.X - meanX) * (pixel.Y - meanY)));
    }

    [Fact]
    public void ResizeGrip_SitsInTheCardsBottomRightCorner_AndIsSmall()
    {
        using var app = LaunchWith(Note());
        var card = app.Find("Card_N1");
        var cell = app.Find("WidgetGrid").BoundingRectangle.Width / 5.0;

        var grip = ShowGrip(app, card).BoundingRectangle;
        var cardBounds = card.BoundingRectangle;

        Assert.InRange(cardBounds.Right - grip.Right, 0, 2);
        Assert.InRange(cardBounds.Bottom - grip.Bottom, 0, 2);
        Assert.True(grip.Width <= cell * 0.2, $"The grip {grip} should be small (cell {cell}).");
    }

    [Fact]
    public void ResizeGrip_ArrowPointsTopLeftToBottomRight()
    {
        using var app = LaunchWith(Note());
        var card = app.Find("Card_N1");
        var grip = ShowGrip(app, card).BoundingRectangle;

        using var screen = Capture.Screen().Bitmap;
        Capture.Element(card).ToFile(Artifacts.PathOf("resize-grip"));
        var (count, covariance) = ArrowShape(screen, grip);

        Assert.True(count >= 8, $"The grip should show an arrow ({count} arrow pixels).");
        Assert.True(covariance > 0, $"The arrow should run top-left to bottom-right (x/y covariance {covariance:F1}).");
    }

    [Fact]
    public void NoteCard_IsYellow()
    {
        using var app = LaunchWith(Note());
        var card = app.Find("Card_N1").BoundingRectangle;
        GridDriver.WaitForUi();

        using var screen = Capture.Screen().Bitmap;
        var color = Pixel(screen, card, 0.5, 0.8);

        Assert.True(color.R - color.B > 25 && color.G - color.B > 15, $"The note card should be yellow, was {color}.");
    }

    [Fact]
    public void AppCard_StandsOutFromTheSurface()
    {
        using var app = LaunchWith(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Tool", @"C:\missing\tool.exe", LaunchKind.Executable, null));
        var card = app.Find("Card_A1").BoundingRectangle;
        var grid = app.Find("WidgetGrid").BoundingRectangle;
        GridDriver.WaitForUi();

        using var screen = Capture.Screen().Bitmap;
        var cardColor = screen.GetPixel(card.Left + 6, card.Bottom - 6);
        var surface = screen.GetPixel(grid.Right - 10, grid.Bottom - 10);

        Assert.True(Math.Abs(Brightness(cardColor) - Brightness(surface)) > 12, $"The card {cardColor} should stand out from the surface {surface}.");
    }
}
