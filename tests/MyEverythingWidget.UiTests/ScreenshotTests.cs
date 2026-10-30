using FlaUI.Core.Capturing;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.UiTests.Infrastructure;
using GridCell = MyEverythingWidget.Core.Grid.GridCell;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Saves screenshots of key states for visual review (layout, theme, drag feedback). The images go to
/// <see cref="ArtifactsVariable"/>, set by the sandbox runner to <c>results\shots</c>.
/// </summary>
public sealed class ScreenshotTests : IDisposable
{
    private const string ArtifactsVariable = "MEW_UI_TEST_ARTIFACTS";
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private static string ShotPath(string name)
    {
        var directory = Environment.GetEnvironmentVariable(ArtifactsVariable) ?? Path.Combine(Path.GetTempPath(), "mew-shots");
        Directory.CreateDirectory(directory);
        return Path.Combine(directory, name + ".png");
    }

    [Fact]
    public void Capture_GridWithItemsAndDuringDrag()
    {
        StateFiles.Seed(_data, new Dictionary<string, GridPlacement>
        {
            ["A1"] = new(0, 0, 1, 1),
            ["A2"] = new(0, 1, 1, 1),
            ["N1"] = new(0, 2, 2, 1),
            ["I1"] = new(1, 0, 2, 2),
            ["N2"] = new(3, 2, 3, 2),
        });
        using var app = AppSession.Launch(_data);
        var grid = new GridDriver(app, GridSize.Default);
        GridDriver.WaitForUi();

        Capture.Element(app.MainWindow).ToFile(ShotPath("grid-items"));

        var start = grid.CellCenter(new GridCell(0, 2));
        var end = grid.CellCenter(new GridCell(1, 3));
        GridDriver.Press(start);
        GridDriver.MoveSmoothly(start, end);
        GridDriver.WaitForUi();
        Capture.Element(app.MainWindow).ToFile(ShotPath("grid-during-drag"));
        GridDriver.Release();

        Assert.True(File.Exists(ShotPath("grid-during-drag")));
    }
}
