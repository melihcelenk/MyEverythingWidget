using Microsoft.UI.Input;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// The corner a card is resized from. Shows the same diagonal double-arrow cursor as a window corner.
/// </summary>
public sealed partial class ResizeGrip : Grid
{
    /// <summary>Creates the grip.</summary>
    public ResizeGrip()
    {
        ProtectedCursor = InputSystemCursor.Create(InputSystemCursorShape.SizeNorthwestSoutheast);
    }

    /// <inheritdoc />
    /// <remarks>Panels have no automation peer of their own; tests and screen readers find the grip through this one.</remarks>
    protected override AutomationPeer OnCreateAutomationPeer() => new FrameworkElementAutomationPeer(this);
}
