using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Keeps a dialog inside the widget with a gap on both sides. WinUI dialogs are at least 320 px wide, wider than a
/// small widget, so they would touch or cross the window edges.
/// </summary>
internal static class DialogSizing
{
    /// <summary>Space kept between the dialog and every edge of the window.</summary>
    public const double SideGap = 12;

    /// <summary>Padding inside a dialog that is narrower than its usual width; the default 24 px leaves too little room.</summary>
    public const double NarrowPadding = 12;

    private const double DefaultMinWidth = 320;

    /// <summary>
    /// Limits <paramref name="dialog"/> to the size of <paramref name="root"/> minus a gap on every side; content that
    /// does not fit then scrolls inside the dialog.
    /// </summary>
    /// <param name="dialog">The dialog to size.</param>
    /// <param name="root">The window the dialog opens in.</param>
    /// <param name="width">The dialog's width when the window is wide enough; WinUI's own minimum is 320 px.</param>
    public static void FitToWindow(ContentDialog dialog, XamlRoot root, double width = DefaultMinWidth)
    {
        ArgumentNullException.ThrowIfNull(dialog);
        ArgumentNullException.ThrowIfNull(root);

        var available = Math.Max(0, root.Size.Width - (2 * SideGap));
        dialog.Resources["ContentDialogMinWidth"] = Math.Min(width, available);
        dialog.Resources["ContentDialogMaxWidth"] = available;
        dialog.Resources["ContentDialogMaxHeight"] = Math.Max(0, root.Size.Height - (2 * SideGap));
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
