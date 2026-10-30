using System.Runtime.InteropServices;
using FlaUI.Core.AutomationElements;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>Sets the text of a box that may still be opening (flyout animation), retrying until it accepts the value.</summary>
internal static class TextInput
{
    public static void Set(AutomationElement box, string text)
    {
        var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(5);
        while (true)
        {
            try
            {
                box.AsTextBox().Text = text;
                return;
            }
            catch (COMException) when (DateTime.UtcNow < deadline)
            {
                Thread.Sleep(100);
            }
        }
    }
}
