using System.Globalization;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace MyEverythingWidget.Core.Settings;

/// <summary>
/// Stores <see cref="AppSettings"/> as <c>settings.json</c> in a directory.
/// </summary>
/// <remarks>
/// Writes go to a temporary file that then replaces the real one, so a crash mid-write never leaves a
/// half-written file. A file that cannot be parsed is kept as <c>settings.corrupt-{timestamp}.json</c>
/// instead of being overwritten, so the user's data is never silently lost.
/// </remarks>
public sealed partial class JsonSettingsStore : ISettingsStore
{
    private const string FileName = "settings.json";

    private readonly string _directory;
    private readonly TimeProvider _timeProvider;
    private readonly ILogger<JsonSettingsStore> _logger;

    /// <summary>
    /// Creates a store that keeps its file in <paramref name="directory"/>.
    /// </summary>
    public JsonSettingsStore(string directory, TimeProvider timeProvider, ILogger<JsonSettingsStore> logger)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(directory);
        ArgumentNullException.ThrowIfNull(timeProvider);
        ArgumentNullException.ThrowIfNull(logger);

        _directory = directory;
        _timeProvider = timeProvider;
        _logger = logger;
    }

    private string FilePath => Path.Combine(_directory, FileName);

    /// <inheritdoc />
    public AppSettings Load()
    {
        if (!File.Exists(FilePath))
        {
            return AppSettings.Default;
        }

        try
        {
            var json = File.ReadAllText(FilePath);
            return JsonSerializer.Deserialize(json, SettingsJsonContext.Default.AppSettings) ?? AppSettings.Default;
        }
        catch (JsonException exception)
        {
            var backupPath = KeepCorruptCopy();
            LogCorruptFile(exception, FilePath, backupPath);
            return AppSettings.Default;
        }
    }

    /// <inheritdoc />
    public void Save(AppSettings settings)
    {
        ArgumentNullException.ThrowIfNull(settings);

        Directory.CreateDirectory(_directory);
        var temporaryPath = FilePath + ".tmp";
        File.WriteAllText(temporaryPath, JsonSerializer.Serialize(settings, SettingsJsonContext.Default.AppSettings));
        File.Move(temporaryPath, FilePath, overwrite: true);
    }

    private string KeepCorruptCopy()
    {
        var timestamp = _timeProvider.GetUtcNow().ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
        var backupPath = Path.Combine(_directory, $"settings.corrupt-{timestamp}.json");
        File.Move(FilePath, backupPath, overwrite: true);
        return backupPath;
    }

    [LoggerMessage(Level = LogLevel.Warning, Message = "Settings file {Path} could not be parsed; kept it as {BackupPath} and using defaults")]
    private partial void LogCorruptFile(Exception exception, string path, string backupPath);
}
