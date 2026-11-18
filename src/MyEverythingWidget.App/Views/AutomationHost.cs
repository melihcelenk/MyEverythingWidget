using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Wraps a purely visual element (Border, Panel) so it appears in the UI Automation tree with its
/// AutomationId, Name and HelpText, for screen readers and UI tests.
/// </summary>
public sealed partial class AutomationHost : UserControl
{
    /// <inheritdoc />
    protected override AutomationPeer OnCreateAutomationPeer() => new FrameworkElementAutomationPeer(this);
}
