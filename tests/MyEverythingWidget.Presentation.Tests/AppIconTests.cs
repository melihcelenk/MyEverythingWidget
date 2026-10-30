using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>"Change icon…" and "Reset icon" on app cards.</summary>
public sealed class AppIconTests
{
    private readonly FakeAppServices _services = new();
    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category("c1", "General")],
        [new AppItem("a1", "c1", new GridPlacement(0, 0, 1, 1), "Cmd", @"C:\Windows\System32\cmd.exe", LaunchKind.Executable, @"icons\old.png")]));

    private BoardViewModel CreateBoard() =>
        new(new WidgetBoard(_store, () => "x", GridSize.Default, NullLogger<WidgetBoard>.Instance), _services, _services);

    [Fact]
    public async Task ChangeIcon_UsesPickedImageAndDeletesOldIcon()
    {
        _services.ImportedIcon = @"icons\custom.png";
        var board = CreateBoard();

        Assert.True(await board.ChangeIconAsync("a1", new MemoryStream([1, 2, 3]), TestContext.Current.CancellationToken));

        Assert.Equal(@"icons\custom.png", board.Items.Single().IconPath);
        Assert.Equal([@"icons\old.png"], _services.DeletedIcons);
    }

    [Fact]
    public async Task ChangeIcon_UnreadableImage_KeepsIconAndWarns()
    {
        _services.ImportedIcon = null;
        var board = CreateBoard();

        Assert.False(await board.ChangeIconAsync("a1", new MemoryStream([1]), TestContext.Current.CancellationToken));

        Assert.Equal(@"icons\old.png", board.Items.Single().IconPath);
        Assert.Equal(BoardViewModel.ImageNotReadMessage, board.StatusMessage);
        Assert.Empty(_services.DeletedIcons);
    }

    [Fact]
    public async Task ResetIcon_RecreatesIconFromTarget()
    {
        _services.IconToReturn = @"icons\fresh.png";
        var board = CreateBoard();

        Assert.True(await board.ResetIconAsync("a1", TestContext.Current.CancellationToken));

        Assert.Equal(@"icons\fresh.png", board.Items.Single().IconPath);
        Assert.Equal(@"C:\Windows\System32\cmd.exe", Assert.Single(_services.IconRequests).Target);
        Assert.Equal([@"icons\old.png"], _services.DeletedIcons);
    }
}
