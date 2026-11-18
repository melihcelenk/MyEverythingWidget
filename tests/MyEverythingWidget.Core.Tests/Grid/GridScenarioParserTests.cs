using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Tests.GridDsl;

namespace MyEverythingWidget.Core.Tests.Grid;

/// <summary>
/// Checks the DSL reader itself, so a scenario failure always points at the grid rules, not at parsing.
/// </summary>
public sealed class GridScenarioParserTests
{
    private const string Sample = """
        Rows: 2
        Columns: 3

        Initial:
        N1 N1 .
        I1 .  x

        Action:
        # comment
        Create(APP, "Notepad", A1)
        Drag(N1, R2C2)
        Resize(N1, 1x1)
        Delete(I1)

        Expected:
        .  .  .
        .  .  .

        Outcome: NoRoom
        """;

    [Fact]
    public void Parse_ReadsSizeGridActionsAndOutcome()
    {
        var scenario = GridScenario.Parse("sample", Sample);

        Assert.Equal(new GridSize(2, 3), scenario.Size);
        Assert.Equal(new GridPlacement(0, 0, 2, 1), scenario.Initial["N1"]);
        Assert.Equal(new GridPlacement(1, 0, 1, 1), scenario.Initial["I1"]);
        Assert.Equal(
            [
                new CreateAction(ItemKind.App, "Notepad", "A1"),
                new DragAction("N1", new GridCell(1, 1)),
                new ResizeAction("N1", GridSpan.One),
                new DeleteAction("I1"),
            ],
            scenario.Actions);
        Assert.Empty(scenario.Expected);
        Assert.Equal(GridOutcome.NoRoom, scenario.ExpectedOutcome);
    }

    [Fact]
    public void Parse_ReadsVerticalSpan()
    {
        var scenario = GridScenario.Parse("vertical", "Rows: 2\nColumns: 1\nInitial:\nI1\nI1\nExpected:\n.\n.\n");

        Assert.Equal(new GridPlacement(0, 0, 1, 2), scenario.Initial["I1"]);
    }

    [Fact]
    public void Parse_RejectsNonRectangularItem()
    {
        const string text = "Rows: 2\nColumns: 2\nInitial:\nN1 N1\nN1 .\nExpected:\n. .\n. .\n";

        Assert.Throws<FormatException>(() => GridScenario.Parse("bad", text));
    }

    [Fact]
    public void Parse_RejectsWrongRowCount()
    {
        const string text = "Rows: 2\nColumns: 2\nInitial:\n. .\nExpected:\n. .\n. .\n";

        Assert.Throws<FormatException>(() => GridScenario.Parse("bad", text));
    }

    [Fact]
    public void Render_WritesOneLinePerRow()
    {
        var items = new Dictionary<string, GridPlacement> { ["N1"] = new(0, 1, 2, 1) };

        var text = GridScenario.Render(new GridSize(2, 3), items);

        Assert.Equal($".  N1 N1{Environment.NewLine}.  .  .{Environment.NewLine}", text);
    }
}
