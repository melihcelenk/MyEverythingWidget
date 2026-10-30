using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using Windows.System;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// A small dialog with one text box, used to add or edit a note and to rename an app card.
/// A dialog rather than a flyout: it opens reliably from menu items, whose closing would dismiss a flyout.
/// Enter saves a single-line text, Ctrl+Enter saves a multi-line text, Escape cancels.
/// </summary>
internal static class TextEditorDialog
{
    /// <summary>Shows the dialog; returns the text, or <see langword="null"/> when cancelled.</summary>
    public static async Task<string?> ShowAsync(XamlRoot root, string title, string initialText, bool multiline)
    {
        var editor = new TextBox
        {
            Text = initialText,
            AcceptsReturn = multiline,
            TextWrapping = multiline ? TextWrapping.Wrap : TextWrapping.NoWrap,
            Width = 280,
            Height = multiline ? 140 : double.NaN,
        };
        AutomationProperties.SetAutomationId(editor, "TextEditorBox");
        AutomationProperties.SetName(editor, title);

        var dialog = new ContentDialog
        {
            XamlRoot = root,
            Title = title,
            Content = editor,
            PrimaryButtonText = "Save",
            CloseButtonText = "Cancel",
            DefaultButton = ContentDialogButton.Primary,
        };
        AutomationProperties.SetAutomationId(dialog, "TextEditorDialog");

        var savedByKey = false;
        editor.KeyDown += (_, e) =>
        {
            var ctrl = Microsoft.UI.Input.InputKeyboardSource.GetKeyStateForCurrentThread(VirtualKey.Control)
                .HasFlag(Windows.UI.Core.CoreVirtualKeyStates.Down);
            if (e.Key == VirtualKey.Enter && (!multiline || ctrl))
            {
                savedByKey = true;
                dialog.Hide();
                e.Handled = true;
            }
        };
        editor.Loaded += (_, _) =>
        {
            editor.Focus(FocusState.Programmatic);
            editor.SelectAll();
        };

        var result = await dialog.ShowAsync();
        return result == ContentDialogResult.Primary || savedByKey ? editor.Text : null;
    }
}
