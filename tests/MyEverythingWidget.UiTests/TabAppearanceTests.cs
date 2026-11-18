using System.Diagnostics;
using System.Drawing;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Capturing;
using FlaUI.Core.Input;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.UiTests.Infrastructure;
using Wait = MyEverythingWidget.UiTests.Infrastructure.Wait;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Tabs are drawn at once, not faded or slid in after their window or dialog appears (MEW-4 Faz 14: A1-A2).
/// The tab's screen area is captured every few milliseconds; it must reach its final look quickly.
/// </summary>
public sealed class TabAppearanceTests : IDisposable
{
    private const string GeneralId = "c1";
    private static readonly TimeSpan Observation = TimeSpan.FromMilliseconds(1200);
    private static readonly TimeSpan Allowed = TimeSpan.FromMilliseconds(150);
    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    private void Seed() => StateFiles.Save(_data, new WidgetState(
        WidgetState.CurrentSchemaVersion,
        [new Category(GeneralId, "General"), new Category("c2", "Work")],
        [new AppItem("A1", GeneralId, new GridPlacement(0, 0, 1, 1), "Cmd", Path.Combine(Environment.SystemDirectory, "cmd.exe"), LaunchKind.Executable, null)]));

    /// <summary>
    /// Captures <paramref name="area"/> repeatedly and returns how long after the first capture it kept changing
    /// (the last capture that still differed clearly from the final look).
    /// </summary>
    private static TimeSpan SettleTime(Rectangle area, string name)
    {
        var frames = new List<(TimeSpan At, Bitmap Image)>();
        var clock = Stopwatch.StartNew();
        while (clock.Elapsed < Observation)
        {
            frames.Add((clock.Elapsed, Capture.Rectangle(area).Bitmap));
            Thread.Sleep(30);
        }

        var final = frames[^1].Image;
        final.Save(Artifacts.PathOf(name + "-final"));
        frames[0].Image.Save(Artifacts.PathOf(name + "-first"));
        var settled = frames.Where(frame => Difference(frame.Image, final) > 6).Select(frame => frame.At).DefaultIfEmpty(TimeSpan.Zero).Max();
        frames.ForEach(frame => frame.Image.Dispose());
        return settled;
    }

    /// <summary>Distance between sampled pixels; sampling keeps each comparison fast, so it does not slow the timing.</summary>
    private const int SampleStride = 6;

    /// <summary>Mean absolute brightness difference per sampled pixel, 0-255.</summary>
    private static double Difference(Bitmap a, Bitmap b)
    {
        var width = Math.Min(a.Width, b.Width);
        var height = Math.Min(a.Height, b.Height);
        double total = 0;
        var samples = 0;
        for (var y = 0; y < height; y += SampleStride)
        {
            for (var x = 0; x < width; x += SampleStride)
            {
                var p = a.GetPixel(x, y);
                var q = b.GetPixel(x, y);
                total += Math.Abs(((p.R + p.G + p.B) - (q.R + q.G + q.B)) / 3.0);
                samples++;
            }
        }

        return samples == 0 ? 0 : total / samples;
    }

    [Fact]
    public void CategoryTabs_AreDrawnWithTheWindow()
    {
        Seed();
        using var app = AppSession.LaunchWithoutSettling(_data);
        var tab = Wait.ForElement(() => app.TryFind("Tab_" + GeneralId));
        Assert.True(Wait.Until(() => !tab.BoundingRectangle.IsEmpty));

        var settle = SettleTime(app.Find("CategoryTabs").BoundingRectangle, "category-tabs");

        Assert.True(settle <= Allowed, $"The category tabs kept changing for {settle.TotalMilliseconds:F0} ms after they appeared.");
    }

    [Fact]
    public void IconDialogTabs_AreDrawnWithTheDialog()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        GridDriver.WaitForUi();
        RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
        Wait.ForElement(() => app.FindInPopups("ChangeIconMenuItem")).AsMenuItem().Invoke();
        var dialog = Wait.ForElement(() => app.FindInPopups("IconPickerDialog"));
        var tab = Wait.ForElement(() => dialog.FindFirstDescendant(c => c.ByAutomationId("SelectImageTab")));
        Assert.True(Wait.Until(() => !tab.BoundingRectangle.IsEmpty));
        var iconTab = dialog.FindFirstDescendant(c => c.ByAutomationId("SelectIconTab"))!.BoundingRectangle;

        var settle = SettleTime(Rectangle.Union(iconTab, tab.BoundingRectangle), "dialog-tabs");

        Assert.True(settle <= Allowed, $"The dialog tabs kept changing for {settle.TotalMilliseconds:F0} ms after they appeared.");
    }

    /// <summary>
    /// Opens the icon dialog from the card menu and returns the time from the click until the dialog is drawn.
    /// </summary>
    private static long OpenIconDialogAndMeasure(AppSession app)
    {
        GridDriver.WaitForUi();
        RealMouse.RightClick(app.Find("Card_A1").BoundingRectangle.Center());
        var item = Wait.ForElement(() => app.FindInPopups("ChangeIconMenuItem")).AsMenuItem();
        var bounds = Win32.GetBounds(app.WindowHandle);
        var area = Rectangle.FromLTRB(bounds.Left, bounds.Top, bounds.Right, bounds.Bottom);
        using var before = Capture.Rectangle(area).Bitmap;
        var clock = Stopwatch.StartNew();
        item.Invoke();
        while (clock.Elapsed < TimeSpan.FromSeconds(10))
        {
            using var frame = Capture.Rectangle(area).Bitmap;
            if (Difference(frame, before) > 10)
            {
                break;
            }

            Thread.Sleep(10);
        }

        var elapsed = clock.ElapsedMilliseconds;
        Assert.NotNull(Wait.ForElement(() => app.FindInPopups("IconPickerDialog")));
        Keyboard.Press(FlaUI.Core.WindowsAPI.VirtualKeyShort.ESCAPE);
        Assert.True(Wait.Until(() => app.FindInPopups("IconPickerDialog") is null));
        return elapsed;
    }

    [Fact]
    public void IconDialog_OpensQuickly()
    {
        Seed();
        using var app = AppSession.Launch(_data);
        Thread.Sleep(TimeSpan.FromSeconds(4));

        var first = OpenIconDialogAndMeasure(app);
        var later = new[] { OpenIconDialogAndMeasure(app), OpenIconDialogAndMeasure(app), OpenIconDialogAndMeasure(app) }.Order().ToArray();
        var report = $"first {first} ms, later {string.Join(", ", later)} ms";
        File.WriteAllText(Artifacts.PathOf("icon-dialog-times").Replace(".png", ".txt", StringComparison.Ordinal), report);

        Assert.True(first <= 1200, $"The first icon dialog should appear within 1.2 s of the click; {report}.");
        Assert.True(later[1] <= 400, $"Later icon dialogs should appear within 0.4 s of the click; {report}.");
    }
}
