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

    private void SetHoverParts(double opacity)
    {
        ResizeHandle.Opacity = opacity;
        CopyButton.Opacity = opacity;
    }

    private async void OnCopyClicked(object sender, RoutedEventArgs e)
    {
        if (Item.Kind == ItemKind.Image)
        {
            if (DataFiles.Resolve(Item.ImagePath) is { } imageFile)
            {
                await ClipboardWriter.CopyImageAsync(imageFile);
            }

            return;
        }

        var package = new DataPackage();
        package.SetText(Item.Text ?? "");
        Clipboard.SetContent(package);
    }

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
        AutomationProperties.SetName(CopyButton, Item.Kind == ItemKind.Image ? "Copy image" : "Copy note");

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
        ImageContent.Source = imageFile is null ? null : new BitmapImage(new Uri(imageFile));
    }
}
