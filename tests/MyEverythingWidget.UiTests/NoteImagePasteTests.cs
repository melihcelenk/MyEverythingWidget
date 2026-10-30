using FlaUI.Core.AutomationElements;
using FlaUI.Core.Input;
using FlaUI.Core.WindowsAPI;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Notes, images and Ctrl+V with the real keyboard and clipboard (MEW-4 Faz 6: N1, N2, I1, I2, K7).
/// </summary>
public sealed class NoteImagePasteTests : IDisposable
{
    private const string GeneralId = "c1";
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private void Seed(params WidgetItem[] items) =>
        StateFiles.Save(_data, new WidgetState(WidgetState.CurrentSchemaVersion, [new Category(GeneralId, "General")], items));

    private static void PressCtrlV(AppSession app)
    {
        app.MainWindow.Focus();
        Thread.Sleep(200);
        Keyboard.TypeSimultaneously(VirtualKeyShort.CONTROL, VirtualKeyShort.KEY_V);
    }

    private IReadOnlyList<WidgetItem> ItemsAfterClose(AppSession app)
    {
        app.ClickCloseAndWaitForExit();
        return StateFiles.ReadState(_data).Items;
    }

    private static AutomationElement Editor(AppSession app) => Wait.ForElement(() => app.FindInPopups("TextEditorBox"));

    /// <summary>The dialog's Save button; searched inside the dialog because other dialogs use the same ids.</summary>
    private static Button SaveButton(AppSession app)
    {
        var dialog = Wait.ForElement(() => app.FindInPopups("TextEditorDialog"));
        return Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("PrimaryButton"))).AsButton();
    }

    [Fact]
    public void PastingText_AddsNote()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        SandboxClipboard.SetText("Meeting at 10\r\nRoom 4");

        PressCtrlV(app);

        Assert.True(Wait.Until(() => app.Find("WidgetGrid").FindAllChildren().Length == 1));
        var note = Assert.IsType<NoteItem>(Assert.Single(ItemsAfterClose(app)));
        Assert.Equal("Meeting at 10\r\nRoom 4", note.Text);
        Assert.Equal(new GridSpan(2, 1), note.Placement.Span);
    }

    [Fact]
    public void PastingScreenshot_AddsImageSizedByAspectRatio()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        SandboxClipboard.SetPicture(1600, 900);

        PressCtrlV(app);

        Assert.True(Wait.Until(() => app.Find("WidgetGrid").FindAllChildren().Length == 1));
        var image = Assert.IsType<ImageItem>(Assert.Single(ItemsAfterClose(app)));
        Assert.Equal(new GridSpan(3, 2), image.Placement.Span);
        Assert.Equal((1600, 900), (image.PixelWidth, image.PixelHeight));
        Assert.True(File.Exists(Path.Combine(_data.Path, image.ImagePath)));
    }

    [Fact]
    public void PastingCopiedProgram_AddsAppCard()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        SandboxClipboard.SetFile(Path.Combine(Environment.SystemDirectory, "cmd.exe"));

        PressCtrlV(app);

        Assert.True(Wait.Until(() => app.Find("WidgetGrid").FindAllChildren().Length == 1));
        Assert.Equal("Cmd", Assert.IsType<AppItem>(Assert.Single(ItemsAfterClose(app))).Name);
    }

    [Fact]
    public void PastingIntoTextBox_DoesNotAddCard()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        SandboxClipboard.SetText("pasted text");
        RealMouse.Click(app.Find("AddItemButton").BoundingRectangle.Center());
        Wait.ForElement(() => app.FindInPopups("AddNoteMenuItem")).AsMenuItem().Invoke();
        var editor = Editor(app).AsTextBox();

        editor.Focus();
        Keyboard.TypeSimultaneously(VirtualKeyShort.CONTROL, VirtualKeyShort.KEY_V);

        Assert.True(Wait.Until(() => editor.Text.Contains("pasted text", StringComparison.Ordinal)));
        Keyboard.Press(VirtualKeyShort.ESCAPE);
        Assert.Empty(ItemsAfterClose(app));
    }

    [Fact]
    public void AddNoteFromMenu_AddsNote()
    {
        Seed();
        using var app = AppSession.Launch(_data);

        RealMouse.Click(app.Find("AddItemButton").BoundingRectangle.Center());
        Wait.ForElement(() => app.FindInPopups("AddNoteMenuItem")).AsMenuItem().Invoke();
        TextInput.Set(Editor(app), "Groceries");
        SaveButton(app).Invoke();

        Assert.True(Wait.Until(() => app.Find("WidgetGrid").FindAllChildren().Length == 1));
        Assert.Equal("Groceries", Assert.IsType<NoteItem>(Assert.Single(ItemsAfterClose(app))).Text);
    }

    [Fact]
    public void CopyButton_PutsNoteTextOnClipboard()
    {
        Seed(new NoteItem("N1", GeneralId, new GridPlacement(0, 0, 2, 1), "Wi-Fi password: hunter2"));
        using var app = AppSession.Launch(_data);
        SandboxClipboard.SetText("something else");
        var card = app.Find("Card_N1");
        RealMouse.MoveTo(card.BoundingRectangle.Center());
        Thread.Sleep(200);

        Wait.ForElement(() => card.FindFirstDescendant(c => c.ByAutomationId("CopyNoteButton"))).AsButton().Invoke();

        Assert.True(Wait.Until(() => SandboxClipboard.GetText() == "Wi-Fi password: hunter2"));
    }

    [Fact]
    public void EditNoteFromMenu_ChangesText()
    {
        Seed(new NoteItem("N1", GeneralId, new GridPlacement(0, 0, 2, 1), "Old"));
        using var app = AppSession.Launch(_data);

        RealMouse.RightClick(app.Find("Card_N1").BoundingRectangle.Center());
        Wait.ForElement(() => app.FindInPopups("EditNoteMenuItem")).AsMenuItem().Invoke();
        TextInput.Set(Editor(app), "New");
        SaveButton(app).Invoke();

        Assert.True(Wait.Until(() => app.Find("Card_N1").Name == "New"));
        Assert.Equal("New", Assert.IsType<NoteItem>(Assert.Single(ItemsAfterClose(app))).Text);
    }

    [Fact]
    public void RenameAppFromMenu_ChangesName()
    {
        Seed(new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Cmd", Path.Combine(Environment.SystemDirectory, "cmd.exe"), LaunchKind.Executable, null));
        using var app = AppSession.Launch(_data);

        RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
        Wait.ForElement(() => app.FindInPopups("RenameItemMenuItem")).AsMenuItem().Invoke();
        TextInput.Set(Editor(app), "Terminal");
        Keyboard.Press(VirtualKeyShort.ENTER);

        Assert.True(Wait.Until(() => app.Find("Card_A1").Name == "Terminal"));
        Assert.Equal("Terminal", Assert.IsType<AppItem>(Assert.Single(ItemsAfterClose(app))).Name);
    }
}
