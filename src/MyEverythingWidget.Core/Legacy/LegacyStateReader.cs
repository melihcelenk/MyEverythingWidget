using System.Text.Json;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Legacy;

/// <summary>Kind of a note in the Python version.</summary>
public enum LegacyNoteKind
{
    /// <summary>Plain text.</summary>
    Text,

    /// <summary>An image; the content is the image file path.</summary>
    Image,

    /// <summary>A web link; the content is the address.</summary>
    Link,

    /// <summary>A file; the content is the file path.</summary>
    File,
}

/// <summary>An app shortcut of the Python version. Items refer to their category by name.</summary>
public sealed record LegacyApp(string Name, string Target, LaunchKind Kind, string CategoryName, GridPlacement? Placement);

/// <summary>A note of the Python version.</summary>
public sealed record LegacyNote(string Content, LegacyNoteKind Kind, string CategoryName, GridPlacement? Placement);

/// <summary>Everything read from the Python version's <c>app_state.json</c>.</summary>
public sealed record LegacyData(IReadOnlyList<string> Categories, IReadOnlyList<LegacyApp> Apps, IReadOnlyList<LegacyNote> Notes);

/// <summary>
/// Reads the Python version's state file (<c>%LOCALAPPDATA%\MyEverythingWidget\app_state.json</c>).
/// Missing fields are tolerated; entries without a target or content are skipped.
/// </summary>
public static class LegacyStateReader
{
    /// <summary>Default location of the Python version's state file.</summary>
    public static string DefaultPath => Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "MyEverythingWidget", "app_state.json");

    /// <summary>Parses the file content; throws <see cref="JsonException"/> when it is not JSON.</summary>
    public static LegacyData Parse(string json)
    {
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;

        var categories = Array(root, "categories")
            .Select(category => Text(category, "name"))
            .Where(name => name.Length > 0)
            .ToList();

        var apps = Array(root, "apps")
            .Select(app => new LegacyApp(Text(app, "name"), Text(app, "target"), AppKind(Text(app, "type")), Text(app, "category"), Placement(app)))
            .Where(app => app.Target.Length > 0)
            .ToList();

        var notes = Array(root, "notes")
            .Select(note => new LegacyNote(Text(note, "content"), NoteKind(Text(note, "type")), Text(note, "category"), Placement(note)))
            .Where(note => note.Content.Trim().Length > 0)
            .ToList();

        return new LegacyData(categories, apps, notes);
    }

    private static List<JsonElement> Array(JsonElement root, string name) =>
        root.ValueKind == JsonValueKind.Object && root.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.Array
            ? value.EnumerateArray().Where(element => element.ValueKind == JsonValueKind.Object).ToList()
            : [];

    private static string Text(JsonElement element, string name) =>
        element.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String ? value.GetString() ?? "" : "";

    private static int? Number(JsonElement element, string name) =>
        element.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.Number && value.TryGetInt32(out var number) ? number : null;

    private static GridPlacement? Placement(JsonElement element) =>
        Number(element, "grid_row") is { } row && Number(element, "grid_col") is { } column
            ? new GridPlacement(row, column, Number(element, "col_span") ?? 1, Number(element, "row_span") ?? 1)
            : null;

    private static LaunchKind AppKind(string type) => type switch
    {
        "url" => LaunchKind.Url,
        "folder" => LaunchKind.Folder,
        _ => LaunchKind.Executable,
    };

    private static LegacyNoteKind NoteKind(string type) => type switch
    {
        "image" => LegacyNoteKind.Image,
        "link" => LegacyNoteKind.Link,
        "file" => LegacyNoteKind.File,
        _ => LegacyNoteKind.Text,
    };
}
