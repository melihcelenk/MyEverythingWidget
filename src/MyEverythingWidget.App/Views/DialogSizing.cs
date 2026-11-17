using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Keeps a dialog inside the widget with a gap on both sides. WinUI dialogs are at least 320 px wide, wider than a
/// small widget, so they would touch or cross the window edges.
/// </summary>
internal static class DialogSizing
{
    /// <summary>Space kept between the dialog and each side of the window.</summary>
    public const double SideGap = 12;

    /// <summary>Padding inside a dialog that is narrower than its usual width; the default 24 px leaves too little room.</summary>
    public const double NarrowPadding = 12;

    private const double DefaultMinWidth = 320;

    /// <summary>Limits <paramref name="dialog"/> to the width of <paramref name="root"/> minus a gap on each side.</summary>
    public static void FitToWindow(ContentDialog dialog, XamlRoot root)
    {
        ArgumentNullException.ThrowIfNull(dialog);
        ArgumentNullException.ThrowIfNull(root);

        var available = Math.Max(0, root.Size.Width - (2 * SideGap));
        dialog.Resources["ContentDialogMinWidth"] = Math.Min(DefaultMinWidth, available);
        dialog.Resources["ContentDialogMaxWidth"] = available;
        if (available < DefaultMinWidth)
        {
            dialog.Resources["ContentDialogPadding"] = new Thickness(NarrowPadding);
        }
        else
        {
            dialog.Resources.Remove("ContentDialogPadding");
        }
    }
}
