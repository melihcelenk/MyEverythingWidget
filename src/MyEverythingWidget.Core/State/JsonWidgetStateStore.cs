using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Logging;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Storage;

namespace MyEverythingWidget.Core.State;

/// <summary>
/// Stores <see cref="WidgetState"/> as <c>state.json</c> in the data folder (atomic writes, corrupt files kept
/// aside; see <see cref="AtomicJsonFile{T}"/>).
/// </summary>
public sealed partial class JsonWidgetStateStore : IWidgetStateStore
{
    private readonly AtomicJsonFile<WidgetState> _file;
    private readonly ILogger<JsonWidgetStateStore> _logger;

    /// <summary>Creates a store that keeps its file in <paramref name="directory"/>.</summary>
    public JsonWidgetStateStore(string directory, TimeProvider timeProvider, ILogger<JsonWidgetStateStore> logger)
    {
        ArgumentNullException.ThrowIfNull(logger);

        _file = new AtomicJsonFile<WidgetState>(directory, "state", StateJsonContext.Default.WidgetState, timeProvider, Validate);
        _logger = logger;
    }

    /// <inheritdoc />
    public StateLoadResult Load()
    {
        var result = _file.Read();
        if (result.CorruptBackupPath is { } backupPath)
        {
            LogCorruptFile(result.Error, _file.FilePath, backupPath);
        }

        return new StateLoadResult(result.Value, result.CorruptBackupPath);
    }

    /// <inheritdoc />
    public void Save(WidgetState state) => _file.Write(state);

    /// <summary>Rejects states that would break the grid: unknown lists, invalid spans, overlaps.</summary>
    private static void Validate(WidgetState state)
    {
        if (state.Categories is null || state.Items is null)
        {
            throw new JsonException("The state file has no categories or items list.");
        }

        foreach (var group in state.Items.GroupBy(item => item.CategoryId, StringComparer.Ordinal))
        {
            try
            {
                _ = new GridLayout(GridSize.Default, group.ToDictionary(item => item.Id, item => item.Placement, StringComparer.Ordinal));
            }
            catch (ArgumentException exception)
            {
                throw new JsonException($"Category '{group.Key}' has an invalid layout: {exception.Message}", exception);
            }
        }
    }

    [LoggerMessage(Level = LogLevel.Error, Message = "State file {Path} could not be read; kept it as {BackupPath} and starting empty")]
    private partial void LogCorruptFile(Exception? exception, string path, string backupPath);
}

/// <summary>
/// Writes <see cref="GridPlacement"/> as <c>{ "row", "column", "columns", "rows" }</c>.
/// </summary>
internal sealed class GridPlacementJsonConverter : JsonConverter<GridPlacement>
{
    public override GridPlacement Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        var value = JsonSerializer.Deserialize(ref reader, StateJsonContext.Default.PlacementDto)
            ?? throw new JsonException("A placement is null.");
        return new GridPlacement(value.Row, value.Column, value.Columns, value.Rows);
    }

    public override void Write(Utf8JsonWriter writer, GridPlacement value, JsonSerializerOptions options)
    {
        ArgumentNullException.ThrowIfNull(writer);
        var dto = new PlacementDto(value.Anchor.Row, value.Anchor.Column, value.Span.Columns, value.Span.Rows);
        JsonSerializer.Serialize(writer, dto, StateJsonContext.Default.PlacementDto);
    }
}

/// <summary>Stored shape of a placement.</summary>
internal sealed record PlacementDto(int Row, int Column, int Columns, int Rows);

/// <summary>Source-generated JSON metadata for the state file.</summary>
[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    WriteIndented = true,
    UseStringEnumConverter = true,
    Converters = [typeof(GridPlacementJsonConverter)])]
[JsonSerializable(typeof(WidgetState))]
[JsonSerializable(typeof(PlacementDto))]
internal sealed partial class StateJsonContext : JsonSerializerContext;
