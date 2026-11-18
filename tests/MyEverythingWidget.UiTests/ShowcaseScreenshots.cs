using System.Drawing;
using System.Runtime.InteropServices;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Capturing;
using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.Infrastructure.Shell;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Takes the README and Store screenshots: each one shows a real use of the widget with realistic, made-up content.
/// Run with <c>pwsh scripts/capture-screenshots.ps1</c>; the normal UI test run skips them. The sandbox desktop is
/// switched to a plain colour and each picture is cropped around the windows, so no wallpaper or taskbar shows.
/// </summary>
[Trait("Category", "Showcase")]
public sealed partial class ShowcaseScreenshots : IDisposable
{
    /// <summary>Plain desktop colour behind the windows; <c>scripts/capture-screenshots.ps1</c> continues it around them.</summary>
    private static readonly Color Desktop = Color.FromArgb(0xDC, 0xE6, 0xF2);

    private const int Margin = 72;

    private const string WorkId = "work";
    private const string SnippetsId = "snippets";
    private const string InboxId = "inbox";
    private const string ScreensId = "screens";

    private static readonly GridSize Grid = new(Rows: 4, Columns: 5);

    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    [Fact]
    public void Launcher()
    {
        using var app = Launch(AppTheme.Light);
        Select(app, WorkId);
        Save(app, "showcase-1-launcher");
    }

    [Fact]
    public void Snippets()
    {
        using var app = Launch(AppTheme.Light);
        Select(app, SnippetsId);
        var card = app.Find("Card_S1");
        RealMouse.MoveTo(card.BoundingRectangle.Center());
        var copy = Wait.ForElement(() => card.FindFirstDescendant(c => c.ByAutomationId("CopyNoteButton")));
        GridDriver.WaitForUi();
        RealMouse.Click(copy.BoundingRectangle.Center());
        Thread.Sleep(300);
        Save(app, "showcase-2-snippets");
    }

    [Fact]
    public void QuickNotes()
    {
        using var app = Launch(AppTheme.Light);
        Select(app, InboxId);
        SandboxClipboard.SetText("Ticket SR-20931\nReply within 2 working days");
        RealMouse.Click(app.Find("WidgetGrid").BoundingRectangle.Center());
        FlaUI.Core.Input.Keyboard.TypeSimultaneously(FlaUI.Core.WindowsAPI.VirtualKeyShort.CONTROL, FlaUI.Core.WindowsAPI.VirtualKeyShort.KEY_V);
        Wait.Until(() => StateFiles.ReadState(_data).Items.Count(item => item.CategoryId == InboxId) > 4);
        GridDriver.WaitForUi();
        Save(app, "showcase-3-quick-notes");
    }

    [Fact]
    public void Screens()
    {
        using var app = Launch(AppTheme.Light);
        Select(app, ScreensId);
        RealMouse.Click(app.Find("Card_P1").BoundingRectangle.Center());
        var viewer = Wait.ForElement(() => app.FindWindow("error-screen.png"));
        GridDriver.WaitForUi();
        var widget = Bounds(app.WindowHandle);
        Win32.MoveTo(viewer.Properties.NativeWindowHandle.Value, widget.Right - 80, widget.Top + 90);
        GridDriver.WaitForUi();
        var inside = viewer.BoundingRectangle;
        RealMouse.RightClick(new Point(inside.Left + (inside.Width / 3), inside.Top + (inside.Height / 2)));
        Wait.ForElement(() => viewer.FindFirstDescendant(c => c.ByAutomationId("ViewerCopyMenuItem")) ?? app.FindInPopups("ViewerCopyMenuItem"));
        GridDriver.WaitForUi();
        CaptureAround("showcase-4-screens", Bounds(app.WindowHandle), viewer.BoundingRectangle);
    }

    [Fact]
    public void Compact()
    {
        using var app = Launch(AppTheme.Dark);
        Select(app, WorkId);
        Save(app, "showcase-5-expanded");

        RealMouse.Click(app.Find("CompactButton").BoundingRectangle.Center());
        var icon = Wait.ForElement(() => app.TryFind("CompactIcon"));
        GridDriver.WaitForUi();
        RealMouse.MoveTo(new Point(5, 5));
        Thread.Sleep(1500);
        CaptureAround("showcase-5-compact", icon.BoundingRectangle);
    }

    private AppSession Launch(AppTheme theme)
    {
        UsePlainDesktop();
        SeedImages();
        StateFiles.Save(_data, WithIcons(State()));
        new JsonSettingsStore(_data.Path, TimeProvider.System, NullLogger<JsonSettingsStore>.Instance)
            .Save(AppSettings.Default with { Theme = theme, GridSize = Grid });
        var app = AppSession.Launch(_data);
        Win32.MoveTo(app.WindowHandle, 160, 120);
        GridDriver.WaitForUi();
        return app;
    }

    private static void Select(AppSession app, string categoryId)
    {
        app.Find("Tab_" + categoryId).AsTabItem().Select();
        GridDriver.WaitForUi();

        // A tab's tooltip can stay open from start-up; hovering the grid and then leaving the window closes it.
        RealMouse.MoveTo(app.Find("WidgetGrid").BoundingRectangle.Center());
        Thread.Sleep(500);
        RealMouse.MoveTo(new Point(5, 5));
        FlaUI.Core.Input.Keyboard.Type(FlaUI.Core.WindowsAPI.VirtualKeyShort.ESCAPE);
        Thread.Sleep(1500);
    }

    private static void Save(AppSession app, string name) => CaptureAround(name, Bounds(app.WindowHandle));

    private static Rectangle Bounds(nint window)
    {
        var bounds = Win32.GetBounds(window);
        return Rectangle.FromLTRB(bounds.Left, bounds.Top, bounds.Right, bounds.Bottom);
    }

    /// <summary>Saves the screen area covering <paramref name="areas"/> plus a margin of plain desktop.</summary>
    private static void CaptureAround(string name, params Rectangle[] areas)
    {
        var union = areas.Aggregate(Rectangle.Union);
        union.Inflate(Margin, Margin);
        Capture.Rectangle(union).ToFile(Artifacts.PathOf(name));
    }

    /// <summary>Gives the app and folder cards their real shell icons, as adding them in the app does.</summary>
    private WidgetState WithIcons(WidgetState state)
    {
        var icons = new ShellIconStore(_data.Path, new NoSiteIcons(), NullLogger<ShellIconStore>.Instance);
        var items = state.Items.Select(item => item is AppItem { Emoji: null } app
            ? app with { IconPath = icons.CreateIconAsync(new LaunchTarget(app.LaunchKind, app.Target, app.Name), CancellationToken.None).GetAwaiter().GetResult() }
            : item).ToList();
        return state with { Items = items };
    }

    private static void UsePlainDesktop()
    {
        const uint setWallpaper = 0x0014;
        const uint sendChange = 0x02;
        const int desktopColor = 1;
        SystemParametersInfoW(setWallpaper, 0, "", sendChange);
        SetSysColors(1, [desktopColor], [ColorTranslator.ToWin32(Desktop)]);

        // Hides the desktop icons (the list view inside Progman's SHELLDLL_DefView).
        const int hide = 0;
        var view = FindWindowExW(FindWindowExW(FindWindowW("Progman", null), 0, "SHELLDLL_DefView", null), 0, "SysListView32", null);
        if (view != 0)
        {
            ShowWindow(view, hide);
        }
    }

    [LibraryImport("user32.dll", StringMarshalling = StringMarshalling.Utf16)]
    private static partial nint FindWindowW(string className, string? windowName);

    [LibraryImport("user32.dll", StringMarshalling = StringMarshalling.Utf16)]
    private static partial nint FindWindowExW(nint parent, nint after, string className, string? windowName);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool ShowWindow(nint window, int command);

    [LibraryImport("user32.dll", StringMarshalling = StringMarshalling.Utf16)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool SystemParametersInfoW(uint action, uint param, string value, uint flags);

    [LibraryImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static partial bool SetSysColors(int count, int[] elements, int[] colors);

    /// <summary>The sandbox has no network; web cards use emoji instead of site icons.</summary>
    private sealed class NoSiteIcons : ISiteIconSource
    {
        public Task<byte[]?> GetPngAsync(Uri page, int size, CancellationToken cancellationToken) => Task.FromResult<byte[]?>(null);
    }

    private void SeedImages()
    {
        var images = Path.Combine(_data.Path, "images");
        Directory.CreateDirectory(images);
        foreach (var file in new[] { "error-screen.png", "signups-chart.png" })
        {
            File.Copy(Path.Combine(AppContext.BaseDirectory, "Showcase", file), Path.Combine(images, file), overwrite: true);
        }
    }

    private static WidgetState State()
    {
        var system = Environment.SystemDirectory;
        var profile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        var edge = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), @"Microsoft\Edge\Application\msedge.exe");

        var work = new List<WidgetItem>();
        void App(string name, string target, LaunchKind kind = LaunchKind.Executable, string? emoji = null)
        {
            var index = work.Count;
            work.Add(new AppItem("W" + index, WorkId, new GridPlacement(index / Grid.Columns, index % Grid.Columns, 1, 1), name, target, kind, null) { Emoji = emoji });
        }

        App("Edge", edge);
        App("PowerShell", Path.Combine(system, @"WindowsPowerShell\v1.0\powershell.exe"));
        App("Cmd", Path.Combine(system, "cmd.exe"));
        App("Tasks", Path.Combine(system, "Taskmgr.exe"));
        App("Remote PC", Path.Combine(system, "mstsc.exe"));
        App("Projects", Path.Combine(profile, "Documents"), LaunchKind.Folder);
        App("Downloads", Path.Combine(profile, "Downloads"), LaunchKind.Folder);
        App("Docs", "https://learn.microsoft.com", LaunchKind.Url, "📚");
        App("Issues", "https://github.com/issues", LaunchKind.Url, "🐞");
        App("Calendar", "https://outlook.live.com/calendar", LaunchKind.Url, "📅");
        App("Mail", "https://outlook.live.com/mail", LaunchKind.Url, "✉️");
        App("Team chat", "https://teams.microsoft.com", LaunchKind.Url, "💬");
        App("Explorer", Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "explorer.exe"));
        App("Calculator", Path.Combine(system, "calc.exe"));
        App("Monitor", Path.Combine(system, "resmon.exe"));
        App("Control", Path.Combine(system, "control.exe"));
        App("Char Map", Path.Combine(system, "charmap.exe"));
        App("Settings", "ms-settings:", LaunchKind.Url, "⚙️");
        App("Releases", "https://github.com/melihcelenk/MyEverythingWidget/releases", LaunchKind.Url, "🚀");
        App("Status", "https://status.example.com", LaunchKind.Url, "🟢");

        WidgetItem[] snippets =
        [
            new NoteItem("S1", SnippetsId, new GridPlacement(0, 0, 3, 2),
                "docker run --rm -it -v \"${PWD}:/app\" -w /app mcr.microsoft.com/dotnet/sdk:10.0 dotnet test --filter Category=Smoke"),
            new NoteItem("S2", SnippetsId, new GridPlacement(0, 3, 2, 2),
                "Kind regards,\nAlex Morgan\nProduct Designer\nNorthwind Studio"),
            new NoteItem("S3", SnippetsId, new GridPlacement(2, 0, 2, 2),
                "Northwind Studio\n21 Harbour Street, Unit 4\nLeeds LS1 5BW\nUnited Kingdom"),
            new NoteItem("S4", SnippetsId, new GridPlacement(2, 2, 3, 2),
                "SELECT o.id, o.total, c.email\nFROM orders o\nJOIN customers c ON c.id = o.customer_id\nWHERE o.status = 'failed'\n  AND o.created_at > now() - interval '1 day';"),
        ];

        WidgetItem[] inbox =
        [
            new NoteItem("Q1", InboxId, new GridPlacement(0, 0, 2, 2), "Order 4417-2291\nCourier: collect before Fri 18:00"),
            new NoteItem("Q2", InboxId, new GridPlacement(0, 2, 3, 1), "Call Sam back: invoice is €240 off"),
            new NoteItem("Q3", InboxId, new GridPlacement(1, 2, 3, 1), "Venue Wi-Fi: Harbour-Guest"),
            new NoteItem("Q4", InboxId, new GridPlacement(2, 0, 3, 1), "Review link from Dana:\nmeet.example.com/q4-review"),
        ];

        WidgetItem[] screens =
        [
            new ImageItem("P1", ScreensId, new GridPlacement(0, 0, 3, 2), @"images\error-screen.png", 720, 420),
            new ImageItem("P2", ScreensId, new GridPlacement(2, 0, 3, 2), @"images\signups-chart.png", 640, 400),
            new NoteItem("P3", ScreensId, new GridPlacement(0, 3, 2, 2), "Sync times out with 200+ invoices. Send this screen to support."),
        ];

        return new WidgetState(
            WidgetState.CurrentSchemaVersion,
            [new Category(WorkId, "Work"), new Category(SnippetsId, "Snippets"), new Category(InboxId, "Inbox"), new Category(ScreensId, "Screens")],
            [.. work, .. snippets, .. inbox, .. screens]);
    }
}
