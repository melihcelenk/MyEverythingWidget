using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

public sealed class DefaultCategoryNameTests
{
    [Fact]
    public void FirstRun_NamesTheFirstCategoryInTheAppsLanguage()
    {
        var board = new WidgetBoard(new InMemoryWidgetStateStore(), () => "c1", GridSize.Default, NullLogger<WidgetBoard>.Instance, defaultCategoryName: "Genel");

        Assert.Equal("Genel", Assert.Single(board.State.Categories).Name);
    }

    [Fact]
    public void FirstRun_WithoutAName_UsesGeneral()
    {
        var board = new WidgetBoard(new InMemoryWidgetStateStore(), () => "c1", GridSize.Default, NullLogger<WidgetBoard>.Instance);

        Assert.Equal(WidgetState.DefaultCategoryName, Assert.Single(board.State.Categories).Name);
    }
}
