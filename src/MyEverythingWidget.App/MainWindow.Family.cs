using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using MyEverythingWidget.Presentation;
using Windows.Graphics;
using FamilyEdge = WidgetFamily.Edge;
using FamilyPlacement = WidgetFamily.Placement;
using FamilyRect = WidgetFamily.PixelRect;
using FamilySize = WidgetFamily.PixelSize;

namespace MyEverythingWidget.App;

/// <summary>
/// The widget family menu of the compact icon (MEW-5): right-click shows the installed family widgets on the icon's
/// four sides; clicking one opens it next to the icon. Window-level only; the decisions are in
/// <see cref="FamilyMenuViewModel"/>.
/// </summary>
public sealed partial class MainWindow
{
    /// <summary>Space between the icon and a slot, in device-independent pixels; the same gap the widgets keep.</summary>
    private const double FamilySlotGap = 8;

    /// <summary>The family members around the compact icon.</summary>
    public FamilyMenuViewModel Family { get; }

    private async void OnCompactIconContextRequested(UIElement sender, ContextRequestedEventArgs args)
    {
        args.Handled = true;
        if (!ViewModel.IsCompact)
        {
            return;
        }

        await Family.RefreshAsync(CancellationToken.None);

        // Opened invisible first: the slots are measured in the live tree, then placed, then shown.
        FamilyRing.Opacity = 0;
        FamilyPopup.IsOpen = true;
        FamilyRing.UpdateLayout();
        LayOutFamilySlots();
        FamilyRing.Opacity = 1;
    }

    /// <summary>
    /// Places each visible slot next to the icon with <see cref="FamilyPlacement.NextTo"/>, the rule the widget uses
    /// when it opens: a side without room moves to the opposite side and every slot stays on the screen.
    /// </summary>
    private void LayOutFamilySlots()
    {
        var icon = IconBounds();
        var area = DisplayArea.GetFromRect(new RectInt32(icon.Left, icon.Top, icon.Width, icon.Height), DisplayAreaFallback.Nearest).WorkArea;
        var workArea = new FamilyRect(area.X, area.Y, area.Width, area.Height);
        var scale = _resizer.Scale;
        var gap = (int)Math.Round(FamilySlotGap * scale);

        var placed = new List<(FrameworkElement Element, double X, double Y)>();
        foreach (var (element, edge) in FamilySlotElements())
        {
            if (element.Visibility != Visibility.Visible)
            {
                continue;
            }

            element.Measure(new Windows.Foundation.Size(double.PositiveInfinity, double.PositiveInfinity));
            var size = new FamilySize(
                (int)Math.Ceiling(element.DesiredSize.Width * scale),
                (int)Math.Ceiling(element.DesiredSize.Height * scale));
            var rect = FamilyPlacement.NextTo(icon, edge, size, workArea, gap);
            placed.Add((element, (rect.Left - icon.Left) / scale, (rect.Top - icon.Top) / scale));
        }

        if (placed.Count == 0)
        {
            return;
        }

        // The popup starts at the top-left slot; the slots are placed inside it relative to that corner.
        var left = placed.Min(slot => slot.X);
        var top = placed.Min(slot => slot.Y);
        foreach (var (element, x, y) in placed)
        {
            Canvas.SetLeft(element, x - left);
            Canvas.SetTop(element, y - top);
        }

        FamilyRing.Width = placed.Max(slot => slot.X + slot.Element.DesiredSize.Width) - left;
        FamilyRing.Height = placed.Max(slot => slot.Y + slot.Element.DesiredSize.Height) - top;
        FamilyPopup.HorizontalOffset = left;
        FamilyPopup.VerticalOffset = top;
    }

    private IEnumerable<(FrameworkElement Element, FamilyEdge Edge)> FamilySlotElements() =>
    [
        (FamilyTop, FamilyEdge.Top),
        (FamilyRight, FamilyEdge.Right),
        (FamilyBottom, FamilyEdge.Bottom),
        (FamilyLeft, FamilyEdge.Left),
        (FamilyEmptyCard, FamilyEdge.Right),
    ];

    /// <summary>A download button: opens the family widget's Store page (T16).</summary>
    private async void OnFamilyDownloadClicked(object sender, RoutedEventArgs e)
    {
        FamilyPopup.IsOpen = false;
        if (sender is FrameworkElement { Tag: string memberId })
        {
            await Family.DownloadAsync(memberId);
        }
    }

    /// <summary>The icon was dragged: the members opened from it move along (MEW-5 Faz 4).</summary>
    private async void MoveFamilyMembersAlong() => await Family.FollowAsync(IconBounds());

    /// <summary>The icon hid for a full-screen app or came back: the members opened from it do the same.</summary>
    private async void HideFamilyMembers(bool hidden) => await Family.SetHiddenAsync(hidden);

    private FamilyRect IconBounds()
    {
        var position = AppWindow.Position;
        var size = AppWindow.Size;
        return new FamilyRect(position.X, position.Y, size.Width, size.Height);
    }

    private async void OnFamilySlotClicked(object sender, RoutedEventArgs e)
    {
        FamilyEdge? edge = sender switch
        {
            _ when ReferenceEquals(sender, FamilyTop) => FamilyEdge.Top,
            _ when ReferenceEquals(sender, FamilyRight) => FamilyEdge.Right,
            _ when ReferenceEquals(sender, FamilyBottom) => FamilyEdge.Bottom,
            _ when ReferenceEquals(sender, FamilyLeft) => FamilyEdge.Left,
            _ => null,
        };
        FamilyPopup.IsOpen = false;
        if (edge is null)
        {
            return;
        }

        await Family.OpenAsync(edge.Value, IconBounds());
    }
}
