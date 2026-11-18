using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Automation.Provider;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Windows.System;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// One emoji in the icon picker. Much lighter than a <see cref="Button"/> (a text element on a rounded surface), so
/// the grid of emojis lays out quickly; it still reacts to the pointer, the keyboard (Enter, Space) and UI Automation.
/// </summary>
internal sealed partial class EmojiCell : Grid
{
    private static readonly FontFamily EmojiFont = new("Segoe UI Emoji");

    private readonly Action _invoke;

    /// <summary>Creates the cell for <paramref name="emoji"/>; <paramref name="invoke"/> runs when it is chosen.</summary>
    public EmojiCell(string emoji, double size, Action invoke)
    {
        _invoke = invoke;
        Width = size;
        Height = size;
        CornerRadius = (CornerRadius)Application.Current.Resources["ControlCornerRadius"];
        Background = Brush("SubtleFillColorTransparentBrush");
        IsTabStop = true;
        UseSystemFocusVisuals = true;
        Children.Add(new TextBlock
        {
            Text = emoji,
            FontFamily = EmojiFont,
            FontSize = 20,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            IsTextScaleFactorEnabled = false,
        });
        AutomationProperties.SetAutomationId(this, "Emoji_" + emoji);
        AutomationProperties.SetName(this, emoji);

        PointerEntered += (_, _) => Background = Brush("SubtleFillColorSecondaryBrush");
        PointerExited += (_, _) => Background = Brush("SubtleFillColorTransparentBrush");
        PointerPressed += (_, _) => Background = Brush("SubtleFillColorTertiaryBrush");
        Tapped += (_, e) =>
        {
            e.Handled = true;
            _invoke();
        };
        KeyDown += OnKeyDown;
    }

    /// <inheritdoc />
    protected override AutomationPeer OnCreateAutomationPeer() => new EmojiCellAutomationPeer(this);

    /// <summary>Chooses this emoji (used by the automation peer).</summary>
    public void Invoke() => _invoke();

    private static Brush Brush(string key) => (Brush)Application.Current.Resources[key];

    private void OnKeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key is VirtualKey.Enter or VirtualKey.Space)
        {
            e.Handled = true;
            _invoke();
        }
    }

    /// <summary>Presents the cell as a button that can be invoked.</summary>
    private sealed partial class EmojiCellAutomationPeer(EmojiCell owner) : FrameworkElementAutomationPeer(owner), IInvokeProvider
    {
        protected override AutomationControlType GetAutomationControlTypeCore() => AutomationControlType.Button;

        protected override string GetClassNameCore() => nameof(EmojiCell);

        protected override object GetPatternCore(PatternInterface patternInterface) =>
            patternInterface == PatternInterface.Invoke ? this : base.GetPatternCore(patternInterface);

        public void Invoke() => owner.Invoke();
    }
}
