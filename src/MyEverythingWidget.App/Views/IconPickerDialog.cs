using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using MyEverythingWidget.Core.Apps;

namespace MyEverythingWidget.App.Views;

/// <summary>What the user chose in the icon dialog.</summary>
internal abstract record IconChoice
{
    /// <summary>Show this emoji.</summary>
    public sealed record Emoji(string Value) : IconChoice;

    /// <summary>Pick an image file.</summary>
    public sealed record Image : IconChoice;

    /// <summary>Go back to the icon of the program, folder or site.</summary>
    public sealed record Reset : IconChoice;
}

/// <summary>
/// One place to change an app card's icon: click an emoji, choose an image, or reset to the original icon.
/// </summary>
internal static class IconPickerDialog
{
    private const double EmojiCellSize = 40;
    private const int EmojisPerRow = 8;

    /// <summary>Shows the dialog; returns the choice, or <see langword="null"/> when cancelled.</summary>
    public static async Task<IconChoice?> ShowAsync(XamlRoot root)
    {
        IconChoice? choice = null;
        var dialog = new ContentDialog
        {
            XamlRoot = root,
            Title = "Change icon",
            CloseButtonText = "Cancel",
            DefaultButton = ContentDialogButton.Close,
        };
        AutomationProperties.SetAutomationId(dialog, "IconPickerDialog");

        void Choose(IconChoice chosen)
        {
            choice = chosen;
            dialog.Hide();
        }

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
            var button = new Button
            {
                Content = emoji,
                FontFamily = new FontFamily("Segoe UI Emoji"),
                FontSize = 20,
                Padding = new Thickness(0),
                Width = EmojiCellSize - 4,
                Height = EmojiCellSize - 4,
                Background = (Brush)Application.Current.Resources["SubtleFillColorTransparentBrush"],
                BorderThickness = new Thickness(0),
            };
            AutomationProperties.SetAutomationId(button, "Emoji_" + emoji);
            AutomationProperties.SetName(button, emoji);
            button.Click += (_, _) => Choose(new IconChoice.Emoji(emoji));
            emojis.Children.Add(button);
        }

        var chooseImage = new Button { Content = "Image…" };
        AutomationProperties.SetAutomationId(chooseImage, "ChooseImageButton");
        chooseImage.Click += (_, _) => Choose(new IconChoice.Image());

        var reset = new Button { Content = "Reset to original" };
        AutomationProperties.SetAutomationId(reset, "ResetIconButton");
        reset.Click += (_, _) => Choose(new IconChoice.Reset());

        dialog.Content = new StackPanel
        {
            Spacing = 12,
            Children =
            {
                emojis,
                new StackPanel { Orientation = Orientation.Horizontal, Spacing = 8, Children = { chooseImage, reset } },
            },
        };

        await dialog.ShowAsync();
        return choice;
    }
}
