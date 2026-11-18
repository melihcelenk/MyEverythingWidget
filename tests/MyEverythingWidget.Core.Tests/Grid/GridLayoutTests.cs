using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.Core.Tests.Grid;

public sealed class GridLayoutTests
{
    private static readonly GridSize Size = new(3, 3);

    [Fact]
    public void Constructor_RejectsPlacementOutsideGrid()
    {
        var items = new Dictionary<string, GridPlacement> { ["N1"] = new(0, 2, 2, 1) };

        Assert.Throws<ArgumentException>(() => new GridLayout(Size, items));
    }

    [Fact]
    public void Constructor_RejectsOverlappingPlacements()
    {
        var items = new Dictionary<string, GridPlacement>
        {
            ["N1"] = new(0, 0, 2, 1),
            ["A1"] = new(0, 1, 1, 1),
        };

        Assert.Throws<ArgumentException>(() => new GridLayout(Size, items));
    }

    [Fact]
    public void Constructor_CopiesItems()
    {
        var items = new Dictionary<string, GridPlacement> { ["A1"] = new(0, 0, 1, 1) };
        var layout = new GridLayout(Size, items);

        items["A2"] = new GridPlacement(1, 1, 1, 1);

        Assert.Single(layout.Items);
    }

    [Fact]
    public void Move_UnknownItem_ReturnsUnknownItemAndSameLayout()
    {
        var layout = GridLayout.Empty(Size);

        var result = layout.Move("A1", new GridCell(0, 0));

        Assert.Equal(GridOutcome.UnknownItem, result.Outcome);
        Assert.Same(layout, result.Layout);
    }

    [Fact]
    public void Add_ExistingId_Throws()
    {
        var layout = GridLayout.Empty(Size).Add("A1", GridSpan.One).Layout;

        Assert.Throws<ArgumentException>(() => layout.Add("A1", GridSpan.One));
    }

    [Fact]
    public void Add_InvalidSpan_ReturnsInvalidSpan()
    {
        var result = GridLayout.Empty(Size).Add("N1", new GridSpan(0, 1));

        Assert.Equal(GridOutcome.InvalidSpan, result.Outcome);
    }

    [Fact]
    public void Move_ToSameCell_SucceedsWithoutChange()
    {
        var layout = GridLayout.Empty(Size).Add("A1", GridSpan.One).Layout;

        var result = layout.Move("A1", new GridCell(0, 0));

        Assert.True(result.Succeeded);
        Assert.Equal(new GridPlacement(0, 0, 1, 1), result.Layout.Items["A1"]);
    }

    [Fact]
    public void Operations_DoNotChangeOriginalLayout()
    {
        var layout = GridLayout.Empty(Size).Add("A1", GridSpan.One).Layout;

        _ = layout.Move("A1", new GridCell(2, 2));

        Assert.Equal(new GridPlacement(0, 0, 1, 1), layout.Items["A1"]);
    }

    [Fact]
    public void FirstFree_UsesReadingOrder()
    {
        var layout = new GridLayout(Size, new Dictionary<string, GridPlacement> { ["A1"] = new(0, 0, 1, 1) });

        var result = layout.Add("A2", GridSpan.One);

        Assert.Equal(new GridPlacement(0, 1, 1, 1), result.Layout.Items["A2"]);
    }
}
