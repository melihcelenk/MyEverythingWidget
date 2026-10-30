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
    /// <summary>
    /// Fixed client-area size in device-independent pixels: the 5x5 grid of 80px cells (400) plus margins, the
    /// title bar (40), the category tabs (40) and room for the status bar.
    /// </summary>
    private static readonly PixelSize ClientSizeInDips = new(412, 560);

    private const double DefaultDpi = 96.0;

    private readonly nint _windowHandle;
    private readonly OverlappedPresenter _presenter;

    /// <summary>Creates the window for <paramref name="viewModel"/> showing <paramref name="board"/>.</summary>
    public MainWindow(MainViewModel viewModel, BoardViewModel board)
    {
        ArgumentNullException.ThrowIfNull(viewModel);
        ArgumentNullException.ThrowIfNull(board);

        ViewModel = viewModel;
        Board = board;
        InitializeComponent();
        GridView.Board = board;

        _windowHandle = WindowNative.GetWindowHandle(this);
        _presenter = OverlappedPresenter.Create();
        _presenter.IsMaximizable = false;
        _presenter.IsResizable = false;
        AppWindow.SetPresenter(_presenter);

        ConfigureTitleBar();
        ApplyBackdropFallback();
        var clientSize = ScaledClientSize();
        AppWindow.ResizeClient(new SizeInt32(clientSize.Width, clientSize.Height));
        var bounds = ResolveStartupBounds();
        AppWindow.Move(new PointInt32(bounds.X, bounds.Y));
        _presenter.IsAlwaysOnTop = ViewModel.IsAlwaysOnTop;

        ViewModel.PropertyChanged += OnViewModelPropertyChanged;
        Closed += OnClosed;

        // Start with programmatic focus on the grid, so no keyboard focus rectangle shows on the title bar buttons.
        RootGrid.Loaded += (_, _) => GridView.Focus(FocusState.Programmatic);
    }

    /// <summary>Gets the view model the window binds to.</summary>
    public MainViewModel ViewModel { get; }

    /// <summary>Gets the grid view model the window binds to.</summary>
    public BoardViewModel Board { get; }

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
        var size = new PixelSize(AppWindow.Size.Width, AppWindow.Size.Height);

        // The window has a fixed size; only the saved position is kept.
        var saved = ViewModel.SavedWindowBounds is { } bounds
            ? new PixelRect(bounds.X, bounds.Y, size.Width, size.Height)
            : (PixelRect?)null;
        return WindowPlacement.Resolve(saved, workAreas, primaryWorkArea, size);
    }

    private PixelSize ScaledClientSize()
    {
        var scale = NativeMethods.GetDpiForWindow(_windowHandle) / DefaultDpi;
        return new PixelSize(
            (int)Math.Round(ClientSizeInDips.Width * scale),
            (int)Math.Round(ClientSizeInDips.Height * scale));
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
