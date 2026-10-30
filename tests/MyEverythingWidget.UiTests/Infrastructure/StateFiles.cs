using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Writes a widget state for the app to start with, and reads back what the app saved.
/// </summary>
internal static class StateFiles
{
    public const string CategoryId = "c1";

    /// <summary>
    /// Writes one "General" category holding <paramref name="placements"/>. Ids starting with A become apps,
    /// N notes and I images; the id is also the app name or note text.
    /// </summary>
    public static void Seed(AppDataFolder data, IReadOnlyDictionary<string, GridPlacement> placements)
    {
        var items = placements.Select(pair => CreateItem(pair.Key, pair.Value)).ToList();
        Store(data).Save(new WidgetState(WidgetState.CurrentSchemaVersion, [new Category(CategoryId, "General")], items));
    }

    /// <summary>Writes <paramref name="state"/> as the app's saved state.</summary>
    public static void Save(AppDataFolder data, WidgetState state) => Store(data).Save(state);

    /// <summary>Reads the whole state the app saved.</summary>
    public static WidgetState ReadState(AppDataFolder data) =>
        Store(data).Load().State ?? throw new InvalidOperationException("The app saved no state.");

    /// <summary>Creates an item of the kind its id names (A app, N note, I image) in <paramref name="categoryId"/>.</summary>
    public static WidgetItem Item(string id, string categoryId, GridPlacement placement) =>
        CreateItem(id, placement) with { CategoryId = categoryId };

    /// <summary>Reads the placements the app saved.</summary>
    public static IReadOnlyDictionary<string, GridPlacement> ReadPlacements(AppDataFolder data) =>
        (Store(data).Load().State ?? throw new InvalidOperationException("The app saved no state."))
            .Items.ToDictionary(item => item.Id, item => item.Placement);

    /// <summary>Reads the saved item with <paramref name="id"/>, or <see langword="null"/>.</summary>
    public static WidgetItem? ReadItem(AppDataFolder data, string id) =>
        Store(data).Load().State?.Items.FirstOrDefault(item => item.Id == id);

    private static JsonWidgetStateStore Store(AppDataFolder data) =>
        new(data.Path, TimeProvider.System, NullLogger<JsonWidgetStateStore>.Instance);

    private static WidgetItem CreateItem(string id, GridPlacement placement) => id[0] switch
    {
        'A' => new AppItem(id, CategoryId, placement, id, "notepad.exe", LaunchKind.Executable, null),
        'N' => new NoteItem(id, CategoryId, placement, id),
        'I' => new ImageItem(id, CategoryId, placement, "missing.png", 100, 100),
        _ => throw new ArgumentException($"Cannot tell the kind of item '{id}'.", nameof(id)),
    };
}
