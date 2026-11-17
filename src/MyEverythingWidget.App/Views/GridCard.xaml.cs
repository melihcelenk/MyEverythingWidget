using System.ComponentModel;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Automation.Peers;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Presentation;
using Windows.ApplicationModel.DataTransfer;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Visual of one grid item (app, note or image). Position and drag handling live in <see cref="WidgetGridView"/>.
/// </summary>
public sealed partial class GridCard : UserControl
{
    /// <summary>Creates the card for <paramref name="item"/>.</summary>
    public GridCard(GridItemViewModel item)
    {
        ArgumentNullException.ThrowIfNull(item);

        Item = item;
        InitializeComponent();

        AutomationProperties.SetAutomationId(this, "Card_" + item.Id);
        PointerEntered += (_, _) => SetHoverParts(1);
        PointerExited += (_, _) => SetHoverParts(0);

        ShowContent();
        Item.PropertyChanged += OnItemPropertyChanged;
        Unloaded += (_, _) => Item.PropertyChanged -= OnItemPropertyChanged;
    }

    /// <inheritdoc />
    /// <remarks>UserControl has no automation peer of its own; without one the element is invisible to screen readers and UI tests.</remarks>
    protected override AutomationPeer OnCreateAutomationPeer() => new FrameworkElementAutomationPeer(this);

    /// <summary>Gets the item shown by this card.</summary>
    public GridItemViewModel Item { get; }

    /// <summary>Gets the resize grip, so the grid can start a resize when it is pressed.</summary>
    public UIElement ResizeGrip => ResizeHandle;

    private const string CopyGlyph = "";
    private const string CopiedGlyph = "";
    private static readonly TimeSpan CopiedFeedback = TimeSpan.FromMilliseconds(1500);

    private bool _isPointerOver;
    private bool _isShowingCopied;
    private DateTime _imageWriteTime;

    private void SetHoverParts(double opacity)
    {
        _isPointerOver = opacity > 0;
        ResizeHandle.Opacity = opacity;
        if (!_isShowingCopied)
        {
            CopyButton.Opacity = opacity;
        }
    }

    /// <summary>Copies the note's text or the image to the clipboard and shows on the card that it was copied.</summary>
    public async Task CopyAsync()
    {
        if (Item.Kind == ItemKind.Image)
        {
            if (DataFiles.Resolve(Item.ImagePath) is not { } imageFile)
            {
                return;
            }

            await ClipboardWriter.CopyImageAsync(imageFile);
        }
        else
        {
            var package = new DataPackage();
            package.SetText(Item.Text ?? "");
            Clipboard.SetContent(package);
        }

        ShowCopied();
    }

    /// <summary>For a moment the copy button shows a check mark and says "Copied", even when the pointer is elsewhere.</summary>
    private void ShowCopied()
    {
        _isShowingCopied = true;
        CopyIcon.Glyph = CopiedGlyph;
        CopyButton.Opacity = 1;
        SetCopyButtonName("Copied");

        var timer = DispatcherQueue.CreateTimer();
        timer.Interval = CopiedFeedback;
        timer.IsRepeating = false;
        timer.Tick += (_, _) =>
        {
            _isShowingCopied = false;
            CopyIcon.Glyph = CopyGlyph;
            CopyButton.Opacity = _isPointerOver ? 1 : 0;
            SetCopyButtonName(null);
        };
        timer.Start();
    }

    /// <summary>Sets the copy button's name and tooltip; <see langword="null"/> restores the one for the card's kind.</summary>
    private void SetCopyButtonName(string? name)
    {
        var text = name ?? (Item.Kind == ItemKind.Image ? "Copy image" : "Copy note");
        AutomationProperties.SetName(CopyButton, text);
        ToolTipService.SetToolTip(CopyButton, name ?? "Copy");
    }

    /// <summary>Reloads the image when its file was changed outside the widget (for example saved from Paint).</summary>
    public void RefreshImageIfChanged()
    {
        if (Item.Kind == ItemKind.Image && DataFiles.Resolve(Item.ImagePath) is { } imageFile
            && File.GetLastWriteTimeUtc(imageFile) != _imageWriteTime)
        {
            ShowImage();
        }
    }

    private async void OnCopyClicked(object sender, RoutedEventArgs e) => await CopyAsync();

    private void OnItemPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName is nameof(GridItemViewModel.Title)
            or nameof(GridItemViewModel.Text)
            or nameof(GridItemViewModel.ImagePath)
            or nameof(GridItemViewModel.IconPath)
            or nameof(GridItemViewModel.Emoji))
        {
            ShowContent();
        }
    }

    private void ShowContent()
    {
        AutomationProperties.SetName(this, Item.Title);
        AppContent.Visibility = Item.Kind == ItemKind.App ? Visibility.Visible : Visibility.Collapsed;
        NoteText.Visibility = Item.Kind == ItemKind.Note ? Visibility.Visible : Visibility.Collapsed;
        NoteBackground.Visibility = NoteText.Visibility;
        var copyable = Item.Kind is ItemKind.Note or ItemKind.Image;
        CopyButton.Visibility = copyable ? Visibility.Visible : Visibility.Collapsed;
        AutomationProperties.SetAutomationId(CopyButton, Item.Kind == ItemKind.Image ? "CopyImageButton" : "CopyNoteButton");
        SetCopyButtonName(null);

        switch (Item.Kind)
        {
            case ItemKind.App:
                ShowApp();
                break;
            case ItemKind.Note:
                NoteText.Text = Item.Text ?? "";
                break;
            case ItemKind.Image:
                ShowImage();
                break;
        }
    }

    private void ShowApp()
    {
        AppName.Text = Item.Title;
        var hasEmoji = Item.Emoji is not null;
        AppEmoji.Text = Item.Emoji ?? "";
        AppEmoji.Visibility = hasEmoji ? Visibility.Visible : Visibility.Collapsed;

        var iconFile = hasEmoji ? null : DataFiles.Resolve(Item.IconPath);
        var hasIcon = iconFile is not null;
        AppIcon.Source = hasIcon ? new BitmapImage(new Uri(iconFile!)) : null;
        AppIcon.Visibility = hasIcon ? Visibility.Visible : Visibility.Collapsed;
        AppMonogram.Visibility = hasIcon || hasEmoji ? Visibility.Collapsed : Visibility.Visible;
        AppMonogramText.Text = Item.Title.Length > 0 ? char.ToUpperInvariant(Item.Title[0]).ToString() : "?";
    }

    private void ShowImage()
    {
        var imageFile = DataFiles.Resolve(Item.ImagePath);
        ImageContent.Visibility = imageFile is null ? Visibility.Collapsed : Visibility.Visible;
        ImageMissing.Visibility = imageFile is null ? Visibility.Visible : Visibility.Collapsed;
        _imageWriteTime = imageFile is null ? default : File.GetLastWriteTimeUtc(imageFile);

        // Skip the image cache, so a file saved again under the same name (for example from Paint) is read anew.
        ImageContent.Source = imageFile is null
            ? null
            : new BitmapImage { CreateOptions = BitmapCreateOptions.IgnoreImageCache, UriSource = new Uri(imageFile) };
    }
}
