using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>Adding, opening and removing app cards (MEW-4 Faz 5: U1-U6).</summary>
public sealed class AppItemsTests
{
    private const string GeneralId = "c1";
    private readonly FakeAppServices _services = new();
    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category(GeneralId, "General")],
        [new AppItem("a1", GeneralId, new GridPlacement(0, 0, 1, 1), "Old tool", @"C:\gone\tool.exe", LaunchKind.Executable, "icons/a1.png")]));

    private int _nextId;

    private BoardViewModel CreateBoard(GridSize? size = null) => new(
        new WidgetBoard(_store, () => $"new{++_nextId}", size ?? GridSize.Default, NullLogger<WidgetBoard>.Instance),
        _services,
        _services);

    private AddAppViewModel CreateDialog(BoardViewModel board) =>
        new(board, _services, path => path == @"C:\Projects");

    [Fact]
    public async Task AddApp_SavesItsIconAndPlacesCard()
    {
        var board = CreateBoard();
        var target = new LaunchTarget(LaunchKind.Executable, @"shell:AppsFolder\Code", "Code");

        Assert.True(await board.AddAppAsync(target, "Visual Studio Code", TestContext.Current.CancellationToken));

        var card = board.Items.Single(item => item.Title == "Visual Studio Code");
        Assert.Equal("icons/fake.png", card.IconPath);
        Assert.Equal((0, 1), (card.Row, card.Column));
        Assert.Equal([target], _services.IconRequests);
    }

    [Fact]
    public async Task AddApp_WithoutIcon_StillAddsCard()
    {
        _services.IconToReturn = null;
        var board = CreateBoard();

        Assert.True(await board.AddAppAsync(new LaunchTarget(LaunchKind.Url, "https://example.org", "Example"), "Example", TestContext.Current.CancellationToken));

        Assert.Null(board.Items.Single(item => item.Title == "Example").IconPath);
    }

    [Fact]
    public async Task AddApp_WhenCategoryFull_ShowsWarningAndDeletesIcon()
    {
        var board = CreateBoard(new GridSize(1, 1));

        Assert.False(await board.AddAppAsync(new LaunchTarget(LaunchKind.Url, "https://example.org", "Example"), "Example", TestContext.Current.CancellationToken));

        Assert.Equal(BoardViewModel.GridFullMessage, board.StatusMessage);
        Assert.Equal(["icons/fake.png"], _services.DeletedIcons);
    }

    [Fact]
    public void Launch_StartsApp()
    {
        var board = CreateBoard();

        board.Launch("a1");

        Assert.Equal("a1", Assert.Single(_services.Launched).Id);
        Assert.Null(board.StatusMessage);
    }

    [Fact]
    public void Launch_MissingTarget_ShowsWarningWithName()
    {
        _services.NextLaunchOutcome = LaunchOutcome.TargetMissing;
        var board = CreateBoard();

        board.Launch("a1");

        Assert.Equal(StatusSeverity.Warning, board.StatusSeverity);
        Assert.Equal("\u201COld tool\u201D could not be found. It may have been moved or uninstalled.", board.StatusMessage);
    }

    [Fact]
    public void Launch_Failure_ShowsError()
    {
        _services.NextLaunchOutcome = LaunchOutcome.Failed;
        var board = CreateBoard();

        board.Launch("a1");

        Assert.Equal(StatusSeverity.Error, board.StatusSeverity);
    }

    [Fact]
    public void Launch_NoteCard_DoesNothing()
    {
        var board = CreateBoard();
        board.Items.Clear();

        board.Launch("missing");

        Assert.Empty(_services.Launched);
    }

    [Fact]
    public void DeleteApp_RemovesItsIconFile()
    {
        var board = CreateBoard();

        board.DeleteCommand.Execute("a1");

        Assert.Equal(["icons/a1.png"], _services.DeletedIcons);
    }

    [Fact]
    public async Task DroppedTexts_AddRecognisedTargetsAndReportOthers()
    {
        var board = CreateBoard();

        var added = await board.AddDroppedAsync([@"C:\Projects", "https://github.com", "not a path"], path => path == @"C:\Projects");

        Assert.Equal(2, added);
        Assert.Contains(board.Items, item => item.Title == "Projects");
        Assert.Contains(board.Items, item => item.Title == "Github");
        Assert.Equal(BoardViewModel.SomeNotAddedMessage, board.StatusMessage);
    }

    [Fact]
    public async Task Dialog_ListsInstalledAppsAndFiltersBySearch()
    {
        _services.Apps.AddRange([
            new InstalledApp("Visual Studio Code", @"shell:AppsFolder\Code"),
            new InstalledApp("Calculator", @"shell:AppsFolder\Calc"),
            new InstalledApp("Code Writer", @"shell:AppsFolder\Writer"),
        ]);
        var dialog = CreateDialog(CreateBoard());

        await dialog.LoadAsync(TestContext.Current.CancellationToken);
        dialog.SearchText = "code";

        Assert.Equal(["Code Writer", "Visual Studio Code"], dialog.FilteredApps.Select(app => app.Name));
        Assert.False(dialog.CanAdd);
    }

    [Fact]
    public async Task Dialog_SelectedApp_IsAddedWithItsName()
    {
        _services.Apps.Add(new InstalledApp("Calculator", @"shell:AppsFolder\Calc"));
        var board = CreateBoard();
        var dialog = CreateDialog(board);
        await dialog.LoadAsync(TestContext.Current.CancellationToken);

        dialog.SelectedApp = dialog.FilteredApps[0];
        Assert.True(dialog.CanAdd);
        Assert.True(await dialog.AddAsync(TestContext.Current.CancellationToken));

        Assert.Contains(board.Items, item => item.Title == "Calculator");
    }

    [Fact]
    public async Task Dialog_ManualPath_SuggestsNameAndAdds()
    {
        var board = CreateBoard();
        var dialog = CreateDialog(board);

        dialog.ManualText = @"C:\Projects";

        Assert.True(dialog.CanAdd);
        Assert.Equal("Projects", dialog.ManualName);
        dialog.ManualName = "My projects";
        Assert.True(await dialog.AddAsync(TestContext.Current.CancellationToken));
        Assert.Contains(board.Items, item => item.Title == "My projects");
    }

    [Fact]
    public void Dialog_InvalidManualText_CannotAddAndExplains()
    {
        var dialog = CreateDialog(CreateBoard());

        dialog.ManualText = "notepad";

        Assert.False(dialog.CanAdd);
        Assert.Equal(AddAppViewModel.InvalidTargetMessage, dialog.ManualError);
    }

    [Fact]
    public void Dialog_TypingManualText_ClearsListSelection()
    {
        var dialog = CreateDialog(CreateBoard());
        dialog.SelectedApp = new InstalledApp("Calculator", @"shell:AppsFolder\Calc");

        dialog.ManualText = "https://example.org";

        Assert.Null(dialog.SelectedApp);
    }
}
