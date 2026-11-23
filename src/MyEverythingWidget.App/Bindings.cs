using Microsoft.UI.Xaml.Controls;
using MyEverythingWidget.Presentation;
using MyEverythingWidget.Presentation.Localization;

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

    /// <summary>Returns <see cref="Microsoft.UI.Xaml.Visibility.Collapsed"/> when <paramref name="hidden"/> is true.</summary>
    public static Microsoft.UI.Xaml.Visibility VisibleUnless(bool hidden) => VisibleWhen(!hidden);

    /// <summary>Visible when a family member sits on that side of the compact icon.</summary>
    public static Microsoft.UI.Xaml.Visibility VisibleWhenSlot(FamilySlot? slot) => VisibleWhen(slot is not null);

    /// <summary>The name of the family member on a side of the compact icon, or nothing.</summary>
    public static string SlotName(FamilySlot? slot) => slot?.Name ?? string.Empty;

    /// <summary>The text of the button that downloads the family widget <paramref name="name"/>.</summary>
    public static string DownloadText(string name) => Strings.FamilyGet(name);

    /// <summary>The automation id of the button that downloads the family widget <paramref name="memberId"/>.</summary>
    public static string DownloadId(string memberId) => "FamilyGet_" + memberId;

    /// <summary>Visible when the notice shows or there is anything to download.</summary>
    public static Microsoft.UI.Xaml.Visibility VisibleWhenAny(bool showsNotice, IReadOnlyList<FamilyOffer> downloads) =>
        VisibleWhen(showsNotice || downloads is { Count: > 0 });

    /// <summary>Maps a view-model severity to the InfoBar severity.</summary>
    public static InfoBarSeverity ToInfoBarSeverity(StatusSeverity severity) => severity switch
    {
        StatusSeverity.Informational => InfoBarSeverity.Informational,
        StatusSeverity.Warning => InfoBarSeverity.Warning,
        StatusSeverity.Error => InfoBarSeverity.Error,
        _ => throw new ArgumentOutOfRangeException(nameof(severity), severity, "Unknown status severity."),
    };
}
