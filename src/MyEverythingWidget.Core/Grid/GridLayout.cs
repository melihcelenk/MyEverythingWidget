namespace MyEverythingWidget.Core.Grid;

/// <summary>
/// Immutable placement of the items of one category on a fixed grid, with the drag-and-drop rules
/// (MEW-3 "Temel Kurallar", MEW-4 K5). Every operation returns a new layout; a rejected operation returns this one.
/// </summary>
public sealed class GridLayout
{
    private readonly Dictionary<string, GridPlacement> _items;

    /// <summary>
    /// Creates a layout; throws when a placement leaves the grid or two placements overlap.
    /// </summary>
    public GridLayout(GridSize size, IReadOnlyDictionary<string, GridPlacement> items)
    {
        ArgumentNullException.ThrowIfNull(items);

        Size = size;
        _items = new Dictionary<string, GridPlacement>(items, StringComparer.Ordinal);

        var occupied = new HashSet<GridCell>();
        foreach (var (id, placement) in _items)
        {
            if (!placement.Span.IsValid || !size.Contains(placement))
            {
                throw new ArgumentException($"Item '{id}' at {placement} does not fit a {size.Rows}x{size.Columns} grid.", nameof(items));
            }

            if (!placement.Cells.All(occupied.Add))
            {
                throw new ArgumentException($"Item '{id}' overlaps another item.", nameof(items));
            }
        }
    }

    /// <summary>Gets the grid size.</summary>
    public GridSize Size { get; }

    /// <summary>Gets the placement of every item by id.</summary>
    public IReadOnlyDictionary<string, GridPlacement> Items => _items;

    /// <summary>Returns an empty layout of <paramref name="size"/>.</summary>
    public static GridLayout Empty(GridSize size) => new(size, new Dictionary<string, GridPlacement>());

    /// <summary>Places a new item at the first free cells (reading order) where <paramref name="span"/> fits.</summary>
    public GridResult Add(string id, GridSpan span)
    {
        ArgumentException.ThrowIfNullOrEmpty(id);
        if (_items.ContainsKey(id))
        {
            throw new ArgumentException($"Item '{id}' is already on the grid.", nameof(id));
        }

        if (!span.IsValid)
        {
            return Rejected(GridOutcome.InvalidSpan);
        }

        var placement = FindFirstFree(span, OccupiedCells(exclude: []));
        return placement is { } free ? Changed(Updates((id, free))) : Rejected(GridOutcome.GridFull);
    }

    /// <summary>Drops item <paramref name="id"/> so that its top-left cell is <paramref name="target"/>.</summary>
    public GridResult Move(string id, GridCell target)
    {
        if (!_items.TryGetValue(id, out var source))
        {
            return Rejected(GridOutcome.UnknownItem);
        }

        var destination = source.MovedTo(target);
        if (!Size.Contains(destination))
        {
            return Rejected(GridOutcome.OutOfBounds);
        }

        if (destination == source)
        {
            return Changed([]);
        }

        var destinationCells = destination.Cells.ToHashSet();
        var colliders = _items
            .Where(pair => pair.Key != id && pair.Value.Cells.Any(destinationCells.Contains))
            .OrderBy(pair => pair.Value.Anchor)
            .ToList();

        var excluded = colliders.Select(pair => pair.Key).Append(id).ToHashSet(StringComparer.Ordinal);
        var occupied = OccupiedCells(excluded);
        occupied.UnionWith(destinationCells);

        var updates = new List<(string Id, GridPlacement Placement)> { (id, destination) };
        foreach (var (colliderId, colliderPlacement) in colliders)
        {
            var newPlacement = PlaceDisplaced(colliderPlacement, source.Anchor, occupied);
            if (newPlacement is null)
            {
                return Rejected(GridOutcome.NoRoom);
            }

            occupied.UnionWith(newPlacement.Value.Cells);
            updates.Add((colliderId, newPlacement.Value));
        }

        return Changed(updates);
    }

    /// <summary>Changes the span of item <paramref name="id"/>, keeping its top-left cell.</summary>
    public GridResult Resize(string id, GridSpan span)
    {
        if (!_items.TryGetValue(id, out var current))
        {
            return Rejected(GridOutcome.UnknownItem);
        }

        if (!span.IsValid)
        {
            return Rejected(GridOutcome.InvalidSpan);
        }

        var resized = current with { Span = span };
        if (!Size.Contains(resized))
        {
            return Rejected(GridOutcome.OutOfBounds);
        }

        var occupied = OccupiedCells(exclude: [id]);
        return resized.Cells.Any(occupied.Contains)
            ? Rejected(GridOutcome.NoRoom)
            : Changed(Updates((id, resized)));
    }

    /// <summary>Removes item <paramref name="id"/>; the other items keep their cells.</summary>
    public GridResult Remove(string id)
    {
        if (!_items.ContainsKey(id))
        {
            return Rejected(GridOutcome.UnknownItem);
        }

        var remaining = new Dictionary<string, GridPlacement>(_items, StringComparer.Ordinal);
        remaining.Remove(id);
        return new GridResult(GridOutcome.Success, new GridLayout(Size, remaining));
    }

    /// <summary>
    /// A displaced item goes to the dragged item's old top-left cell when it fits there (a swap);
    /// otherwise to the first free cells in reading order.
    /// </summary>
    private GridPlacement? PlaceDisplaced(GridPlacement displaced, GridCell vacatedAnchor, HashSet<GridCell> occupied)
    {
        var swapped = displaced.MovedTo(vacatedAnchor);
        return Fits(swapped, occupied) ? swapped : FindFirstFree(displaced.Span, occupied);
    }

    private GridPlacement? FindFirstFree(GridSpan span, HashSet<GridCell> occupied)
    {
        for (var row = 0; row < Size.Rows; row++)
        {
            for (var column = 0; column < Size.Columns; column++)
            {
                var candidate = new GridPlacement(new GridCell(row, column), span);
                if (Fits(candidate, occupied))
                {
                    return candidate;
                }
            }
        }

        return null;
    }

    private bool Fits(GridPlacement placement, HashSet<GridCell> occupied) =>
        Size.Contains(placement) && !placement.Cells.Any(occupied.Contains);

    private HashSet<GridCell> OccupiedCells(HashSet<string> exclude) =>
        _items.Where(pair => !exclude.Contains(pair.Key)).SelectMany(pair => pair.Value.Cells).ToHashSet();

    private static List<(string Id, GridPlacement Placement)> Updates((string Id, GridPlacement Placement) update) => [update];

    private GridResult Changed(IEnumerable<(string Id, GridPlacement Placement)> updates)
    {
        var items = new Dictionary<string, GridPlacement>(_items, StringComparer.Ordinal);
        foreach (var (id, placement) in updates)
        {
            items[id] = placement;
        }

        return new GridResult(GridOutcome.Success, new GridLayout(Size, items));
    }

    private GridResult Rejected(GridOutcome outcome) => new(outcome, this);
}
