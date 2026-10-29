using System.Globalization;

namespace MyEverythingWidget.App;

/// <summary>
/// Appends unhandled exceptions to <c>logs\crash.log</c> in the app data folder.
/// </summary>
internal static class CrashLog
{
    /// <summary>Appends <paramref name="exception"/> with a UTC timestamp; never throws.</summary>
    public static void Write(string dataDirectory, Exception exception)
    {
        try
        {
            var logDirectory = Path.Combine(dataDirectory, "logs");
            Directory.CreateDirectory(logDirectory);
            var entry = string.Create(
                CultureInfo.InvariantCulture,
                $"[{DateTimeOffset.UtcNow:O}] {exception}{Environment.NewLine}{Environment.NewLine}");
            File.AppendAllText(Path.Combine(logDirectory, "crash.log"), entry);
        }
        catch (IOException)
        {
            // Nothing else can record the failure; the crash itself still reaches Windows Error Reporting.
        }
        catch (UnauthorizedAccessException)
        {
            // Same as above: the data folder is not writable.
        }
    }
}
