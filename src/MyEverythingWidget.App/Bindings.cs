using Microsoft.UI.Xaml.Controls;
using MyEverythingWidget.Presentation;

namespace MyEverythingWidget.App;

/// <summary>
/// Small conversion functions used from <c>x:Bind</c> expressions.
/// </summary>
public static class Bindings
{
    /// <summary>Returns whether <paramref name="text"/> has any content.</summary>
    public static bool HasText(string? text) => !string.IsNullOrEmpty(text);

    /// <summary>Returns <see cref="Microsoft.UI.Xaml.Visibility.Visible"/> when <paramref name="visible"/> is true.</summary>
    public static Microsoft.UI.Xaml.Visibility VisibleWhen(bool visible) =>
        visible ? Microsoft.UI.Xaml.Visibility.Visible : Microsoft.UI.Xaml.Visibility.Collapsed;

    /// <summary>Maps a view-model severity to the InfoBar severity.</summary>
    public static InfoBarSeverity ToInfoBarSeverity(StatusSeverity severity) => severity switch
    {
        StatusSeverity.Informational => InfoBarSeverity.Informational,
        StatusSeverity.Warning => InfoBarSeverity.Warning,
        StatusSeverity.Error => InfoBarSeverity.Error,
        _ => throw new ArgumentOutOfRangeException(nameof(severity), severity, "Unknown status severity."),
    };
}
