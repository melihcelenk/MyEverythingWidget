using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Presentation;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Settings: theme, always on top, and the About section. Changes apply immediately.
/// </summary>
public sealed partial class SettingsDialog : ContentDialog
{
    private const string Email = "info@melihcelenk.com";
    private const string CopiedText = "Copied";
    private const string EmailGlyph = "";
    private const string CopiedGlyph = "";
    private static readonly Uri Website = new("https://melihcelenk.com/");
    private static readonly Uri SourceCode = new("https://github.com/melihcelenk/MyEverythingWidget");
    private static readonly TimeSpan CopiedFeedback = TimeSpan.FromSeconds(1.5);

    private readonly MainViewModel _viewModel;

    /// <summary>Kept in a field: a timer only referenced from a local variable can be collected before it fires.</summary>
    private DispatcherQueueTimer? _copiedTimer;
    private bool _isLoading = true;

    /// <summary>Creates the dialog for <paramref name="viewModel"/>.</summary>
    public SettingsDialog(MainViewModel viewModel)
    {
        ArgumentNullException.ThrowIfNull(viewModel);

        _viewModel = viewModel;
        InitializeComponent();

        AppNameText.Text = viewModel.Title;
        VersionText.Text = $"Version {viewModel.Version}";
        ShowEmail();
        Describe(EmailButton, $"Copy {Email}");
        WebsiteLink.NavigateUri = Website;
        Describe(WebsiteLink, Website.ToString());
        SourceLink.NavigateUri = SourceCode;
        Describe(SourceLink, SourceCode.ToString());
        AlwaysOnTopSwitch.IsOn = viewModel.IsAlwaysOnTop;
        (viewModel.Theme switch
        {
            AppTheme.Light => ThemeLight,
            AppTheme.Dark => ThemeDark,
            _ => ThemeSystem,
        }).IsChecked = true;
        _isLoading = false;
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
        EmailIcon.Glyph = EmailGlyph;
        AutomationProperties.SetName(EmailButton, Email);
    }

    /// <summary>Copies the e-mail address and shows "Copied" for a moment.</summary>
    private void OnEmailClicked(object sender, RoutedEventArgs e)
    {
        var package = new Windows.ApplicationModel.DataTransfer.DataPackage();
        package.SetText(Email);
        Windows.ApplicationModel.DataTransfer.Clipboard.SetContent(package);
        Windows.ApplicationModel.DataTransfer.Clipboard.Flush();

        EmailText.Text = CopiedText;
        EmailIcon.Glyph = CopiedGlyph;
        AutomationProperties.SetName(EmailButton, CopiedText);

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
}
