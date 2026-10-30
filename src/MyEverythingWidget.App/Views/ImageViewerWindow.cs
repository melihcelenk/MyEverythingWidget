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
            Source = new BitmapImage(new Uri(imageFile)),
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
        AutomationProperties.SetName(close, "Close");
        close.Click += (_, _) => Close();

        var root = new AutomationHost
        {
            RequestedTheme = theme,
            Background = (Brush)Application.Current.Resources["SolidBackgroundFillColorBaseBrush"],
            Content = new Grid { Children = { image, close } },
        };
        AutomationProperties.SetAutomationId(root, "ImageViewer");
        root.KeyboardAccelerators.Add(CloseOnEscape());
        Content = root;

        var bounds = ImageViewerPlacement.Fit(imageSize, workArea);
        AppWindow.MoveAndResize(new RectInt32(bounds.X, bounds.Y, bounds.Width, bounds.Height));
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
