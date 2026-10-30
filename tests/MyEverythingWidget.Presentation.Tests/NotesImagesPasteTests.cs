using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>Notes, images and Ctrl+V (MEW-4 Faz 6: N1, N2, I1, I2, K7).</summary>
public sealed class NotesImagesPasteTests : IDisposable
{
    private const string GeneralId = "c1";
    private readonly FakeAppServices _apps = new();
    private readonly FakeImageStore _images = new();
    private readonly string _imageFile = Path.Combine(Path.GetTempPath(), $"mew-{Guid.NewGuid():N}.png");
    private readonly InMemoryWidgetStateStore _store = new(new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category(GeneralId, "General")],
        [
            new NoteItem("n1", GeneralId, new GridPlacement(4, 0, 2, 1), "Old note"),
            new AppItem("a1", GeneralId, new GridPlacement(4, 4, 1, 1), "Notepad", "notepad.exe", LaunchKind.Executable, null),
            new ImageItem("i1", GeneralId, new GridPlacement(4, 2, 1, 1), @"images\i1.png", 10, 10),
        ]));

    private int _nextId;

    public NotesImagesPasteTests() => File.WriteAllBytes(_imageFile, [1, 2, 3]);

    public void Dispose() => File.Delete(_imageFile);

    private BoardViewModel CreateBoard() => new(
        new WidgetBoard(_store, () => $"new{++_nextId}", GridSize.Default, NullLogger<WidgetBoard>.Instance),
        _apps,
        _apps,
        _images);

    private static Task<Stream?> SomeBitmap(CancellationToken cancellationToken) => Task.FromResult<Stream?>(new MemoryStream([9, 9, 9]));

    [Fact]
    public void AddNote_Creates2x1NoteAtFirstFreeCells()
    {
        var board = CreateBoard();

        Assert.True(board.AddNote("Call the bank"));

        var card = board.Items.Single(item => item.Text == "Call the bank");
        Assert.Equal((0, 0, 2, 1), (card.Row, card.Column, card.ColumnSpan, card.RowSpan));
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    public void AddNote_Blank_AddsNothing(string text)
    {
        var board = CreateBoard();

        Assert.False(board.AddNote(text));

        Assert.Equal(3, board.Items.Count);
    }

    [Fact]
    public void EditNote_ChangesTextOnCard()
    {
        var board = CreateBoard();

        Assert.True(board.EditNote("n1", "New text"));

        Assert.Equal("New text", board.Items.Single(item => item.Id == "n1").Text);
    }

    [Fact]
    public void RenameApp_ChangesCardTitle()
    {
        var board = CreateBoard();

        Assert.True(board.RenameApp("a1", "Editor"));

        Assert.Equal("Editor", board.Items.Single(item => item.Id == "a1").Title);
    }

    [Fact]
    public async Task AddImage_UsesAspectRatioForSpan()
    {
        _images.NextSize = (1920, 1080);
        var board = CreateBoard();

        Assert.True(await board.AddImageAsync(new MemoryStream([1]), TestContext.Current.CancellationToken));

        var card = board.Items.Single(item => item.ImagePath == _images.LastSaved);
        Assert.Equal((3, 2), (card.ColumnSpan, card.RowSpan));
    }

    [Fact]
    public async Task AddImage_Unreadable_ShowsWarning()
    {
        _images.NextSize = null;
        var board = CreateBoard();

        Assert.False(await board.AddImageAsync(new MemoryStream([1]), TestContext.Current.CancellationToken));

        Assert.Equal(BoardViewModel.ImageNotReadMessage, board.StatusMessage);
    }

    [Fact]
    public void DeleteImage_RemovesItsFile()
    {
        var board = CreateBoard();

        board.DeleteCommand.Execute("i1");

        Assert.Equal([@"images\i1.png"], _images.Deleted);
    }

    [Fact]
    public async Task Paste_Bitmap_AddsImage()
    {
        _images.NextSize = (1000, 1000);
        var board = CreateBoard();

        await board.PasteAsync(new PastedContent([], SomeBitmap, "ignored text"), _ => false);

        var card = board.Items.Single(item => item.ImagePath == _images.LastSaved);
        Assert.Equal((2, 2), (card.ColumnSpan, card.RowSpan));
        Assert.DoesNotContain(board.Items, item => item.Text == "ignored text");
    }

    [Fact]
    public async Task Paste_ImageFile_AddsImage()
    {
        _images.NextSize = (1600, 1200);
        var board = CreateBoard();

        await board.PasteAsync(new PastedContent([_imageFile], null, null), _ => false);

        Assert.Contains(board.Items, item => item.ImagePath == _images.LastSaved && item.ColumnSpan == 2 && item.RowSpan == 1);
    }

    [Fact]
    public async Task Paste_ProgramFile_AddsApp()
    {
        var board = CreateBoard();

        await board.PasteAsync(new PastedContent([@"C:\Windows\System32\cmd.exe"], null, null), _ => false);

        Assert.Contains(board.Items, item => item.Title == "Cmd");
    }

    [Fact]
    public async Task Paste_WebAddress_AddsApp()
    {
        var board = CreateBoard();

        await board.PasteAsync(new PastedContent([], null, "  https://github.com  "), _ => false);

        Assert.Contains(board.Items, item => item.Title == "Github");
    }

    [Fact]
    public async Task Paste_Text_AddsNote()
    {
        var board = CreateBoard();

        await board.PasteAsync(new PastedContent([], null, "Meeting at 10\nRoom 4"), _ => false);

        Assert.Contains(board.Items, item => item.Text == "Meeting at 10\nRoom 4");
    }

    [Fact]
    public async Task Paste_TextWithAddressInside_AddsNote()
    {
        var board = CreateBoard();

        await board.PasteAsync(new PastedContent([], null, "see https://github.com later"), _ => false);

        Assert.Contains(board.Items, item => item.Text == "see https://github.com later");
    }

    [Fact]
    public async Task Paste_Nothing_DoesNothing()
    {
        var board = CreateBoard();

        await board.PasteAsync(new PastedContent([], null, "   "), _ => false);

        Assert.Equal(3, board.Items.Count);
        Assert.Null(board.StatusMessage);
    }

    private sealed class FakeImageStore : IImageStore
    {
        public (int Width, int Height)? NextSize { get; set; } = (100, 100);

        public string? LastSaved { get; private set; }

        public List<string> Deleted { get; } = [];

        public Task<StoredImage?> ImportAsync(Stream image, CancellationToken cancellationToken)
        {
            if (NextSize is not { } size)
            {
                return Task.FromResult<StoredImage?>(null);
            }

            LastSaved = $@"images\{Guid.NewGuid():N}.png";
            return Task.FromResult<StoredImage?>(new StoredImage(LastSaved, size.Width, size.Height));
        }

        public void Delete(string relativePath) => Deleted.Add(relativePath);
    }
}
