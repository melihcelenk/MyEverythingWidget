using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Media.Imaging;
using MyEverythingWidget.Core.Geometry;
using Windows.Graphics;
using Windows.System;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Shows one image large, centred on a monitor. Escape, a click on the image or the close button closes it.
/// </summary>
internal sealed partial class ImageViewerWindow : Window
{
    /// <summary>Creates the viewer for <paramref name="imageFile"/> and places it on <paramref name="workArea"/>.</summary>
    public ImageViewerWindow(string imageFile, PixelSize imageSize, PixelRect workArea, ElementTheme theme)
    {
        Title = Path.GetFileName(imageFile);
        ExtendsContentIntoTitleBar = true;
        AppWindow.TitleBar.PreferredHeightOption = TitleBarHeightOption.Collapsed;
        if (AppWindow.Presenter is OverlappedPresenter presenter)
        {
            presenter.IsMaximizable = false;
            presenter.IsMinimizable = false;
        }

        var image = new Image
        {
            Source = new BitmapImage { CreateOptions = BitmapCreateOptions.IgnoreImageCache, UriSource = new Uri(imageFile) },
            Stretch = Stretch.Uniform,
        };
        AutomationProperties.SetAutomationId(image, "ViewerImage");
        AutomationProperties.SetName(image, Title);
        image.Tapped += (_, _) => Close();

        var close = new Button
        {
            Content = new FontIcon { Glyph = "", FontSize = 12 },
            HorizontalAlignment = HorizontalAlignment.Right,
            VerticalAlignment = VerticalAlignment.Top,
            Margin = new Thickness(8),
            Style = (Style)Application.Current.Resources["TitleBarButtonStyle"],
            Background = (Brush)Application.Current.Resources["SolidBackgroundFillColorQuarternaryBrush"],
        };
        AutomationProperties.SetAutomationId(close, "ViewerCloseButton");
        AutomationProperties.SetName(close, Strings.Close);
        close.Click += (_, _) => Close();

        _imageFile = imageFile;
        _notice = CreateNotice();
        var root = new AutomationHost
        {
            RequestedTheme = theme,
            Background = (Brush)Application.Current.Resources["SolidBackgroundFillColorBaseBrush"],
            Content = new Grid { Children = { image, close, _notice } },
            ContextFlyout = CreateMenu(),
        };
        AutomationProperties.SetAutomationId(root, "ImageViewer");
        root.KeyboardAccelerators.Add(CloseOnEscape());
        root.KeyboardAccelerators.Add(CopyOnCtrlC());
        Content = root;

        var bounds = ImageViewerPlacement.Fit(imageSize, workArea);
        AppWindow.MoveAndResize(new RectInt32(bounds.X, bounds.Y, bounds.Width, bounds.Height));
    }

    private static readonly TimeSpan NoticeDuration = TimeSpan.FromMilliseconds(1500);

    private readonly string _imageFile;
    private readonly AutomationHost _notice;

    /// <summary>Ctrl+C copies the shown image, as a picture and as a file.</summary>
    private KeyboardAccelerator CopyOnCtrlC()
    {
        var copy = new KeyboardAccelerator { Modifiers = VirtualKeyModifiers.Control, Key = VirtualKey.C };
        copy.Invoked += async (_, args) =>
        {
            args.Handled = true;
            await CopyAsync();
        };
        return copy;
    }

    /// <summary>Right-click menu: copy the image or open it in Paint.</summary>
    private MenuFlyout CreateMenu()
    {
        var copy = new MenuFlyoutItem { Text = Strings.Copy, Icon = new FontIcon { Glyph = "" } };
        AutomationProperties.SetAutomationId(copy, "ViewerCopyMenuItem");
        copy.Click += async (_, _) => await CopyAsync();

        var edit = new MenuFlyoutItem { Text = Strings.EditInPaint, Icon = new FontIcon { Glyph = "" } };
        AutomationProperties.SetAutomationId(edit, "ViewerEditMenuItem");
        edit.Click += (_, _) =>
        {
            if (!ImageEditor.TryOpenInPaint(_imageFile))
            {
                ShowNotice(ImageEditor.PaintNotAvailableMessage);
            }
        };

        return new MenuFlyout { Items = { copy, edit } };
    }

    private async Task CopyAsync()
    {
        await ClipboardWriter.CopyImageAsync(_imageFile);
        ShowNotice(Strings.Copied);
    }

    /// <summary>A short message at the bottom of the viewer, such as "Copied".</summary>
    private static AutomationHost CreateNotice()
    {
        var notice = new AutomationHost
        {
            Visibility = Visibility.Collapsed,
            IsHitTestVisible = false,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Bottom,
            Margin = new Thickness(16),
            Content = new Border
            {
                Padding = new Thickness(14, 8, 14, 8),
                CornerRadius = (CornerRadius)Application.Current.Resources["OverlayCornerRadius"],
                Background = (Brush)Application.Current.Resources["SolidBackgroundFillColorQuarternaryBrush"],
                BorderBrush = (Brush)Application.Current.Resources["CardStrokeColorDefaultBrush"],
                BorderThickness = new Thickness(1),
                Child = new TextBlock(),
            },
        };
        AutomationProperties.SetAutomationId(notice, "ViewerCopiedNotice");
        return notice;
    }

    private void ShowNotice(string message)
    {
        ((TextBlock)((Border)_notice.Content).Child).Text = message;
        AutomationProperties.SetName(_notice, message);
        _notice.Visibility = Visibility.Visible;

        var timer = DispatcherQueue.CreateTimer();
        timer.Interval = NoticeDuration;
        timer.IsRepeating = false;
        timer.Tick += (_, _) => _notice.Visibility = Visibility.Collapsed;
        timer.Start();
    }

    private KeyboardAccelerator CloseOnEscape()
    {
        var escape = new KeyboardAccelerator { Key = VirtualKey.Escape };
        escape.Invoked += (_, args) =>
        {
            args.Handled = true;
            Close();
        };
        return escape;
    }
}
