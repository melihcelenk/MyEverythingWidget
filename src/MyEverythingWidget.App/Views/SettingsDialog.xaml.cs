using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Presentation;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Settings: theme, always on top, and the About section. Changes apply immediately.
/// </summary>
public sealed partial class SettingsDialog : ContentDialog
{
    private readonly MainViewModel _viewModel;
    private bool _isLoading = true;

    /// <summary>Creates the dialog for <paramref name="viewModel"/>.</summary>
    public SettingsDialog(MainViewModel viewModel)
    {
        ArgumentNullException.ThrowIfNull(viewModel);

        _viewModel = viewModel;
        InitializeComponent();

        VersionText.Text = $"{viewModel.Title} {viewModel.Version}";
        AlwaysOnTopSwitch.IsOn = viewModel.IsAlwaysOnTop;
        (viewModel.Theme switch
        {
            AppTheme.Light => ThemeLight,
            AppTheme.Dark => ThemeDark,
            _ => ThemeSystem,
        }).IsChecked = true;
        _isLoading = false;
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
