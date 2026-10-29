namespace MyEverythingWidget.Core.Grid;

/// <summary>
/// A cell of the grid; row and column are zero-based.
/// </summary>
/// <param name="Row">Zero-based row.</param>
/// <param name="Column">Zero-based column.</param>
public readonly record struct GridCell(int Row, int Column) : IComparable<GridCell>
{
    /// <summary>Orders cells in reading order: by row, then by column.</summary>
    public int CompareTo(GridCell other) =>
        Row != other.Row ? Row.CompareTo(other.Row) : Column.CompareTo(other.Column);

    /// <summary>Reading-order comparison.</summary>
    public static bool operator <(GridCell left, GridCell right) => left.CompareTo(right) < 0;

    /// <summary>Reading-order comparison.</summary>
    public static bool operator >(GridCell left, GridCell right) => left.CompareTo(right) > 0;

    /// <summary>Reading-order comparison.</summary>
    public static bool operator <=(GridCell left, GridCell right) => left.CompareTo(right) <= 0;

    /// <summary>Reading-order comparison.</summary>
    public static bool operator >=(GridCell left, GridCell right) => left.CompareTo(right) >= 0;
}

/// <summary>
/// How many columns and rows an item covers.
/// </summary>
/// <param name="Columns">Number of columns (width).</param>
/// <param name="Rows">Number of rows (height).</param>
public readonly record struct GridSpan(int Columns, int Rows)
{
    /// <summary>Smallest allowed extent in either direction.</summary>
    public const int Min = 1;

    /// <summary>Largest allowed extent in either direction.</summary>
    public const int Max = 3;

    /// <summary>A single cell.</summary>
    public static GridSpan One { get; } = new(1, 1);

    /// <summary>Gets a value indicating whether both extents are within <see cref="Min"/>..<see cref="Max"/>.</summary>
    public bool IsValid => Columns is >= Min and <= Max && Rows is >= Min and <= Max;

    /// <inheritdoc />
    public override string ToString() => $"{Columns}x{Rows}";
}

/// <summary>
/// Where an item sits: its top-left cell and its span.
/// </summary>
/// <param name="Anchor">Top-left cell.</param>
/// <param name="Span">Columns and rows covered.</param>
public readonly record struct GridPlacement(GridCell Anchor, GridSpan Span)
{
    /// <summary>Creates a placement from zero-based row/column and span.</summary>
    public GridPlacement(int row, int column, int columns, int rows)
        : this(new GridCell(row, column), new GridSpan(columns, rows))
    {
    }

    /// <summary>Gets the cells covered, in reading order.</summary>
    public IEnumerable<GridCell> Cells
    {
        get
        {
            for (var row = Anchor.Row; row < Anchor.Row + Span.Rows; row++)
            {
                for (var column = Anchor.Column; column < Anchor.Column + Span.Columns; column++)
                {
                    yield return new GridCell(row, column);
                }
            }
        }
    }

    /// <summary>Returns the same span anchored at <paramref name="anchor"/>.</summary>
    public GridPlacement MovedTo(GridCell anchor) => this with { Anchor = anchor };
}

/// <summary>
/// Number of rows and columns of a grid.
/// </summary>
/// <param name="Rows">Row count.</param>
/// <param name="Columns">Column count.</param>
public readonly record struct GridSize(int Rows, int Columns)
{
    /// <summary>The widget's grid: 5 rows by 5 columns.</summary>
    public static GridSize Default { get; } = new(5, 5);

    /// <summary>Returns whether every cell of <paramref name="placement"/> is inside the grid.</summary>
    public bool Contains(GridPlacement placement) =>
        placement.Anchor.Row >= 0
        && placement.Anchor.Column >= 0
        && placement.Anchor.Row + placement.Span.Rows <= Rows
        && placement.Anchor.Column + placement.Span.Columns <= Columns;
}

/// <summary>
/// Result of a grid operation.
/// </summary>
public enum GridOutcome
{
    /// <summary>The operation was applied.</summary>
    Success,

    /// <summary>The item would leave the grid.</summary>
    OutOfBounds,

    /// <summary>Some item could not be given a place, so nothing changed.</summary>
    NoRoom,

    /// <summary>There is no free place for a new item.</summary>
    GridFull,

    /// <summary>A span is outside 1..3 in some direction.</summary>
    InvalidSpan,

    /// <summary>No item has the given id.</summary>
    UnknownItem,
}

/// <summary>
/// Outcome of a grid operation together with the resulting layout (unchanged when the operation was rejected).
/// </summary>
/// <param name="Outcome">What happened.</param>
/// <param name="Layout">The layout after the operation.</param>
public sealed record GridResult(GridOutcome Outcome, GridLayout Layout)
{
    /// <summary>Gets a value indicating whether the operation was applied.</summary>
    public bool Succeeded => Outcome == GridOutcome.Success;
}

/// <summary>
/// Kind of widget item; decides its default span.
/// </summary>
public enum ItemKind
{
    /// <summary>An application, URL or folder shortcut.</summary>
    App,

    /// <summary>A text note.</summary>
    Note,

    /// <summary>An image.</summary>
    Image,
}

/// <summary>
/// Default spans of new items.
/// </summary>
public static class DefaultSpans
{
    /// <summary>Returns the span a new item of <paramref name="kind"/> gets: apps 1x1, notes 2x1, images 2x2.</summary>
    public static GridSpan For(ItemKind kind) => kind switch
    {
        ItemKind.App => GridSpan.One,
        ItemKind.Note => new GridSpan(2, 1),
        ItemKind.Image => new GridSpan(2, 2),
        _ => throw new ArgumentOutOfRangeException(nameof(kind), kind, "Unknown item kind."),
    };
}
