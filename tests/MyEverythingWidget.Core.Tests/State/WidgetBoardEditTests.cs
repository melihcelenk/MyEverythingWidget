using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.State;

public sealed class WidgetBoardEditTests
{
    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category("c1", "General")],
        [
            new AppItem("a1", "c1", new GridPlacement(0, 0, 1, 1), "Notepad", "notepad.exe", LaunchKind.Executable, null),
            new NoteItem("n1", "c1", new GridPlacement(0, 1, 2, 1), "Buy milk"),
        ]));

    private WidgetBoard CreateBoard() => new(_store, () => "x", GridSize.Default, NullLogger<WidgetBoard>.Instance);

    [Fact]
    public void UpdateNoteText_ChangesTextAndKeepsPlace()
    {
        var board = CreateBoard();

        Assert.True(board.UpdateNoteText("n1", "  Buy milk\nand bread  "));

        var note = Assert.IsType<NoteItem>(board.Find("n1"));
        Assert.Equal("Buy milk\nand bread", note.Text);
        Assert.Equal(new GridPlacement(0, 1, 2, 1), note.Placement);
        Assert.Equal("Buy milk\nand bread", Assert.IsType<NoteItem>(_store.Current!.Items[1]).Text);
    }

    [Theory]
    [InlineData("")]
    [InlineData("  ")]
    public void UpdateNoteText_Blank_IsRefused(string text)
    {
        var board = CreateBoard();

        Assert.False(board.UpdateNoteText("n1", text));

        Assert.Equal("Buy milk", Assert.IsType<NoteItem>(board.Find("n1")).Text);
    }

    [Fact]
    public void UpdateNoteText_OnApp_IsRefused()
    {
        Assert.False(CreateBoard().UpdateNoteText("a1", "x"));
    }

    [Fact]
    public void RenameApp_ChangesNameOnly()
    {
        var board = CreateBoard();

        Assert.True(board.RenameApp("a1", " Editor "));

        var app = Assert.IsType<AppItem>(board.Find("a1"));
        Assert.Equal("Editor", app.Name);
        Assert.Equal("notepad.exe", app.Target);
    }

    [Theory]
    [InlineData("n1", "x")]
    [InlineData("a1", " ")]
    [InlineData("missing", "x")]
    public void RenameApp_Invalid_IsRefused(string itemId, string name)
    {
        Assert.False(CreateBoard().RenameApp(itemId, name));
    }
}
