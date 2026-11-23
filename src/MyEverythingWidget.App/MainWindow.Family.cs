using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Input;
using MyEverythingWidget.Presentation;
using FamilyEdge = WidgetFamily.Edge;
using FamilyRect = WidgetFamily.PixelRect;

namespace MyEverythingWidget.App;

/// <summary>
/// The widget family menu of the compact icon (MEW-5): right-click shows the installed family widgets on the icon's
/// four sides; clicking one opens it next to the icon. Window-level only; the decisions are in
/// <see cref="FamilyMenuViewModel"/>.
/// </summary>
public sealed partial class MainWindow
{
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
        FamilyPopup.IsOpen = true;
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
