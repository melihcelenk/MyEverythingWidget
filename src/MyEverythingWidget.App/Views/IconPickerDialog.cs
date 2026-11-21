using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using MyEverythingWidget.Core.Apps;
using Windows.ApplicationModel.DataTransfer;
using Windows.Graphics.Imaging;
using Windows.Storage;
using Windows.System;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.App.Views;

/// <summary>What the user chose in the icon dialog.</summary>
internal abstract record IconChoice
{
    /// <summary>Show this emoji.</summary>
    public sealed record Emoji(string Value) : IconChoice;

    /// <summary>Use this image, dropped or pasted.</summary>
    public sealed record ImageData(byte[] Bytes) : IconChoice;

    /// <summary>Pick an image file with the file picker.</summary>
    public sealed record Browse : IconChoice;

    /// <summary>Go back to the icon of the program, folder or site.</summary>
    public sealed record Reset : IconChoice;
}

/// <summary>
/// One place to change an app card's icon, with two tabs: "Select icon" (an emoji grid) and "Select image" (browse,
/// drop or Ctrl+V). "Reset to original" and "Cancel" are the dialog's own buttons, so they stay visible however small
/// the widget is; the tab content scrolls when it does not fit.
/// </summary>
internal sealed class IconPickerDialog
{
    private const double EmojiCellSize = 40;
    private const int EmojisPerRow = 8;

    private static readonly string[] ImageExtensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".tif", ".tiff"];

    private readonly ContentDialog _dialog;
    private readonly ScrollViewer _iconPage;
    private readonly ScrollViewer _imagePage;
    private readonly TextBlock _imageMessage;
    private SelectorBarItem? _iconTab;
    private IconChoice? _choice;

    /// <summary>The dialog is built once per window and reused: its template and emoji grid are then already laid out.</summary>
    private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<XamlRoot, IconPickerDialog> Instances = [];

    private IconPickerDialog(XamlRoot root)
    {
        _dialog = new ContentDialog
        {
            XamlRoot = root,
            SecondaryButtonText = Strings.ResetToOriginal,
            CloseButtonText = Strings.Cancel,
            DefaultButton = ContentDialogButton.Close,
        };
        AutomationProperties.SetAutomationId(_dialog, "IconPickerDialog");
        AutomationProperties.SetName(_dialog, Strings.ChangeIcon);

        _imageMessage = new TextBlock
        {
            Foreground = (Brush)Application.Current.Resources["SystemFillColorCriticalBrush"],
            Style = (Style)Application.Current.Resources["CaptionTextBlockStyle"],
            HorizontalAlignment = HorizontalAlignment.Center,
        };
        _iconPage = Page(CreateEmojiGrid());
        _imagePage = Page(CreateImageArea());
        _imagePage.Visibility = Visibility.Collapsed;

        var tabs = CreateTabs();
        var content = new Grid
        {
            RowSpacing = 8,
            RowDefinitions = { new RowDefinition { Height = GridLength.Auto }, new RowDefinition { Height = new GridLength(1, GridUnitType.Star) } },
        };
        content.Children.Add(tabs);
        content.Children.Add(_iconPage);
        content.Children.Add(_imagePage);
        Grid.SetRow(_iconPage, 1);
        Grid.SetRow(_imagePage, 1);
        content.KeyboardAccelerators.Add(PasteAccelerator());
        _dialog.Content = content;

        // The tab goes back to "Select icon" only once the dialog is on screen: changing the selection of a SelectorBar
        // that is not in the visual tree makes WinUI loop forever and the app stops responding.
        _dialog.Opened += (_, _) => _iconTab!.IsSelected = true;
    }

    /// <summary>Shows the dialog; returns the choice, or <see langword="null"/> when cancelled.</summary>
    public static async Task<IconChoice?> ShowAsync(XamlRoot root)
    {
        var picker = Instances.GetValue(root, key => new IconPickerDialog(key));
        picker.Reset();
        DialogSizing.FitToWindow(picker._dialog, root);
        var result = await picker._dialog.ShowAsync();
        return result == ContentDialogResult.Secondary ? new IconChoice.Reset() : picker._choice;
    }

    /// <summary>Builds the dialog for <paramref name="root"/> ahead of its first use, so opening it is quick.</summary>
    public static void Prepare(XamlRoot root) => Instances.GetValue(root, key => new IconPickerDialog(key));

    /// <summary>Starts every showing like a new dialog: no choice and no warning; the tab is reset when it opens.</summary>
    private void Reset()
    {
        _choice = null;
        _imageMessage.Text = "";
    }

    private void Choose(IconChoice chosen)
    {
        _choice = chosen;
        _dialog.Hide();
    }

    private static ScrollViewer Page(UIElement content) => new()
    {
        Content = content,
        HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled,
        VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
    };

    private SelectorBar CreateTabs()
    {
        var iconTab = new SelectorBarItem { Text = Strings.SelectIcon, IsSelected = true };
        _iconTab = iconTab;
        AutomationProperties.SetAutomationId(iconTab, "SelectIconTab");
        var imageTab = new SelectorBarItem { Text = Strings.SelectImage };
        AutomationProperties.SetAutomationId(imageTab, "SelectImageTab");

        var tabs = new SelectorBar { Items = { iconTab, imageTab } };
        tabs.SelectionChanged += (_, _) =>
        {
            var showImage = ReferenceEquals(tabs.SelectedItem, imageTab);
            _iconPage.Visibility = showImage ? Visibility.Collapsed : Visibility.Visible;
            _imagePage.Visibility = showImage ? Visibility.Visible : Visibility.Collapsed;
        };
        return tabs;
    }

    private VariableSizedWrapGrid CreateEmojiGrid()
    {
        var emojis = new VariableSizedWrapGrid
        {
            Orientation = Orientation.Horizontal,
            MaximumRowsOrColumns = EmojisPerRow,
            ItemWidth = EmojiCellSize,
            ItemHeight = EmojiCellSize,
        };
        AutomationProperties.SetAutomationId(emojis, "IconEmojiList");
        foreach (var emoji in IconEmoji.Suggestions)
        {
            emojis.Children.Add(new EmojiCell(emoji, EmojiCellSize - 4, () => Choose(new IconChoice.Emoji(emoji))));
        }

        return emojis;
    }

    /// <summary>A dashed drop area with the Browse button; Ctrl+V anywhere in the dialog pastes too.</summary>
    private Border CreateImageArea()
    {
        var browse = new Button { Content = Strings.Browse, HorizontalAlignment = HorizontalAlignment.Center };
        AutomationProperties.SetAutomationId(browse, "BrowseImageButton");
        browse.Click += (_, _) => Choose(new IconChoice.Browse());

        var area = new AutomationHost
        {
            AllowDrop = true,
            Content = new StackPanel
            {
                Spacing = 10,
                Padding = new Thickness(16, 24, 16, 24),
                VerticalAlignment = VerticalAlignment.Center,
                Children =
                {
                    new FontIcon { Glyph = "", FontSize = 28, Foreground = (Brush)Application.Current.Resources["TextFillColorSecondaryBrush"] },
                    new TextBlock
                    {
                        Text = Strings.DropImageHere,
                        TextAlignment = TextAlignment.Center,
                        HorizontalAlignment = HorizontalAlignment.Center,
                        Foreground = (Brush)Application.Current.Resources["TextFillColorSecondaryBrush"],
                    },
                    browse,
                    _imageMessage,
                },
            },
        };
        AutomationProperties.SetAutomationId(area, "ImageDropArea");
        AutomationProperties.SetName(area, Strings.ImageDropArea);
        area.DragOver += (_, e) =>
        {
            if (e.DataView.Contains(StandardDataFormats.StorageItems) || e.DataView.Contains(StandardDataFormats.Bitmap))
            {
                e.AcceptedOperation = DataPackageOperation.Copy;
                e.DragUIOverride.Caption = Strings.UseAsIcon;
            }
        };
        area.Drop += async (_, e) =>
        {
            var deferral = e.GetDeferral();
            try
            {
                await UseImageFromAsync(e.DataView);
            }
            finally
            {
                deferral.Complete();
            }
        };

        return new Border
        {
            Child = area,
            CornerRadius = (CornerRadius)Application.Current.Resources["ControlCornerRadius"],
            BorderThickness = new Thickness(1),
            BorderBrush = (Brush)Application.Current.Resources["ControlStrongStrokeColorDefaultBrush"],
            MaxWidth = EmojiCellSize * EmojisPerRow,
        };
    }

    private KeyboardAccelerator PasteAccelerator()
    {
        var paste = new KeyboardAccelerator { Modifiers = VirtualKeyModifiers.Control, Key = VirtualKey.V };
        paste.Invoked += async (_, args) =>
        {
            args.Handled = true;
            await UseImageFromAsync(Clipboard.GetContent());
        };
        return paste;
    }

    /// <summary>Uses a picture or the first image file in <paramref name="data"/>; anything else shows a short warning.</summary>
    private async Task UseImageFromAsync(DataPackageView data)
    {
        if (await ReadImageAsync(data) is { } bytes)
        {
            Choose(new IconChoice.ImageData(bytes));
        }
        else
        {
            _imageMessage.Text = Strings.NotAnImage;
        }
    }

    private static async Task<byte[]?> ReadImageAsync(DataPackageView data)
    {
        if (data.Contains(StandardDataFormats.Bitmap))
        {
            var reference = await data.GetBitmapAsync();
            using var stream = (await reference.OpenReadAsync()).AsStreamForRead();
            return await ImageBytesAsync(stream);
        }

        if (data.Contains(StandardDataFormats.StorageItems))
        {
            var file = (await data.GetStorageItemsAsync()).OfType<StorageFile>()
                .FirstOrDefault(item => ImageExtensions.Contains(Path.GetExtension(item.Path), StringComparer.OrdinalIgnoreCase));
            if (file is not null)
            {
                using var stream = await file.OpenStreamForReadAsync();
                return await ImageBytesAsync(stream);
            }
        }

        return null;
    }

    /// <summary>Returns the bytes when they decode as an image, otherwise <see langword="null"/>.</summary>
    private static async Task<byte[]?> ImageBytesAsync(Stream stream)
    {
        using var copy = new MemoryStream();
        await stream.CopyToAsync(copy);
        var bytes = copy.ToArray();
        try
        {
            using var check = new MemoryStream(bytes);
            await BitmapDecoder.CreateAsync(check.AsRandomAccessStream());
            return bytes;
        }
        catch (Exception exception) when (exception is ArgumentException or System.Runtime.InteropServices.COMException)
        {
            return null;
        }
    }
}
