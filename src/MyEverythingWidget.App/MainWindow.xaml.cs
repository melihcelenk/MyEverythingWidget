using System.ComponentModel;
using Microsoft.UI;
using Microsoft.UI.Composition.SystemBackdrops;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using MyEverythingWidget.App.Interop;
using MyEverythingWidget.App.Views;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Presentation;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Windows.ApplicationModel.DataTransfer;
using Windows.Storage.Pickers;
using Windows.Graphics;
using WinRT.Interop;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.App;

/// <summary>
/// The widget window. Applies window-level state (bounds, always-on-top, title bar) that the view model
/// cannot reach; all decisions about that state live in <see cref="MainViewModel"/> and Core.
/// </summary>
public sealed partial class MainWindow : Window
{
    /// <summary>
    /// Client area around the grid, in device-independent pixels: grid margins (6 on each side), the one-row title bar
    /// (40) and the bottom bar (44). Must match the row heights and margins in MainWindow.xaml.
    /// </summary>
    private static readonly GridWindowSizing Sizing = new(GridMetrics.CellSize, ChromeWidth: 12, ChromeHeight: 96);

    /// <summary>Compact mode shows the 48 px logo with an 8 px frame around it.</summary>
    private const double CompactSizeInDips = 64;

    private readonly nint _windowHandle;
    private readonly OverlappedPresenter _presenter;

    private readonly IInstalledAppsSource _installedApps;
    private readonly CellSnappingResizer _resizer;

    /// <summary>Hides the compact icon while a video, game or presentation fills its monitor.</summary>
    private readonly FullScreenWatcher _fullScreenWatcher;
    private NativeMethods.NativePoint? _compactPressCursor;
    private PointInt32 _compactPressWindow;
    private bool _compactDragged;

    /// <summary>
    /// The icon corner the widget last opened from, and where it opened; shrinking the unmoved widget goes back to
    /// that corner so the icon returns to exactly where it was.
    /// </summary>
    private (WindowCorner Corner, PixelRect Widget)? _openedFrom;
    private ImageViewerWindow? _imageViewer;

    /// <summary>Creates the window for <paramref name="viewModel"/> showing <paramref name="board"/>.</summary>
    public MainWindow(MainViewModel viewModel, BoardViewModel board, IInstalledAppsSource installedApps)
    {
        ArgumentNullException.ThrowIfNull(viewModel);
        ArgumentNullException.ThrowIfNull(board);
        ArgumentNullException.ThrowIfNull(installedApps);

        ViewModel = viewModel;
        Board = board;
        _installedApps = installedApps;
        InitializeComponent();
        GridView.Board = board;
        GridView.ItemInvoked += (_, item) => OnItemInvoked(item);
        TabsView.Board = board;

        _windowHandle = WindowNative.GetWindowHandle(this);
        _presenter = OverlappedPresenter.Create();
        _presenter.IsMaximizable = false;
        _presenter.IsResizable = true;
        AppWindow.SetPresenter(_presenter);
        GridView.OwnerWindowHandle = _windowHandle;
        _resizer = new CellSnappingResizer(
            _windowHandle,
            Sizing,
            Board.ResizeGrid,
            () => Board.MinimumGridSize,
            () => ViewModel.IsCompact ? CompactClientSize() : null,
            () => ViewModel.SaveGridSize(Board.GridSize));
        _fullScreenWatcher = new FullScreenWatcher(_windowHandle, DispatcherQueue);
        _fullScreenWatcher.CoveredChanged += OnFullScreenChanged;

        ConfigureTitleBar();
        ApplyBackdropFallback();
        ApplyLayoutMode();
        var bounds = ResolveStartupBounds();
        AppWindow.Move(new PointInt32(bounds.X, bounds.Y));
        ApplyAlwaysOnTop();
        ApplyTheme();

        CompactIcon.AddHandler(UIElement.PointerPressedEvent, new PointerEventHandler(OnCompactPointerPressed), handledEventsToo: true);
        CompactIcon.AddHandler(UIElement.PointerMovedEvent, new PointerEventHandler(OnCompactPointerMoved), handledEventsToo: true);
        CompactIcon.AddHandler(UIElement.PointerReleasedEvent, new PointerEventHandler(OnCompactPointerReleased), handledEventsToo: true);

        ViewModel.PropertyChanged += OnViewModelPropertyChanged;

        // Coming back to the widget after editing an image in Paint shows the saved change.
        Activated += (_, e) =>
        {
            if (e.WindowActivationState != WindowActivationState.Deactivated)
            {
                GridView.RefreshChangedImages();
            }
        };
        Closed += OnClosed;

        // Start with programmatic focus on the grid, so no keyboard focus rectangle shows on the title bar buttons.
        RootGrid.Loaded += (_, _) =>
        {
            GridView.Focus(FocusState.Programmatic);
            EmojiFontWarmUp.Start(WarmUpLayer, () => IconPickerDialog.Prepare(RootGrid.XamlRoot));
        };
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
        AppWindow.SetIcon(Path.Combine(AppContext.BaseDirectory, "app.ico"));
        ExtendsContentIntoTitleBar = true;
        AppWindow.TitleBar.PreferredHeightOption = TitleBarHeightOption.Collapsed;
        SetTitleBar(TabsView.DragRegion);
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

    private PixelSize CompactClientSize()
    {
        var side = (int)Math.Round(CompactSizeInDips * _resizer.Scale);
        return new PixelSize(side, side);
    }

    /// <summary>
    /// Shows the widget or its one-cell icon and sizes the window for it. The visible top-left corner stays where it
    /// was; the opened widget is then kept entirely on the icon's monitor.
    /// </summary>
    private void ApplyLayoutMode()
    {
        var compact = ViewModel.IsCompact;
        var corner = _resizer.ClientBounds();
        ExpandedView.Visibility = compact ? Visibility.Collapsed : Visibility.Visible;
        CompactIcon.Visibility = compact ? Visibility.Visible : Visibility.Collapsed;
        _presenter.IsResizable = !compact;

        // Windows keeps a framed window at least ~136 px wide, so the one-cell icon drops the frame and caption.
        _presenter.SetBorderAndTitleBar(hasBorder: !compact, hasTitleBar: !compact);

        var client = compact ? CompactClientSize() : Sizing.ClientSize(Board.GridSize, _resizer.Scale);
        _resizer.ResizeClient(client);

        var workArea = ToPixelRect(DisplayArea.GetFromPoint(new PointInt32(corner.X, corner.Y), DisplayAreaFallback.Nearest).WorkArea);
        PixelRect target;
        if (compact)
        {
            // Back to the corner the widget opened from, unless the user has moved it since.
            var side = _openedFrom is { } opened && opened.Widget == corner ? opened.Corner : WindowPlacement.NearestCorner(corner, workArea);
            target = WindowPlacement.AlignCorner(corner, client, side);
        }
        else
        {
            // The widget opens from the icon's corner nearest the screen corner, so it grows into the screen.
            var side = WindowPlacement.NearestCorner(corner, workArea);
            target = WindowPlacement.FitInside(WindowPlacement.AlignCorner(corner, client, side), workArea);
            _openedFrom = (side, target);
        }

        _resizer.MoveClientTo(target.X, target.Y);
        ApplyAlwaysOnTop();
        if (compact)
        {
            _fullScreenWatcher.Start();
        }
        else
        {
            _fullScreenWatcher.Stop();
        }

        if (compact)
        {
            // Loaded on first use only: the widget's start-up should not pay for an image it does not show.
            CompactLogo.Source ??= new Microsoft.UI.Xaml.Media.Imaging.BitmapImage(
                new Uri(Path.Combine(AppContext.BaseDirectory, "Assets", "Square44x44Logo.targetsize-48.png")));
            CompactIcon.Focus(FocusState.Programmatic);
        }
    }

    /// <summary>
    /// The compact icon steps aside while a video, game or presentation fills its monitor, and comes back on top when
    /// that window leaves full screen or the user switches away from it.
    /// </summary>
    private void OnFullScreenChanged(object? sender, bool covered)
    {
        if (covered)
        {
            AppWindow.Hide();
        }
        else if (!AppWindow.IsVisible)
        {
            AppWindow.Show(activateWindow: false);
            ApplyAlwaysOnTop();
        }
    }

    /// <summary>The compact icon is always on top; the widget follows the pin setting.</summary>
    private void ApplyAlwaysOnTop() => _presenter.IsAlwaysOnTop = ViewModel.IsCompact || ViewModel.IsAlwaysOnTop;

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
            ApplyAlwaysOnTop();
        }
        else if (e.PropertyName == nameof(MainViewModel.Theme))
        {
            ApplyTheme();
        }
        else if (e.PropertyName == nameof(MainViewModel.IsCompact))
        {
            ApplyLayoutMode();
        }
    }

    private void OnCompactIconClicked(object sender, RoutedEventArgs e)
    {
        // A drag ends with the pointer still over the icon, which the button reports as a click.
        if (_compactDragged)
        {
            _compactDragged = false;
            return;
        }

        if (ViewModel.IsCompact)
        {
            ViewModel.ToggleCompactCommand.Execute(null);
        }
    }

    private void OnCompactPointerPressed(object sender, PointerRoutedEventArgs e)
    {
        if (!e.GetCurrentPoint(CompactIcon).Properties.IsLeftButtonPressed)
        {
            return;
        }

        NativeMethods.GetCursorPos(out var cursor);
        _compactPressCursor = cursor;
        _compactPressWindow = AppWindow.Position;
        _compactDragged = false;
        CompactIcon.CapturePointer(e.Pointer);
    }

    /// <summary>
    /// Dragging the compact icon moves the window with the cursor; screen coordinates are used because the window
    /// itself moves under the pointer.
    /// </summary>
    private void OnCompactPointerMoved(object sender, PointerRoutedEventArgs e)
    {
        if (_compactPressCursor is not { } start)
        {
            return;
        }

        NativeMethods.GetCursorPos(out var cursor);
        var dx = cursor.X - start.X;
        var dy = cursor.Y - start.Y;
        var threshold = GridMetrics.DragThreshold * _resizer.Scale;
        if (!_compactDragged && Math.Abs(dx) < threshold && Math.Abs(dy) < threshold)
        {
            return;
        }

        _compactDragged = true;
        AppWindow.Move(new PointInt32(_compactPressWindow.X + dx, _compactPressWindow.Y + dy));
    }

    private void OnCompactPointerReleased(object sender, PointerRoutedEventArgs e)
    {
        _compactPressCursor = null;
        CompactIcon.ReleasePointerCaptures();
    }

    private void OnCloseClicked(object sender, RoutedEventArgs e) => Close();

    /// <summary>A click on an app card opens it; on an image card it shows the image large.</summary>
    private void OnItemInvoked(GridItemViewModel item)
    {
        if (item.Kind != Core.Grid.ItemKind.Image)
        {
            Board.Launch(item.Id);
            return;
        }

        if (DataFiles.Resolve(item.ImagePath) is not { } imageFile)
        {
            return;
        }

        _imageViewer?.Close();
        var workArea = ToPixelRect(DisplayArea.GetFromWindowId(AppWindow.Id, DisplayAreaFallback.Nearest).WorkArea);
        var viewer = new ImageViewerWindow(imageFile, new PixelSize(item.ImagePixelWidth, item.ImagePixelHeight), workArea, RootGrid.ActualTheme);
        viewer.Closed += (_, _) =>
        {
            if (ReferenceEquals(_imageViewer, viewer))
            {
                _imageViewer = null;
            }
        };
        _imageViewer = viewer;
        viewer.Activate();
    }

    /// <summary>Applies the theme to the whole window (dialogs and flyouts follow the content root).</summary>
    private void ApplyTheme() => RootGrid.RequestedTheme = ViewModel.Theme switch
    {
        AppTheme.Light => ElementTheme.Light,
        AppTheme.Dark => ElementTheme.Dark,
        _ => ElementTheme.Default,
    };

    private async void OnSettingsClicked(object sender, RoutedEventArgs e)
    {
        var dialog = new SettingsDialog(ViewModel) { XamlRoot = RootGrid.XamlRoot, RequestedTheme = RootGrid.ActualTheme };
        dialog.FitTo(RootGrid.XamlRoot);
        dialog.RestartRequested += (_, _) => RestartRequested?.Invoke(this, EventArgs.Empty);
        void FollowTheme(object? s, System.ComponentModel.PropertyChangedEventArgs args)
        {
            if (args.PropertyName == nameof(MainViewModel.Theme))
            {
                dialog.RequestedTheme = RootGrid.RequestedTheme == ElementTheme.Default ? ElementTheme.Default : RootGrid.RequestedTheme;
            }
        }

        ViewModel.PropertyChanged += FollowTheme;
        await dialog.ShowAsync();
        ViewModel.PropertyChanged -= FollowTheme;

        // The dialog returns keyboard focus to the Settings button, which then shows its tooltip over the grid until
        // the user does something else; give the focus back to the grid instead.
        GridView.Focus(FocusState.Programmatic);
    }

    private async void OnAddAppClicked(object sender, RoutedEventArgs e)
    {
        var dialog = new AddAppDialog(new AddAppViewModel(Board, _installedApps, Directory.Exists), _windowHandle)
        {
            XamlRoot = RootGrid.XamlRoot,
        };
        DialogSizing.FitToWindow(dialog, RootGrid.XamlRoot);
        await dialog.ShowAsync();
    }

    private async void OnAddNoteClicked(object sender, RoutedEventArgs e)
    {
        if (await TextEditorDialog.ShowAsync(RootGrid.XamlRoot, Strings.AddNote, "", multiline: true) is { } text)
        {
            Board.AddNote(text);
        }
    }

    private async void OnAddImageClicked(object sender, RoutedEventArgs e)
    {
        var picker = new FileOpenPicker { SuggestedStartLocation = PickerLocationId.PicturesLibrary };
        foreach (var extension in new[] { ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp" })
        {
            picker.FileTypeFilter.Add(extension);
        }

        InitializeWithWindow.Initialize(picker, _windowHandle);
        if (await picker.PickSingleFileAsync() is { } file)
        {
            await Board.AddImageFileAsync(file.Path);
        }
    }

    /// <summary>Ctrl+V anywhere in the window, except in a text box, which pastes into itself.</summary>
    private async void OnPasteInvoked(KeyboardAccelerator sender, KeyboardAcceleratorInvokedEventArgs args)
    {
        // A text box pastes into itself; an open dialog (such as the icon dialog) handles its own paste.
        if (FocusManager.GetFocusedElement(RootGrid.XamlRoot) is TextBox
            || Microsoft.UI.Xaml.Media.VisualTreeHelper.GetOpenPopupsForXamlRoot(RootGrid.XamlRoot).Any(popup => popup.Child is ContentDialog))
        {
            return;
        }

        args.Handled = true;
        var content = await ClipboardReader.ReadAsync(Clipboard.GetContent());
        await Board.PasteAsync(content, Directory.Exists);
    }

    private void OnGridDragOver(object sender, DragEventArgs e)
    {
        var data = e.DataView;
        if (data.Contains(StandardDataFormats.StorageItems) || data.Contains(StandardDataFormats.Bitmap)
            || data.Contains(StandardDataFormats.WebLink) || data.Contains(StandardDataFormats.Text))
        {
            e.AcceptedOperation = DataPackageOperation.Link;
            e.DragUIOverride.Caption = Strings.AddToWidget;
        }
    }

    /// <summary>Turns dropped files, folders and links into app cards.</summary>
    private async void OnGridDrop(object sender, DragEventArgs e)
    {
        var deferral = e.GetDeferral();
        try
        {
            var data = e.DataView;

            // A picture dragged from a web page or an app carries the image itself; files and links take the other path.
            if (data.Contains(StandardDataFormats.Bitmap) && !data.Contains(StandardDataFormats.StorageItems))
            {
                await Board.AddDroppedPictureAsync(async _ =>
                    (await (await data.GetBitmapAsync()).OpenReadAsync()).AsStreamForRead());
                return;
            }

            var texts = await DroppedTexts.ReadAsync(data);
            if (texts.Count > 0)
            {
                await Board.AddDroppedAsync(texts, Directory.Exists);
            }
        }
        finally
        {
            deferral.Complete();
        }
    }

    /// <summary>Raised when the app should restart, to show a newly chosen language.</summary>
    public event EventHandler? RestartRequested;

    /// <summary>Records where the window is, so the next start reopens it there.</summary>
    public void SaveWindowBounds()
    {
        var position = AppWindow.Position;
        var size = AppWindow.Size;
        ViewModel.SaveWindowBounds(new PixelRect(position.X, position.Y, size.Width, size.Height));
    }

    private void OnClosed(object sender, WindowEventArgs args)
    {
        ViewModel.PropertyChanged -= OnViewModelPropertyChanged;
        _fullScreenWatcher.CoveredChanged -= OnFullScreenChanged;
        _fullScreenWatcher.Stop();
        _imageViewer?.Close();
        _resizer.Detach();
        SaveWindowBounds();
    }

    private static PixelRect ToPixelRect(RectInt32 rect) => new(rect.X, rect.Y, rect.Width, rect.Height);

}
