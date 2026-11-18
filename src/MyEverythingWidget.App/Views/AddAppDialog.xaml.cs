using System.ComponentModel;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Presentation;
using Windows.Storage.Pickers;
using WinRT.Interop;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// "Add app" dialog. Code-behind only bridges list selection and the file picker to <see cref="AddAppViewModel"/>.
/// </summary>
public sealed partial class AddAppDialog : ContentDialog
{
    private readonly nint _ownerWindow;

    /// <summary>Creates the dialog for <paramref name="viewModel"/>; <paramref name="ownerWindow"/> parents the file picker.</summary>
    public AddAppDialog(AddAppViewModel viewModel, nint ownerWindow)
    {
        ArgumentNullException.ThrowIfNull(viewModel);

        ViewModel = viewModel;
        _ownerWindow = ownerWindow;
        InitializeComponent();
        ViewModel.PropertyChanged += OnViewModelPropertyChanged;
        Opened += async (_, _) =>
        {
            SearchBox.Focus(Microsoft.UI.Xaml.FocusState.Programmatic);
            await ViewModel.LoadAsync(CancellationToken.None);
        };
        Closed += (_, _) => ViewModel.PropertyChanged -= OnViewModelPropertyChanged;
    }

    /// <summary>Gets the view model.</summary>
    public AddAppViewModel ViewModel { get; }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(AddAppViewModel.SelectedApp) && ViewModel.SelectedApp is null)
        {
            AppList.SelectedItem = null;
        }
    }

    private void OnAppSelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (AppList.SelectedItem is InstalledApp app)
        {
            ViewModel.SelectedApp = app;
        }
    }

    private void OnAppDoubleTapped(object sender, DoubleTappedRoutedEventArgs e)
    {
        if (ViewModel.CanAdd)
        {
            _ = AddAndCloseAsync();
        }
    }

    private async Task AddAndCloseAsync()
    {
        await ViewModel.AddAsync(CancellationToken.None);
        Hide();
    }

    private async void OnAddClicked(ContentDialog sender, ContentDialogButtonClickEventArgs args)
    {
        var deferral = args.GetDeferral();
        try
        {
            await ViewModel.AddAsync(CancellationToken.None);
        }
        finally
        {
            deferral.Complete();
        }
    }

    private async void OnBrowseClicked(object sender, Microsoft.UI.Xaml.RoutedEventArgs e)
    {
        var picker = new FileOpenPicker { SuggestedStartLocation = PickerLocationId.Desktop };
        picker.FileTypeFilter.Add("*");
        InitializeWithWindow.Initialize(picker, _ownerWindow);
        if (await picker.PickSingleFileAsync() is { } file)
        {
            ViewModel.ManualText = file.Path;
        }
    }
}
