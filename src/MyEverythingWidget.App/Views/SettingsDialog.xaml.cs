using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Presentation;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Settings: language, theme, always on top, and the About section. Changes apply immediately; a new language
/// restarts the app (<see cref="RestartRequested"/>). A cross at the top right, Esc or a click outside closes it.
/// </summary>
public sealed partial class SettingsDialog : ContentDialog
{
    /// <summary>The dialog's width when the widget is wide enough: 252 px of content and 24 px padding on each side.</summary>
    public const double PreferredWidth = 300;

    private const string Email = "info@melihcelenk.com";
    private const string EmailGlyph = "\u2709";
    private const string CopiedGlyph = "\u2714";

    /// <summary>Padding above the header: the cross sits close to the dialog's top edge.</summary>
    private const double HeaderTopPadding = 8;

    /// <summary>Space between the cross and the dialog's right edge.</summary>
    private const double CrossEdgeGap = 4;

    /// <summary>Space WinUI leaves between a box and the flyout opened under it.</summary>
    private const double ListGap = 4;

    /// <summary>Padding above and below the language list inside its flyout.</summary>
    private const double ListVerticalPadding = 2;

    /// <summary>Border of the flyout around the language list.</summary>
    private const double ListBorder = 1;

    /// <summary>The list never shrinks below three rows, even when the About card ends right under the box.</summary>
    private const double MinimumListHeight = 120;

    /// <summary>Name of the dialog's visible box in WinUI's template; the dialog itself covers the whole window.</summary>
    private const string BoxPartName = "BackgroundElement";
    private static readonly Uri Personal = new("https://melihcelenk.com/");
    private static readonly Uri Website = new("https://melihcelenk.github.io/MyEverythingWidget/");

    /// <summary>The app's Microsoft Store page (Store ID 9NRSQN57C9FH), where it can be rated.</summary>
    private static readonly Uri Rate = new("https://apps.microsoft.com/detail/9NRSQN57C9FH");
    private static readonly TimeSpan CopiedFeedback = TimeSpan.FromSeconds(1.5);

    private readonly MainViewModel _viewModel;

    /// <summary>Kept in a field: a timer only referenced from a local variable can be collected before it fires.</summary>
    private DispatcherQueueTimer? _copiedTimer;
    private bool _isLoading = true;

    /// <summary>The dialog's visible box, to tell a click on it from a click on the window around it.</summary>
    private FrameworkElement? _box;

    /// <summary>Elements of the open popups (the dialog and the dimmed layer around it) that report clicks.</summary>
    private readonly List<UIElement> _clickSources = [];

    private readonly PointerEventHandler _pointerPressed;

    /// <summary>Raised when the user picked another language; the app restarts to show it.</summary>
    public event EventHandler? RestartRequested;

    /// <summary>Creates the dialog for <paramref name="viewModel"/>.</summary>
    public SettingsDialog(MainViewModel viewModel)
    {
        ArgumentNullException.ThrowIfNull(viewModel);

        _viewModel = viewModel;
        InitializeComponent();
        _pointerPressed = OnPointerPressedAnywhere;
        Opened += OnOpened;
        Closed += OnClosed;

        AppNameText.Text = viewModel.Title;
        VersionText.Text = Strings.Version(viewModel.Version);
        ShowEmail();
        Describe(EmailButton, Strings.CopyEmail(Email));
        FillLanguages(viewModel.Language);
        Link(PersonalLink, Personal);
        Link(WebsiteLink, Website);
        Link(RateLink, Rate);
        AlwaysOnTopSwitch.IsOn = viewModel.IsAlwaysOnTop;
        (viewModel.Theme switch
        {
            AppTheme.Light => ThemeLight,
            AppTheme.Dark => ThemeDark,
            _ => ThemeSystem,
        }).IsChecked = true;
        _isLoading = false;
    }

    private static void Link(HyperlinkButton link, Uri target)
    {
        link.NavigateUri = target;
        Describe(link, target.OriginalString);
    }

    /// <summary>Shows <paramref name="text"/> when the pointer rests on <paramref name="link"/>: where it leads.</summary>
    private static void Describe(FrameworkElement link, string text)
    {
        ToolTipService.SetToolTip(link, text);
        AutomationProperties.SetHelpText(link, text);
    }

    private void ShowEmail()
    {
        EmailText.Text = Email;
        EmailIcon.Text = EmailGlyph;
        AutomationProperties.SetName(EmailButton, Email);
    }

    /// <summary>Copies the e-mail address and shows "Copied" for a moment.</summary>
    private void OnEmailClicked(object sender, RoutedEventArgs e)
    {
        var package = new Windows.ApplicationModel.DataTransfer.DataPackage();
        package.SetText(Email);
        Windows.ApplicationModel.DataTransfer.Clipboard.SetContent(package);
        Windows.ApplicationModel.DataTransfer.Clipboard.Flush();

        EmailText.Text = Strings.Copied;
        EmailIcon.Text = CopiedGlyph;
        AutomationProperties.SetName(EmailButton, Strings.Copied);

        if (_copiedTimer is null)
        {
            _copiedTimer = DispatcherQueue.CreateTimer();
            _copiedTimer.Interval = CopiedFeedback;
            _copiedTimer.IsRepeating = false;
            _copiedTimer.Tick += (_, _) => ShowEmail();
        }

        _copiedTimer.Stop();
        _copiedTimer.Start();
    }

    private void OnThemeChecked(object sender, RoutedEventArgs e)
    {
        if (_isLoading)
        {
            return;
        }

        _viewModel.Theme = ReferenceEquals(sender, ThemeLight) ? AppTheme.Light
            : ReferenceEquals(sender, ThemeDark) ? AppTheme.Dark
            : AppTheme.System;
    }

    private void OnAlwaysOnTopToggled(object sender, RoutedEventArgs e)
    {
        if (!_isLoading && AlwaysOnTopSwitch.IsOn != _viewModel.IsAlwaysOnTop)
        {
            _viewModel.ToggleAlwaysOnTopCommand.Execute(null);
        }
    }

    /// <summary>
    /// Sizes the dialog for <paramref name="root"/> and moves the header up to the top edge, with the cross in the
    /// top-right corner.
    /// </summary>
    public void FitTo(XamlRoot root)
    {
        ArgumentNullException.ThrowIfNull(root);

        // The right padding is only the cross's gap; the settings below keep the usual padding with a margin.
        var side = DialogSizing.FitToWindow(this, root, PreferredWidth);
        Resources["ContentDialogPadding"] = new Thickness(side, HeaderTopPadding, CrossEdgeGap, side);
        ContentScroller.Margin = new Thickness(0, 0, side - CrossEdgeGap, 0);
    }

    /// <summary>"System language" first, then every language under its own name.</summary>
    private void FillLanguages(string? chosen)
    {
        LanguageList.Items.Add(Strings.LanguageSystem);
        foreach (var language in AppLanguages.Supported)
        {
            LanguageList.Items.Add(language.NativeName);
        }

        var index = AppLanguages.Supported.ToList().FindIndex(language => language.Code == chosen) + 1;
        LanguageList.SelectedIndex = index;
        LanguageText.Text = (string)LanguageList.Items[index];
    }

    /// <summary>
    /// The list is as wide as the box and reaches from under the box to the bottom of the About card; languages that
    /// do not fit scroll.
    /// </summary>
    private void OnLanguageListOpening(object? sender, object e)
    {
        var boxBottom = LanguageChoice.TransformToVisual(AboutCard).TransformPoint(new Windows.Foundation.Point(0, LanguageChoice.ActualHeight)).Y;
        var presenterChrome = (2 * ListVerticalPadding) + (2 * ListBorder);
        LanguageList.Width = Math.Max(0, LanguageChoice.ActualWidth - (2 * ListBorder));
        LanguageList.Height = Math.Max(MinimumListHeight, AboutCard.ActualHeight - boxBottom - ListGap - presenterChrome);
    }

    private void OnLanguageListOpened(object? sender, object e)
    {
        if (LanguageList.SelectedItem is { } chosen)
        {
            LanguageList.ScrollIntoView(chosen);
        }
    }

    private void OnLanguagePicked(object sender, SelectionChangedEventArgs e)
    {
        if (_isLoading || LanguageList.SelectedIndex < 0)
        {
            return;
        }

        LanguageText.Text = (string)LanguageList.Items[LanguageList.SelectedIndex];
        LanguageFlyout.Hide();
        var code = LanguageList.SelectedIndex == 0 ? null : AppLanguages.Supported[LanguageList.SelectedIndex - 1].Code;
        if (_viewModel.SetLanguage(code))
        {
            Hide();
            RestartRequested?.Invoke(this, EventArgs.Empty);
        }
    }

    private void OnCloseClicked(object sender, RoutedEventArgs e) => Hide();

    /// <inheritdoc />
    protected override void OnApplyTemplate()
    {
        base.OnApplyTemplate();
        _box = GetTemplateChild(BoxPartName) as FrameworkElement;
    }

    /// <summary>
    /// Listens to clicks on every open popup of the window: the dimmed layer around the dialog is a popup of its own, so
    /// a click on it does not reach the dialog.
    /// </summary>
    private void OnOpened(ContentDialog sender, ContentDialogOpenedEventArgs args)
    {
        foreach (var popup in Microsoft.UI.Xaml.Media.VisualTreeHelper.GetOpenPopupsForXamlRoot(XamlRoot))
        {
            if (popup.Child is { } child)
            {
                child.AddHandler(PointerPressedEvent, _pointerPressed, handledEventsToo: true);
                _clickSources.Add(child);
            }
        }
    }

    private void OnClosed(ContentDialog sender, ContentDialogClosedEventArgs args)
    {
        foreach (var source in _clickSources)
        {
            source.RemoveHandler(PointerPressedEvent, _pointerPressed);
        }

        _clickSources.Clear();
    }

    /// <summary>A click on the dimmed window around the dialog closes it.</summary>
    private void OnPointerPressedAnywhere(object sender, PointerRoutedEventArgs e)
    {
        if (_box is null)
        {
            return;
        }

        var point = e.GetCurrentPoint(_box).Position;
        if (point.X < 0 || point.Y < 0 || point.X > _box.ActualWidth || point.Y > _box.ActualHeight)
        {
            Hide();
        }
    }
}
