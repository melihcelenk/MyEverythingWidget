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

    /// <summary>Maps a view-model severity to the InfoBar severity.</summary>
    public static InfoBarSeverity ToInfoBarSeverity(StatusSeverity severity) => severity switch
    {
        StatusSeverity.Informational => InfoBarSeverity.Informational,
        StatusSeverity.Warning => InfoBarSeverity.Warning,
        StatusSeverity.Error => InfoBarSeverity.Error,
        _ => throw new ArgumentOutOfRangeException(nameof(severity), severity, "Unknown status severity."),
    };
}
