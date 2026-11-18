using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using MyEverythingWidget.Core.Apps;

namespace MyEverythingWidget.App;

/// <summary>
/// Draws the icon picker's emojis once after start-up, behind an opaque surface where they are never seen. The first
/// drawing of a colour emoji is expensive; done here one emoji at a time while the app is idle, it costs no visible
/// pause, and the icon dialog opens without paying it.
/// </summary>
internal static class EmojiFontWarmUp
{
    private static readonly TimeSpan StepInterval = TimeSpan.FromMilliseconds(60);

    /// <summary>
    /// Starts drawing the emojis, one per idle step, in <paramref name="hiddenLayer"/> (a panel covered by an opaque
    /// element); <paramref name="finished"/> runs when all are drawn and the layer is empty again.
    /// </summary>
    public static void Start(Panel hiddenLayer, Action? finished = null)
    {
        ArgumentNullException.ThrowIfNull(hiddenLayer);

        var font = new FontFamily("Segoe UI Emoji");
        var pending = new Queue<string>(IconEmoji.Suggestions);
        var timer = hiddenLayer.DispatcherQueue.CreateTimer();
        timer.Interval = StepInterval;
        timer.Tick += (_, _) =>
        {
            if (pending.TryDequeue(out var emoji))
            {
                hiddenLayer.Children.Add(new TextBlock
                {
                    Text = emoji,
                    FontFamily = font,
                    FontSize = 20,
                    HorizontalAlignment = HorizontalAlignment.Left,
                    VerticalAlignment = VerticalAlignment.Top,
                });
                return;
            }

            timer.Stop();
            hiddenLayer.Children.Clear();
            finished?.Invoke();
        };
        timer.Start();
    }
}
