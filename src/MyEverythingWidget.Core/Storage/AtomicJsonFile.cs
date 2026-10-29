using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization.Metadata;

namespace MyEverythingWidget.Core.Storage;

/// <summary>Result of reading an <see cref="AtomicJsonFile{T}"/>.</summary>
/// <param name="Value">The parsed value, or <see langword="null"/> when the file is missing or unreadable.</param>
/// <param name="CorruptBackupPath">Where an unreadable file was moved to; otherwise <see langword="null"/>.</param>
/// <param name="Error">Why the file was unreadable; otherwise <see langword="null"/>.</param>
public sealed record JsonReadResult<T>(T? Value, string? CorruptBackupPath, Exception? Error)
    where T : class;

/// <summary>
/// A JSON file that is written atomically and never silently overwritten when it cannot be parsed.
/// </summary>
/// <remarks>
/// Writes go to <c>{name}.tmp</c>, which then replaces the real file, so a crash mid-write never leaves a
/// half-written file. A file that cannot be parsed or fails <c>validate</c> is moved to
/// <c>{name}.corrupt-{timestamp}.json</c> before the caller starts over.
/// </remarks>
public sealed class AtomicJsonFile<T>
    where T : class
{
    private readonly string _directory;
    private readonly string _baseName;
    private readonly JsonTypeInfo<T> _typeInfo;
    private readonly TimeProvider _timeProvider;
    private readonly Action<T>? _validate;

    /// <summary>
    /// Creates a file named <paramref name="baseName"/><c>.json</c> in <paramref name="directory"/>.
    /// <paramref name="validate"/> may throw <see cref="JsonException"/> to reject a parsed value.
    /// </summary>
    public AtomicJsonFile(string directory, string baseName, JsonTypeInfo<T> typeInfo, TimeProvider timeProvider, Action<T>? validate = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(directory);
        ArgumentException.ThrowIfNullOrWhiteSpace(baseName);
        ArgumentNullException.ThrowIfNull(typeInfo);
        ArgumentNullException.ThrowIfNull(timeProvider);

        _directory = directory;
        _baseName = baseName;
        _typeInfo = typeInfo;
        _timeProvider = timeProvider;
        _validate = validate;
    }

    /// <summary>Gets the full path of the file.</summary>
    public string FilePath => Path.Combine(_directory, _baseName + ".json");

    /// <summary>Reads the file; a missing file gives an empty result, an unreadable one is moved aside first.</summary>
    public JsonReadResult<T> Read()
    {
        if (!File.Exists(FilePath))
        {
            return new JsonReadResult<T>(null, null, null);
        }

        try
        {
            var value = JsonSerializer.Deserialize(File.ReadAllText(FilePath), _typeInfo)
                ?? throw new JsonException("The file contains null.");
            _validate?.Invoke(value);
            return new JsonReadResult<T>(value, null, null);
        }
        catch (JsonException exception)
        {
            return new JsonReadResult<T>(null, MoveAside(), exception);
        }
    }

    /// <summary>Writes <paramref name="value"/>, replacing the file atomically.</summary>
    public void Write(T value)
    {
        ArgumentNullException.ThrowIfNull(value);

        Directory.CreateDirectory(_directory);
        var temporaryPath = FilePath + ".tmp";
        File.WriteAllText(temporaryPath, JsonSerializer.Serialize(value, _typeInfo));
        File.Move(temporaryPath, FilePath, overwrite: true);
    }

    private string MoveAside()
    {
        var timestamp = _timeProvider.GetUtcNow().ToString("yyyyMMdd-HHmmss", CultureInfo.InvariantCulture);
        var backupPath = Path.Combine(_directory, $"{_baseName}.corrupt-{timestamp}.json");
        File.Move(FilePath, backupPath, overwrite: true);
        return backupPath;
    }
}
