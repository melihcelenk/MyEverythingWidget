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
    /// <param name="width">
    /// A fixed width for the dialog when the window is wide enough, or <see langword="null"/> to let it size to its
    /// content between WinUI's 320 px minimum and the window. A fixed width bounds the dialog on both sides, so the
    /// content cannot be laid out wider than the visible dialog.
    /// </param>
    public static void FitToWindow(ContentDialog dialog, XamlRoot root, double? width = null)
    {
        ArgumentNullException.ThrowIfNull(dialog);
        ArgumentNullException.ThrowIfNull(root);

        var available = Math.Max(0, root.Size.Width - (2 * SideGap));
        var usual = width ?? DefaultMinWidth;
        dialog.Resources["ContentDialogMinWidth"] = Math.Min(usual, available);
        dialog.Resources["ContentDialogMaxWidth"] = width is { } fixedWidth ? Math.Min(fixedWidth, available) : available;
        dialog.Resources["ContentDialogMaxHeight"] = Math.Max(0, root.Size.Height - (2 * SideGap));
        if (available < usual)
        {
            dialog.Resources["ContentDialogPadding"] = new Thickness(NarrowPadding);
        }
        else
        {
            dialog.Resources.Remove("ContentDialogPadding");
        }
    }
}
