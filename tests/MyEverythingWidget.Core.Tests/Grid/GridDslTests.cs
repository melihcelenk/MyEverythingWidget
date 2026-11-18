using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Tests.GridDsl;

namespace MyEverythingWidget.Core.Tests.Grid;

/// <summary>
/// Runs every <c>tests/Grid/*.dsl</c> scenario against <see cref="GridLayout"/>.
/// The scenario files are the specification of grid behaviour.
/// </summary>
public sealed class GridDslTests
{
    private static readonly string ScenarioDirectory = Path.Combine(AppContext.BaseDirectory, "Grid");

    public static TheoryData<string> Scenarios()
    {
        var data = new TheoryData<string>();
        foreach (var file in Directory.GetFiles(ScenarioDirectory, "*.dsl").Order(StringComparer.Ordinal))
        {
            data.Add(Path.GetFileName(file));
        }

        return data;
    }

    [Fact]
    public void ScenarioFolder_ContainsTheLegacyScenarios()
    {
        var names = Directory.GetFiles(ScenarioDirectory, "*.dsl").Select(Path.GetFileName).ToList();

        Assert.Contains("2x1_note_right_edge.dsl", names);
        Assert.Contains("create_app_and_note.dsl", names);
        Assert.Contains("swap_note_and_app.dsl", names);
    }

    [Theory]
    [MemberData(nameof(Scenarios))]
    public void Scenario_ProducesExpectedGrid(string fileName)
    {
        var scenario = GridScenario.Load(Path.Combine(ScenarioDirectory, fileName));
        var layout = new GridLayout(scenario.Size, scenario.Initial);
        GridOutcome? lastOutcome = null;

        foreach (var action in scenario.Actions)
        {
            var result = Apply(layout, action);
            layout = result.Layout;
            lastOutcome = result.Outcome;
        }

        Assert.Equal(GridScenario.Render(scenario.Size, scenario.Expected), GridScenario.Render(layout.Size, layout.Items));
        Assert.Equal(scenario.ExpectedOutcome ?? GridOutcome.Success, lastOutcome);
    }

    private static GridResult Apply(GridLayout layout, GridAction action) => action switch
    {
        CreateAction create => layout.Add(create.Id, DefaultSpans.For(create.Kind)),
        DragAction drag => layout.Move(drag.Id, drag.Target),
        ResizeAction resize => layout.Resize(resize.Id, resize.Span),
        DeleteAction delete => layout.Remove(delete.Id),
        _ => throw new ArgumentOutOfRangeException(nameof(action), action, "Unknown scenario action."),
    };
}
