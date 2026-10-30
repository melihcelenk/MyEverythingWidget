using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

public sealed class WidgetBoardIconTests
{
    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category("c1", "General")],
        [
            new AppItem("a1", "c1", new GridPlacement(0, 0, 1, 1), "Cmd", "cmd.exe", LaunchKind.Executable, @"icons\old.png"),
            new NoteItem("n1", "c1", new GridPlacement(0, 1, 2, 1), "x"),
        ]));

    private WidgetBoard CreateBoard() => new(_store, () => "x", GridSize.Default, NullLogger<WidgetBoard>.Instance);

    [Fact]
    public void SetAppIcon_ReplacesPathAndReturnsOldOne()
    {
        var board = CreateBoard();

        var old = board.SetAppIcon("a1", @"icons\new.png");

        Assert.Equal(@"icons\old.png", old);
        Assert.Equal(@"icons\new.png", Assert.IsType<AppItem>(_store.Current!.Items[0]).IconPath);
    }

    [Fact]
    public void SetAppIcon_OnNote_IsIgnored()
    {
        var board = CreateBoard();

        Assert.Null(board.SetAppIcon("n1", @"icons\new.png"));

        Assert.IsType<NoteItem>(board.Find("n1"));
    }
}
