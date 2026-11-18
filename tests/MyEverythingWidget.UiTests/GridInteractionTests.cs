using FlaUI.Core.AutomationElements;
using MyEverythingWidget.Core.Grid;
using GridCell = MyEverythingWidget.Core.Grid.GridCell;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;
using MyEverythingWidget.Tests.GridDsl;
using MyEverythingWidget.UiTests.Infrastructure;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Drag-and-drop and resize with the real mouse (MEW-4 Faz 3, acceptance criteria G1-G8, G10).
/// </summary>
public sealed class GridInteractionTests : IDisposable
{
    private static readonly string ScenarioDirectory = Path.Combine(AppContext.BaseDirectory, "Grid");
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    /// <summary>Every 5x5 scenario made only of drags can be replayed in the real app.</summary>
    public static TheoryData<string> DragScenarios()
    {
        var data = new TheoryData<string>();
        foreach (var file in Directory.GetFiles(ScenarioDirectory, "*.dsl").Order(StringComparer.Ordinal))
        {
            var scenario = GridScenario.Load(file);
            if (scenario.Size == GridSize.Default && scenario.Actions.Count > 0 && scenario.Actions.All(action => action is DragAction))
            {
                data.Add(Path.GetFileName(file));
            }
        }

        return data;
    }

    [Theory]
    [MemberData(nameof(DragScenarios))]
    public void Scenario_ReplayedWithRealMouse_ProducesExpectedGrid(string fileName)
    {
        var scenario = GridScenario.Load(Path.Combine(ScenarioDirectory, fileName));
        StateFiles.Seed(_data, scenario.Initial);

        using (var app = AppSession.Launch(_data))
        {
            var grid = new GridDriver(app, scenario.Size);
            foreach (var drag in scenario.Actions.Cast<DragAction>())
            {
                grid.Drag(drag.Id, drag.Target);
            }

            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal(
            GridScenario.Render(scenario.Size, scenario.Expected),
            GridScenario.Render(scenario.Size, StateFiles.ReadPlacements(_data)));
    }

    [Fact]
    public void DraggedNote_KeepsItsSizeFollowsPointerAndHighlightsTwoCells()
    {
        StateFiles.Seed(_data, new Dictionary<string, GridPlacement> { ["N1"] = new(1, 0, 2, 1) });
        using var app = AppSession.Launch(_data);
        var grid = new GridDriver(app, GridSize.Default);
        var before = grid.Card("N1").BoundingRectangle;
        var start = grid.CellCenter(new GridCell(1, 0));
        var grabOffset = new System.Drawing.Size(start.X - before.Left, start.Y - before.Top);
        var end = grid.CellCenter(new GridCell(3, 2));

        GridDriver.Press(start);
        GridDriver.MoveSmoothly(start, end);
        GridDriver.WaitForUi();
        var during = grid.Card("N1").BoundingRectangle;
        var preview = app.Find("DropPreview");
        var previewBounds = preview.BoundingRectangle;
        var previewHelp = preview.HelpText;
        GridDriver.Release();

        Assert.InRange(during.Width, before.Width - 2, before.Width + 2);
        Assert.InRange(during.Height, before.Height - 2, before.Height + 2);
        Assert.InRange(end.X - during.Left, grabOffset.Width - 3, grabOffset.Width + 3);
        Assert.InRange(end.Y - during.Top, grabOffset.Height - 3, grabOffset.Height + 3);
        Assert.InRange(previewBounds.Width, (2 * grid.Pitch) - 10, 2 * grid.Pitch);
        Assert.InRange(previewBounds.Height, grid.Pitch - 10, grid.Pitch);
        Assert.Equal("allowed", previewHelp);
    }

    [Fact]
    public void DraggingPastEdge_ShowsNotAllowedAndSnapsBack()
    {
        StateFiles.Seed(_data, new Dictionary<string, GridPlacement> { ["N1"] = new(0, 0, 2, 1) });
        using (var app = AppSession.Launch(_data))
        {
            var grid = new GridDriver(app, GridSize.Default);
            var start = grid.CellCenter(new GridCell(0, 0));
            var end = grid.CellCenter(new GridCell(2, 4));

            GridDriver.Press(start);
            GridDriver.MoveSmoothly(start, end);
            var previewHelp = app.Find("DropPreview").HelpText;
            GridDriver.Release();

            Assert.Equal("not allowed", previewHelp);
            Assert.Equal(new GridCell(0, 0), grid.AnchorOf("N1"));
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal(new GridPlacement(0, 0, 2, 1), StateFiles.ReadPlacements(_data)["N1"]);
    }

    [Fact]
    public void DraggingResizeHandle_GrowsNoteByOneColumn()
    {
        StateFiles.Seed(_data, new Dictionary<string, GridPlacement> { ["N1"] = new(0, 0, 2, 1) });
        using (var app = AppSession.Launch(_data))
        {
            var grid = new GridDriver(app, GridSize.Default);
            var card = grid.Card("N1");
            RealMouse.MoveTo(card.BoundingRectangle.Center());
            Thread.Sleep(200);
            var handle = card.FindFirstDescendant(condition => condition.ByAutomationId("ResizeHandle"))
                ?? throw new InvalidOperationException("Resize handle not found.");
            var start = handle.BoundingRectangle.Center();
            var end = new System.Drawing.Point(start.X + (int)Math.Round(grid.Pitch), start.Y);

            GridDriver.Press(start);
            GridDriver.MoveSmoothly(start, end);
            GridDriver.Release();
            app.ClickCloseAndWaitForExit();
        }

        Assert.Equal(new GridPlacement(0, 0, 3, 1), StateFiles.ReadPlacements(_data)["N1"]);
    }

    [Fact]
    public void ContextMenuDelete_RemovesOnlyThatCard()
    {
        StateFiles.Seed(_data, new Dictionary<string, GridPlacement>
        {
            ["A1"] = new(0, 0, 1, 1),
            ["A2"] = new(0, 1, 1, 1),
        });
        using (var app = AppSession.Launch(_data))
        {
            var grid = new GridDriver(app, GridSize.Default);
            RealMouse.RightClick(grid.Card("A1").BoundingRectangle.Center());
            var delete = Wait.ForElement(() => app.FindInPopups("DeleteItemMenuItem"));
            delete.AsMenuItem().Invoke();
            Assert.True(Wait.Until(() => app.TryFind("Card_A1") is null), "Card A1 should disappear.");
            app.ClickCloseAndWaitForExit();
        }

        var placements = StateFiles.ReadPlacements(_data);
        Assert.False(placements.ContainsKey("A1"));
        Assert.Equal(new GridPlacement(0, 1, 1, 1), placements["A2"]);
    }

    [Fact]
    public void CorruptState_ShowsWarningInStatusBar()
    {
        Directory.CreateDirectory(_data.Path);
        File.WriteAllText(Path.Combine(_data.Path, "state.json"), "{ broken");

        using var app = AppSession.Launch(_data);

        var statusBar = app.Find("StatusInfoBar");
        Assert.True(Wait.Until(() => statusBar.FindAllDescendants().Any(element =>
            (element.Properties.Name.ValueOrDefault ?? "").Contains("could not be read", StringComparison.Ordinal))));
    }
}
