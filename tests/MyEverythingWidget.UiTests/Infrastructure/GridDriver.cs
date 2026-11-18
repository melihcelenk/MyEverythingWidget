using System.Drawing;
using FlaUI.Core.AutomationElements;
using MyEverythingWidget.Core.Grid;
using GridCell = MyEverythingWidget.Core.Grid.GridCell;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Drives the widget grid with the real mouse, in screen pixels derived from the grid's bounding rectangle,
/// so the tests work at any DPI.
/// </summary>
internal sealed class GridDriver(AppSession app, GridSize size)
{
    private const int MoveSteps = 12;
    private static readonly TimeSpan StepDelay = TimeSpan.FromMilliseconds(15);
    private static readonly TimeSpan SettleDelay = TimeSpan.FromMilliseconds(450);

    private Rectangle GridBounds => app.Find("WidgetGrid").BoundingRectangle;

    /// <summary>Gets the size of one cell in screen pixels.</summary>
    public double Pitch => GridBounds.Width / (double)size.Columns;

    public AutomationElement Card(string itemId) => app.Find("Card_" + itemId);

    /// <summary>Returns the cell under the top-left corner of the item's card.</summary>
    public GridCell AnchorOf(string itemId)
    {
        var card = Card(itemId).BoundingRectangle;
        var grid = GridBounds;
        return new GridCell(
            (int)Math.Round((card.Top - grid.Top) / Pitch),
            (int)Math.Round((card.Left - grid.Left) / Pitch));
    }

    public Point CellCenter(GridCell cell)
    {
        var grid = GridBounds;
        return new Point(
            (int)Math.Round(grid.Left + ((cell.Column + 0.5) * Pitch)),
            (int)Math.Round(grid.Top + ((cell.Row + 0.5) * Pitch)));
    }

    /// <summary>Grabs the item at the centre of its top-left cell and drops it with that cell on <paramref name="target"/>.</summary>
    public void Drag(string itemId, GridCell target)
    {
        var start = CellCenter(AnchorOf(itemId));
        var end = CellCenter(target);
        Press(start);
        MoveSmoothly(start, end);
        Release();
    }

    public static void Press(Point point)
    {
        RealMouse.MoveTo(point);
        Thread.Sleep(StepDelay);
        RealMouse.LeftDown();
        Thread.Sleep(StepDelay);
    }

    public static void MoveSmoothly(Point from, Point to)
    {
        for (var step = 1; step <= MoveSteps; step++)
        {
            RealMouse.MoveTo(new Point(
                from.X + ((to.X - from.X) * step / MoveSteps),
                from.Y + ((to.Y - from.Y) * step / MoveSteps)));
            Thread.Sleep(StepDelay);
        }
    }

    /// <summary>Lets the app process the last pointer moves and render before something is measured.</summary>
    public static void WaitForUi() => Thread.Sleep(SettleDelay);

    public static void Release()
    {
        RealMouse.LeftUp();
        Thread.Sleep(SettleDelay);
    }
}
