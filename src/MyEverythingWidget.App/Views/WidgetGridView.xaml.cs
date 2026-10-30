using System.Collections.Specialized;
using System.ComponentModel;
using Microsoft.UI.Composition;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Hosting;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Presentation;
using Windows.Foundation;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Shows the cards of a <see cref="BoardViewModel"/> on the fixed grid and handles dragging and resizing.
/// The card itself follows the pointer at its real size; the cells it would cover are highlighted, and all
/// decisions (where it lands, whether it may) come from the view model.
/// </summary>
public sealed partial class WidgetGridView : UserControl
{
    private const int DraggedZIndex = 100;
    private const int CardZIndex = 1;
    private static readonly TimeSpan MoveAnimationDuration = TimeSpan.FromMilliseconds(180);

    private readonly Dictionary<string, GridCard> _cards = new(StringComparer.Ordinal);
    private BoardViewModel? _board;
    private DragSession? _session;
    private ImplicitAnimationCollection? _moveAnimations;

    /// <summary>Creates the view.</summary>
    public WidgetGridView()
    {
        InitializeComponent();
    }

    /// <inheritdoc />
    /// <remarks>UserControl has no automation peer of its own; without one the element is invisible to screen readers and UI tests.</remarks>
    protected override AutomationPeer OnCreateAutomationPeer() => new FrameworkElementAutomationPeer(this);

    /// <summary>Raised when a card is clicked (pressed and released without dragging).</summary>
    public event EventHandler<GridItemViewModel>? ItemInvoked;

    /// <summary>Gets or sets the board shown; set once after construction.</summary>
    public BoardViewModel? Board
    {
        get => _board;
        set
        {
            if (_board is not null)
            {
                _board.Items.CollectionChanged -= OnItemsChanged;
                _board.PropertyChanged -= OnBoardPropertyChanged;
            }

            _board = value;
            RebuildCards();
            if (_board is not null)
            {
                ApplyGridSize();
                _board.Items.CollectionChanged += OnItemsChanged;
                _board.PropertyChanged += OnBoardPropertyChanged;
            }
        }
    }

    private void OnBoardPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(BoardViewModel.GridSize))
        {
            ApplyGridSize();
        }
    }

    private void ApplyGridSize()
    {
        Width = _board!.GridSize.Columns * GridMetrics.CellSize;
        Height = _board.GridSize.Rows * GridMetrics.CellSize;
    }

    private void RebuildCards()
    {
        foreach (var card in _cards.Values)
        {
            card.Item.PropertyChanged -= OnItemPropertyChanged;
            CardLayer.Children.Remove(card);
        }

        _cards.Clear();
        foreach (var item in _board?.Items ?? [])
        {
            AddCard(item);
        }
    }

    private void OnItemsChanged(object? sender, NotifyCollectionChangedEventArgs e)
    {
        if (e.Action == NotifyCollectionChangedAction.Reset)
        {
            RebuildCards();
            return;
        }

        foreach (GridItemViewModel removed in e.OldItems ?? Array.Empty<GridItemViewModel>())
        {
            RemoveCard(removed.Id);
        }

        foreach (GridItemViewModel added in e.NewItems ?? Array.Empty<GridItemViewModel>())
        {
            AddCard(added);
        }
    }

    private void AddCard(GridItemViewModel item)
    {
        var card = new GridCard(item);
        Canvas.SetZIndex(card, CardZIndex);
        card.ContextFlyout = CreateCardMenu(item);
        card.PointerPressed += OnCardPointerPressed;
        card.PointerMoved += OnCardPointerMoved;
        card.PointerReleased += OnCardPointerReleased;
        card.PointerCaptureLost += OnCardPointerCaptureLost;
        card.Loaded += (_, _) => EnableMoveAnimation(card);
        card.DoubleTapped += (_, _) =>
        {
            if (item.Kind == ItemKind.Note)
            {
                _ = EditAsync(item);
            }
        };
        item.PropertyChanged += OnItemPropertyChanged;

        _cards[item.Id] = card;
        CardLayer.Children.Add(card);
        PlaceAtSlot(card);
    }

    private void RemoveCard(string itemId)
    {
        if (_cards.Remove(itemId, out var card))
        {
            card.Item.PropertyChanged -= OnItemPropertyChanged;
            CardLayer.Children.Remove(card);
        }
    }

    private MenuFlyout CreateCardMenu(GridItemViewModel item)
    {
        var moveTo = new MenuFlyoutSubItem { Text = "Move to", Icon = new FontIcon { Glyph = "\uE8DE" } };
        AutomationProperties.SetAutomationId(moveTo, "MoveToMenuItem");

        var delete = new MenuFlyoutItem { Text = "Delete", Icon = new FontIcon { Glyph = "\uE74D" } };
        AutomationProperties.SetAutomationId(delete, "DeleteItemMenuItem");
        delete.Click += (_, _) => _board?.DeleteCommand.Execute(item.Id);

        var menu = new MenuFlyout();
        if (item.Kind == ItemKind.Note)
        {
            var edit = new MenuFlyoutItem { Text = "Edit", Icon = new FontIcon { Glyph = "\uE70F" } };
            AutomationProperties.SetAutomationId(edit, "EditNoteMenuItem");
            edit.Click += (_, _) => _ = EditAsync(item);
            menu.Items.Add(edit);
        }
        else if (item.Kind == ItemKind.App)
        {
            var rename = new MenuFlyoutItem { Text = "Rename", Icon = new FontIcon { Glyph = "\uE8AC" } };
            AutomationProperties.SetAutomationId(rename, "RenameItemMenuItem");
            rename.Click += (_, _) => _ = EditAsync(item);
            menu.Items.Add(rename);

            var changeIcon = new MenuFlyoutItem { Text = "Change icon…", Icon = new FontIcon { Glyph = "" } };
            AutomationProperties.SetAutomationId(changeIcon, "ChangeIconMenuItem");
            changeIcon.Click += (_, _) => _ = ChangeIconAsync(item);
            menu.Items.Add(changeIcon);
        }

        menu.Items.Add(moveTo);
        menu.Items.Add(new MenuFlyoutSeparator());
        menu.Items.Add(delete);
        menu.Opening += (_, _) => FillMoveToMenu(moveTo, item);
        return menu;
    }

    /// <summary>Gets or sets the window that owns file pickers opened from the card menu.</summary>
    public nint OwnerWindowHandle { get; set; }

    /// <summary>Lets the user change the card's icon: an emoji, an image file, or the original icon.</summary>
    private async Task ChangeIconAsync(GridItemViewModel item)
    {
        if (_board is null)
        {
            return;
        }

        switch (await IconPickerDialog.ShowAsync(XamlRoot))
        {
            case IconChoice.Emoji emoji:
                _board.SetEmoji(item.Id, emoji.Value);
                break;
            case IconChoice.ImageData image:
                await using (var imageStream = new MemoryStream(image.Bytes, writable: false))
                {
                    await _board.ChangeIconAsync(item.Id, imageStream);
                }

                break;
            case IconChoice.Browse:
                await PickIconImageAsync(item);
                break;
            case IconChoice.Reset:
                await _board.ResetIconAsync(item.Id);
                break;
        }
    }

    private async Task PickIconImageAsync(GridItemViewModel item)
    {
        var picker = new Windows.Storage.Pickers.FileOpenPicker { SuggestedStartLocation = Windows.Storage.Pickers.PickerLocationId.PicturesLibrary };
        foreach (var extension in new[] { ".png", ".jpg", ".jpeg", ".ico", ".bmp", ".gif", ".webp" })
        {
            picker.FileTypeFilter.Add(extension);
        }

        WinRT.Interop.InitializeWithWindow.Initialize(picker, OwnerWindowHandle);
        if (await picker.PickSingleFileAsync() is { } file)
        {
            await using var stream = File.OpenRead(file.Path);
            await _board!.ChangeIconAsync(item.Id, stream);
        }
    }

    /// <summary>Edits a note's text or an app card's name in place.</summary>
    private async Task EditAsync(GridItemViewModel item)
    {
        if (_board is null || !_cards.TryGetValue(item.Id, out var card))
        {
            return;
        }

        if (item.Kind == ItemKind.Note)
        {
            if (await TextEditorDialog.ShowAsync(card.XamlRoot, "Edit note", item.Text ?? "", multiline: true) is { } text)
            {
                _board.EditNote(item.Id, text);
            }
        }
        else if (item.Kind == ItemKind.App
            && await TextEditorDialog.ShowAsync(card.XamlRoot, "Rename", item.Title, multiline: false) is { } name)
        {
            _board.RenameApp(item.Id, name);
        }
    }

    /// <summary>Lists the other categories at the moment the menu opens, so new or renamed tabs appear.</summary>
    private void FillMoveToMenu(MenuFlyoutSubItem moveTo, GridItemViewModel item)
    {
        moveTo.Items.Clear();
        foreach (var category in _board?.OtherCategories() ?? [])
        {
            var target = new MenuFlyoutItem { Text = category.Name };
            AutomationProperties.SetAutomationId(target, "MoveTo_" + category.Id);
            target.Click += (_, _) => _board?.MoveItemToCategory(item.Id, category.Id);
            moveTo.Items.Add(target);
        }

        moveTo.IsEnabled = moveTo.Items.Count > 0;
    }

    private void OnItemPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (sender is GridItemViewModel item
            && e.PropertyName is nameof(GridItemViewModel.Row) or nameof(GridItemViewModel.Column)
                or nameof(GridItemViewModel.ColumnSpan) or nameof(GridItemViewModel.RowSpan)
            && _cards.TryGetValue(item.Id, out var card)
            && _session?.Card != card)
        {
            PlaceAtSlot(card);
        }
    }

    /// <summary>Puts a card on the cells of its item; the implicit animation turns this into a slide.</summary>
    private static void PlaceAtSlot(GridCard card)
    {
        var slot = GridMetrics.ToRect(card.Item.Placement);
        Canvas.SetLeft(card, slot.X + GridMetrics.CardInset);
        Canvas.SetTop(card, slot.Y + GridMetrics.CardInset);
        card.Width = slot.Width - (2 * GridMetrics.CardInset);
        card.Height = slot.Height - (2 * GridMetrics.CardInset);
    }

    private void EnableMoveAnimation(GridCard card)
    {
        var visual = ElementCompositionPreview.GetElementVisual(card);
        if (_moveAnimations is null)
        {
            var compositor = visual.Compositor;
            var offset = compositor.CreateVector3KeyFrameAnimation();
            offset.Target = "Offset";
            offset.InsertExpressionKeyFrame(1f, "this.FinalValue");
            offset.Duration = MoveAnimationDuration;

            var size = compositor.CreateVector2KeyFrameAnimation();
            size.Target = "Size";
            size.InsertExpressionKeyFrame(1f, "this.FinalValue");
            size.Duration = MoveAnimationDuration;

            _moveAnimations = compositor.CreateImplicitAnimationCollection();
            _moveAnimations["Offset"] = offset;
            _moveAnimations["Size"] = size;
        }

        visual.ImplicitAnimations = _moveAnimations;
    }

    private void OnCardPointerPressed(object sender, PointerRoutedEventArgs e)
    {
        var card = (GridCard)sender;
        var point = e.GetCurrentPoint(CardLayer);
        if (_session is not null || !point.Properties.IsLeftButtonPressed)
        {
            return;
        }

        var mode = IsWithin(e.OriginalSource as DependencyObject, card.ResizeGrip) ? DragMode.Resize : DragMode.Move;
        _session = new DragSession(card, mode, point.Position);
        card.CapturePointer(e.Pointer);
        e.Handled = true;
    }

    private void OnCardPointerMoved(object sender, PointerRoutedEventArgs e)
    {
        if (_session is not { } session || !ReferenceEquals(session.Card, sender) || _board is null)
        {
            return;
        }

        var position = e.GetCurrentPoint(CardLayer).Position;
        var delta = new Point(position.X - session.StartPointer.X, position.Y - session.StartPointer.Y);
        if (!session.IsDragging)
        {
            if (Math.Abs(delta.X) < GridMetrics.DragThreshold && Math.Abs(delta.Y) < GridMetrics.DragThreshold)
            {
                return;
            }

            session.IsDragging = true;
            Canvas.SetZIndex(session.Card, DraggedZIndex);
            session.Card.Opacity = 0.92;
        }

        var slot = GridMetrics.ToRect(session.Card.Item.Placement);
        if (session.Mode == DragMode.Move)
        {
            session.Translation.X = delta.X;
            session.Translation.Y = delta.Y;
            session.Card.RenderTransform = session.Translation;
            var cell = GridMetrics.NearestCell(new Point(slot.X + delta.X, slot.Y + delta.Y));
            session.Preview = _board.PreviewDrop(session.Card.Item.Id, cell);
        }
        else
        {
            var span = GridMetrics.NearestSpan(position.X - slot.X, position.Y - slot.Y);
            session.Preview = _board.PreviewResize(session.Card.Item.Id, span);
        }

        ShowPreview(session.Preview);
        e.Handled = true;
    }

    private void OnCardPointerReleased(object sender, PointerRoutedEventArgs e)
    {
        if (_session is not { } session || !ReferenceEquals(session.Card, sender))
        {
            return;
        }

        _session = null;
        session.Card.ReleasePointerCapture(e.Pointer);
        e.Handled = true;

        if (!session.IsDragging)
        {
            ItemInvoked?.Invoke(this, session.Card.Item);
            return;
        }

        Finish(session, apply: true);
    }

    private void OnCardPointerCaptureLost(object sender, PointerRoutedEventArgs e)
    {
        if (_session is { } session && ReferenceEquals(session.Card, sender))
        {
            _session = null;
            if (session.IsDragging)
            {
                Finish(session, apply: false);
            }
        }
    }

    /// <summary>
    /// Ends a drag. The card is first pinned where the user sees it (no animation), then given its final slot,
    /// so the implicit animation slides it from the pointer position to where it belongs.
    /// </summary>
    private void Finish(DragSession session, bool apply)
    {
        HidePreview();
        var card = session.Card;
        var visual = ElementCompositionPreview.GetElementVisual(card);

        visual.ImplicitAnimations = null;
        Canvas.SetLeft(card, Canvas.GetLeft(card) + session.Translation.X);
        Canvas.SetTop(card, Canvas.GetTop(card) + session.Translation.Y);
        card.RenderTransform = null;
        card.Opacity = 1;
        Canvas.SetZIndex(card, CardZIndex);
        CardLayer.UpdateLayout();
        visual.ImplicitAnimations = _moveAnimations;

        if (apply && session.Preview is { CanDrop: true } && _board is not null)
        {
            if (session.Mode == DragMode.Move)
            {
                _board.Drop(card.Item.Id, session.Preview.Placement.Anchor);
            }
            else
            {
                _board.Resize(card.Item.Id, session.Preview.Placement.Span);
            }
        }

        PlaceAtSlot(card);
    }

    private void ShowPreview(DropPreview? preview)
    {
        if (preview is null)
        {
            HidePreview();
            return;
        }

        var rect = GridMetrics.ToRect(preview.Placement);
        Canvas.SetLeft(DropPreview, rect.X + GridMetrics.CardInset);
        Canvas.SetTop(DropPreview, rect.Y + GridMetrics.CardInset);
        DropPreview.Width = rect.Width - (2 * GridMetrics.CardInset);
        DropPreview.Height = rect.Height - (2 * GridMetrics.CardInset);
        DropPreviewBox.Background = ThemeBrush(preview.CanDrop ? "SystemFillColorAttentionBackgroundBrush" : "SystemFillColorCriticalBackgroundBrush");
        DropPreviewBox.BorderBrush = ThemeBrush(preview.CanDrop ? "AccentFillColorDefaultBrush" : "SystemFillColorCriticalBrush");
        AutomationProperties.SetHelpText(DropPreview, preview.CanDrop ? "allowed" : "not allowed");
        DropPreview.Visibility = Visibility.Visible;
    }

    private void HidePreview() => DropPreview.Visibility = Visibility.Collapsed;

    private static Brush ThemeBrush(string key) => (Brush)Application.Current.Resources[key];

    private static bool IsWithin(DependencyObject? element, UIElement container)
    {
        for (var current = element; current is not null; current = VisualTreeHelper.GetParent(current))
        {
            if (ReferenceEquals(current, container))
            {
                return true;
            }
        }

        return false;
    }

    private enum DragMode
    {
        Move,
        Resize,
    }

    private sealed class DragSession(GridCard card, DragMode mode, Point startPointer)
    {
        public GridCard Card { get; } = card;

        public DragMode Mode { get; } = mode;

        public Point StartPointer { get; } = startPointer;

        public TranslateTransform Translation { get; } = new();

        public bool IsDragging { get; set; }

        public DropPreview? Preview { get; set; }
    }
}
