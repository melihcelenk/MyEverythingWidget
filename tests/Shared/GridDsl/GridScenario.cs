using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;
using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.Tests.GridDsl;

/// <summary>An action of a grid scenario.</summary>
public abstract record GridAction;

/// <summary><c>Create(NOTE|APP, "text", ID)</c>: adds a new item at the first free place.</summary>
public sealed record CreateAction(ItemKind Kind, string Text, string Id) : GridAction;

/// <summary><c>Drag(ID, RrCc)</c>: drops the item with its top-left cell at the target.</summary>
public sealed record DragAction(string Id, GridCell Target) : GridAction;

/// <summary><c>Resize(ID, CxR)</c>: changes the span (columns x rows).</summary>
public sealed record ResizeAction(string Id, GridSpan Span) : GridAction;

/// <summary><c>Delete(ID)</c>: removes the item.</summary>
public sealed record DeleteAction(string Id) : GridAction;

/// <summary>
/// A grid behaviour scenario read from a <c>.dsl</c> file (format: MEW-4 PHASE2.md, "DSL biçimi").
/// Positions in the file are one-based; the parsed values are zero-based.
/// </summary>
public sealed partial class GridScenario
{
    private const string EmptyToken = ".";
    private const string AlternativeEmptyToken = "x";

    private GridScenario(
        string name,
        GridSize size,
        IReadOnlyDictionary<string, GridPlacement> initial,
        IReadOnlyList<GridAction> actions,
        IReadOnlyDictionary<string, GridPlacement> expected,
        GridOutcome? expectedOutcome)
    {
        Name = name;
        Size = size;
        Initial = initial;
        Actions = actions;
        Expected = expected;
        ExpectedOutcome = expectedOutcome;
    }

    /// <summary>Gets the file name without extension.</summary>
    public string Name { get; }

    /// <summary>Gets the grid size.</summary>
    public GridSize Size { get; }

    /// <summary>Gets the items before the actions.</summary>
    public IReadOnlyDictionary<string, GridPlacement> Initial { get; }

    /// <summary>Gets the actions in order.</summary>
    public IReadOnlyList<GridAction> Actions { get; }

    /// <summary>Gets the items expected after the actions.</summary>
    public IReadOnlyDictionary<string, GridPlacement> Expected { get; }

    /// <summary>Gets the expected outcome of the last action, when the file states one.</summary>
    public GridOutcome? ExpectedOutcome { get; }

    /// <summary>Reads and parses a scenario file.</summary>
    public static GridScenario Load(string path) =>
        Parse(Path.GetFileNameWithoutExtension(path), File.ReadAllText(path));

    /// <summary>Parses scenario text; throws <see cref="FormatException"/> with the line number on bad input.</summary>
    public static GridScenario Parse(string name, string text)
    {
        ArgumentNullException.ThrowIfNull(text);

        int? rows = null;
        int? columns = null;
        var initialLines = new List<string>();
        var expectedLines = new List<string>();
        var actions = new List<GridAction>();
        GridOutcome? outcome = null;
        var section = "";

        var lineNumber = 0;
        foreach (var rawLine in text.Split('\n'))
        {
            lineNumber++;
            var line = rawLine.Trim();
            if (line.Length == 0 || line.StartsWith('#'))
            {
                continue;
            }

            if (TryReadHeader(line, "Rows", out var value))
            {
                rows = ParseInt(value, lineNumber);
            }
            else if (TryReadHeader(line, "Columns", out value))
            {
                columns = ParseInt(value, lineNumber);
            }
            else if (TryReadHeader(line, "Outcome", out value))
            {
                outcome = Enum.Parse<GridOutcome>(value, ignoreCase: false);
            }
            else if (line is "Initial:" or "Action:" or "Expected:")
            {
                section = line.TrimEnd(':');
            }
            else if (section == "Initial")
            {
                initialLines.Add(line);
            }
            else if (section == "Expected")
            {
                expectedLines.Add(line);
            }
            else if (section == "Action")
            {
                actions.Add(ParseAction(line, lineNumber));
            }
            else
            {
                throw new FormatException($"{name}:{lineNumber}: unexpected line '{line}'.");
            }
        }

        var size = new GridSize(
            rows ?? throw new FormatException($"{name}: missing 'Rows:'."),
            columns ?? throw new FormatException($"{name}: missing 'Columns:'."));

        return new GridScenario(
            name,
            size,
            ParseGrid(name, "Initial", initialLines, size),
            actions,
            ParseGrid(name, "Expected", expectedLines, size),
            outcome);
    }

    /// <summary>Renders placements as scenario grid text, one row per line, so failures read like the file.</summary>
    public static string Render(GridSize size, IReadOnlyDictionary<string, GridPlacement> items)
    {
        ArgumentNullException.ThrowIfNull(items);

        var cells = new string[size.Rows, size.Columns];
        foreach (var (id, placement) in items)
        {
            foreach (var cell in placement.Cells)
            {
                if (cell.Row < size.Rows && cell.Column < size.Columns)
                {
                    cells[cell.Row, cell.Column] = id;
                }
            }
        }

        var width = Math.Max(2, items.Keys.Select(id => id.Length).DefaultIfEmpty(1).Max());
        var builder = new StringBuilder();
        for (var row = 0; row < size.Rows; row++)
        {
            var tokens = Enumerable.Range(0, size.Columns).Select(column => (cells[row, column] ?? EmptyToken).PadRight(width));
            builder.AppendLine(string.Join(' ', tokens).TrimEnd());
        }

        return builder.ToString();
    }

    private static bool TryReadHeader(string line, string header, out string value)
    {
        var prefix = header + ":";
        if (line.StartsWith(prefix, StringComparison.Ordinal) && line.Length > prefix.Length)
        {
            value = line[prefix.Length..].Trim();
            return true;
        }

        value = "";
        return false;
    }

    private static int ParseInt(string value, int lineNumber) =>
        int.TryParse(value, NumberStyles.None, CultureInfo.InvariantCulture, out var number)
            ? number
            : throw new FormatException($"Line {lineNumber}: '{value}' is not a number.");

    private static GridAction ParseAction(string line, int lineNumber)
    {
        if (CreatePattern().Match(line) is { Success: true } create)
        {
            var kind = create.Groups["kind"].Value switch
            {
                "NOTE" => ItemKind.Note,
                "APP" => ItemKind.App,
                "IMAGE" => ItemKind.Image,
                var other => throw new FormatException($"Line {lineNumber}: unknown item kind '{other}'."),
            };
            return new CreateAction(kind, create.Groups["text"].Value, create.Groups["id"].Value);
        }

        if (DragPattern().Match(line) is { Success: true } drag)
        {
            var row = ParseInt(drag.Groups["row"].Value, lineNumber) - 1;
            var column = ParseInt(drag.Groups["column"].Value, lineNumber) - 1;
            return new DragAction(drag.Groups["id"].Value, new GridCell(row, column));
        }

        if (ResizePattern().Match(line) is { Success: true } resize)
        {
            var span = new GridSpan(
                ParseInt(resize.Groups["columns"].Value, lineNumber),
                ParseInt(resize.Groups["rows"].Value, lineNumber));
            return new ResizeAction(resize.Groups["id"].Value, span);
        }

        if (DeletePattern().Match(line) is { Success: true } delete)
        {
            return new DeleteAction(delete.Groups["id"].Value);
        }

        throw new FormatException($"Line {lineNumber}: unknown action '{line}'.");
    }

    private static Dictionary<string, GridPlacement> ParseGrid(string name, string section, List<string> lines, GridSize size)
    {
        if (lines.Count != size.Rows)
        {
            throw new FormatException($"{name}: '{section}' has {lines.Count} rows, expected {size.Rows}.");
        }

        var cellsById = new Dictionary<string, List<GridCell>>();
        for (var row = 0; row < lines.Count; row++)
        {
            var tokens = lines[row].Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries);
            if (tokens.Length != size.Columns)
            {
                throw new FormatException($"{name}: '{section}' row {row + 1} has {tokens.Length} cells, expected {size.Columns}.");
            }

            for (var column = 0; column < tokens.Length; column++)
            {
                if (tokens[column] is EmptyToken or AlternativeEmptyToken)
                {
                    continue;
                }

                if (!cellsById.TryGetValue(tokens[column], out var cells))
                {
                    cells = [];
                    cellsById[tokens[column]] = cells;
                }

                cells.Add(new GridCell(row, column));
            }
        }

        return cellsById.ToDictionary(pair => pair.Key, pair => ToPlacement(name, section, pair.Key, pair.Value));
    }

    private static GridPlacement ToPlacement(string name, string section, string id, List<GridCell> cells)
    {
        var top = cells.Min(cell => cell.Row);
        var left = cells.Min(cell => cell.Column);
        var bottom = cells.Max(cell => cell.Row);
        var right = cells.Max(cell => cell.Column);
        var placement = new GridPlacement(top, left, right - left + 1, bottom - top + 1);

        if (placement.Cells.Count() != cells.Count)
        {
            throw new FormatException($"{name}: '{section}' item {id} does not fill a rectangle.");
        }

        return placement;
    }

    [GeneratedRegex("""^Create\(\s*(?<kind>[A-Z]+)\s*,\s*"(?<text>[^"]*)"\s*,\s*(?<id>\w+)\s*\)$""")]
    private static partial Regex CreatePattern();

    [GeneratedRegex(@"^Drag\(\s*(?<id>\w+)\s*,\s*R(?<row>\d+)C(?<column>\d+)\s*\)$")]
    private static partial Regex DragPattern();

    [GeneratedRegex(@"^Resize\(\s*(?<id>\w+)\s*,\s*(?<columns>\d+)x(?<rows>\d+)\s*\)$")]
    private static partial Regex ResizePattern();

    [GeneratedRegex(@"^Delete\(\s*(?<id>\w+)\s*\)$")]
    private static partial Regex DeletePattern();
}
