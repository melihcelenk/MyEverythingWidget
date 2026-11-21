using System.ComponentModel;
using System.Diagnostics;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.App;

/// <summary>
/// Opens an image in Paint for editing. Paint runs as its own process, so the widget stays small; when the user saves,
/// the card shows the change the next time the widget is activated.
/// </summary>
internal static class ImageEditor
{
    /// <summary>Message shown when Paint cannot be started.</summary>
    public static string PaintNotAvailableMessage => Strings.PaintNotAvailable;

    private const string PaintExecutable = "mspaint.exe";

    /// <summary>Opens <paramref name="imageFile"/> in Paint; returns <see langword="false"/> when Paint could not be started.</summary>
    public static bool TryOpenInPaint(string imageFile)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(imageFile);

        try
        {
            using var process = Process.Start(new ProcessStartInfo(PaintExecutable, $"\"{imageFile}\"") { UseShellExecute = true });
            return true;
        }
        catch (Exception exception) when (exception is Win32Exception or InvalidOperationException)
        {
            return false;
        }
    }
}
