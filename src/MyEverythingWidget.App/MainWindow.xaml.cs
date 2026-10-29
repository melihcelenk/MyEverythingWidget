using System.ComponentModel;
using Microsoft.UI;
using Microsoft.UI.Composition.SystemBackdrops;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using MyEverythingWidget.App.Interop;
using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Presentation;
using Windows.Graphics;
using WinRT.Interop;

namespace MyEverythingWidget.App;

/// <summary>
/// The widget window. Applies window-level state (bounds, always-on-top, title bar) that the view model
/// cannot reach; all decisions about that state live in <see cref="MainViewModel"/> and Core.
/// </summary>
public sealed partial class MainWindow : Window
{
    /// <summary>Default size in device-independent pixels: the 5x5 grid of 80px cells plus title bar and margins.</summary>
    private static readonly PixelSize DefaultSizeInDips = new(404, 480);

    private const double DefaultDpi = 96.0;

    private readonly nint _windowHandle;
    private readonly OverlappedPresenter _presenter;

    /// <summary>Creates the window for <paramref name="viewModel"/>.</summary>
    public MainWindow(MainViewModel viewModel)
    {
        ArgumentNullException.ThrowIfNull(viewModel);

        ViewModel = viewModel;
        InitializeComponent();

        _windowHandle = WindowNative.GetWindowHandle(this);
        _presenter = OverlappedPresenter.Create();
        _presenter.IsMaximizable = false;
        AppWindow.SetPresenter(_presenter);

        ConfigureTitleBar();
        ApplyBackdropFallback();
        AppWindow.MoveAndResize(ToRectInt32(ResolveStartupBounds()));
        _presenter.IsAlwaysOnTop = ViewModel.IsAlwaysOnTop;

        ViewModel.PropertyChanged += OnViewModelPropertyChanged;
        Closed += OnClosed;
    }

    /// <summary>Gets the view model the window binds to.</summary>
    public MainViewModel ViewModel { get; }

    /// <summary>Restores the window if needed and makes it the foreground window.</summary>
    public void BringToFront()
    {
        if (_presenter.State == OverlappedPresenterState.Minimized)
        {
            _presenter.Restore();
        }

        Activate();
        NativeMethods.SetForegroundWindow(_windowHandle);
    }

    private void ConfigureTitleBar()
    {
        Title = ViewModel.Title;
        ExtendsContentIntoTitleBar = true;
        AppWindow.TitleBar.PreferredHeightOption = TitleBarHeightOption.Collapsed;
        SetTitleBar(TitleBarDragRegion);
    }

    private void ApplyBackdropFallback()
    {
        // Mica needs Windows 11; on Windows 10 use the plain theme background instead of black.
        if (!MicaController.IsSupported())
        {
            SystemBackdrop = null;
            RootGrid.Background = (Microsoft.UI.Xaml.Media.Brush)Application.Current.Resources["ApplicationPageBackgroundThemeBrush"];
        }
    }

    private PixelRect ResolveStartupBounds()
    {
        var workAreas = GetWorkAreas();
        var primaryWorkArea = ToPixelRect(DisplayArea.Primary.WorkArea);
        var scale = NativeMethods.GetDpiForWindow(_windowHandle) / DefaultDpi;
        var defaultSize = new PixelSize(
            (int)Math.Round(DefaultSizeInDips.Width * scale),
            (int)Math.Round(DefaultSizeInDips.Height * scale));

        return WindowPlacement.Resolve(ViewModel.SavedWindowBounds, workAreas, primaryWorkArea, defaultSize);
    }

    private static List<PixelRect> GetWorkAreas()
    {
        // DisplayArea.FindAll() cannot be enumerated with foreach/LINQ (its projection lacks IEnumerable);
        // index it instead.
        var displayAreas = DisplayArea.FindAll();
        var workAreas = new List<PixelRect>(displayAreas.Count);
        for (var index = 0; index < displayAreas.Count; index++)
        {
            workAreas.Add(ToPixelRect(displayAreas[index].WorkArea));
        }

        return workAreas;
    }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(MainViewModel.IsAlwaysOnTop))
        {
            _presenter.IsAlwaysOnTop = ViewModel.IsAlwaysOnTop;
        }
    }

    private void OnCloseClicked(object sender, RoutedEventArgs e) => Close();

    private void OnClosed(object sender, WindowEventArgs args)
    {
        ViewModel.PropertyChanged -= OnViewModelPropertyChanged;
        var position = AppWindow.Position;
        var size = AppWindow.Size;
        ViewModel.SaveWindowBounds(new PixelRect(position.X, position.Y, size.Width, size.Height));
    }

    private static PixelRect ToPixelRect(RectInt32 rect) => new(rect.X, rect.Y, rect.Width, rect.Height);

    private static RectInt32 ToRectInt32(PixelRect rect) => new(rect.X, rect.Y, rect.Width, rect.Height);
}
