using Microsoft.Extensions.Logging;
using MyEverythingWidget.Core.Storage;

namespace MyEverythingWidget.Core.Settings;

/// <summary>
/// Stores <see cref="AppSettings"/> as <c>settings.json</c> in a directory (atomic writes, corrupt files kept aside;
/// see <see cref="AtomicJsonFile{T}"/>).
/// </summary>
public sealed partial class JsonSettingsStore : ISettingsStore
{
    private readonly AtomicJsonFile<AppSettings> _file;
    private readonly ILogger<JsonSettingsStore> _logger;

    /// <summary>
    /// Creates a store that keeps its file in <paramref name="directory"/>.
    /// </summary>
    public JsonSettingsStore(string directory, TimeProvider timeProvider, ILogger<JsonSettingsStore> logger)
    {
        ArgumentNullException.ThrowIfNull(logger);

        _file = new AtomicJsonFile<AppSettings>(directory, "settings", SettingsJsonContext.Default.AppSettings, timeProvider);
        _logger = logger;
    }

    /// <inheritdoc />
    public AppSettings Load()
    {
        var result = _file.Read();
        if (result.CorruptBackupPath is { } backupPath)
        {
            LogCorruptFile(result.Error, _file.FilePath, backupPath);
        }

        return result.Value ?? AppSettings.Default;
    }

    /// <inheritdoc />
    public void Save(AppSettings settings) => _file.Write(settings);

    [LoggerMessage(Level = LogLevel.Warning, Message = "Settings file {Path} could not be parsed; kept it as {BackupPath} and using defaults")]
    private partial void LogCorruptFile(Exception? exception, string path, string backupPath);
}
