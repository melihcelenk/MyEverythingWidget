using System.Text.Json.Serialization;
using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.Core.State;

/// <summary>
/// A tab of the widget. Categories are shown in list order.
/// </summary>
/// <param name="Id">Stable identifier.</param>
/// <param name="Name">Name shown on the tab.</param>
public sealed record Category(string Id, string Name);

/// <summary>
/// How an app item is opened.
/// </summary>
public enum LaunchKind
{
    /// <summary>An executable or shortcut (<c>.exe</c>, <c>.lnk</c>) or a Store app.</summary>
    Executable,

    /// <summary>A web address, opened in the default browser.</summary>
    Url,

    /// <summary>A folder, opened in File Explorer.</summary>
    Folder,
}

/// <summary>
/// Something placed on a category's grid.
/// </summary>
/// <param name="Id">Stable identifier.</param>
/// <param name="CategoryId">Category the item belongs to.</param>
/// <param name="Placement">Cells the item covers.</param>
[JsonPolymorphic(TypeDiscriminatorPropertyName = "kind")]
[JsonDerivedType(typeof(AppItem), "app")]
[JsonDerivedType(typeof(NoteItem), "note")]
[JsonDerivedType(typeof(ImageItem), "image")]
public abstract record WidgetItem(string Id, string CategoryId, GridPlacement Placement)
{
    /// <summary>Gets the item kind.</summary>
    [JsonIgnore]
    public abstract ItemKind Kind { get; }
}

/// <summary>
/// A shortcut to an application, a URL or a folder.
/// </summary>
/// <param name="Name">Label under the icon.</param>
/// <param name="Target">Path, URL, or Application User Model ID of a Store app.</param>
/// <param name="LaunchKind">How <paramref name="Target"/> is opened.</param>
/// <param name="IconPath">Icon file relative to the data folder; <see langword="null"/> uses a generated icon.</param>
public sealed record AppItem(
    string Id,
    string CategoryId,
    GridPlacement Placement,
    string Name,
    string Target,
    LaunchKind LaunchKind,
    string? IconPath)
    : WidgetItem(Id, CategoryId, Placement)
{
    /// <inheritdoc />
    [JsonIgnore]
    public override ItemKind Kind => ItemKind.App;
}

/// <summary>
/// A text note.
/// </summary>
/// <param name="Text">Note text.</param>
public sealed record NoteItem(string Id, string CategoryId, GridPlacement Placement, string Text)
    : WidgetItem(Id, CategoryId, Placement)
{
    /// <inheritdoc />
    [JsonIgnore]
    public override ItemKind Kind => ItemKind.Note;
}

/// <summary>
/// An image kept in the data folder.
/// </summary>
/// <param name="ImagePath">Image file relative to the data folder.</param>
/// <param name="PixelWidth">Width of the image in pixels.</param>
/// <param name="PixelHeight">Height of the image in pixels.</param>
public sealed record ImageItem(
    string Id,
    string CategoryId,
    GridPlacement Placement,
    string ImagePath,
    int PixelWidth,
    int PixelHeight)
    : WidgetItem(Id, CategoryId, Placement)
{
    /// <inheritdoc />
    [JsonIgnore]
    public override ItemKind Kind => ItemKind.Image;
}

/// <summary>
/// Everything the widget shows: categories and the items on their grids.
/// </summary>
/// <param name="SchemaVersion">Version of the stored format.</param>
/// <param name="Categories">Categories in tab order.</param>
/// <param name="Items">All items of all categories.</param>
public sealed record WidgetState(int SchemaVersion, IReadOnlyList<Category> Categories, IReadOnlyList<WidgetItem> Items)
{
    /// <summary>Version written by this build.</summary>
    public const int CurrentSchemaVersion = 1;

    /// <summary>Name of the category created on first run.</summary>
    public const string DefaultCategoryName = "General";

    /// <summary>Gets the category whose tab was open last; <see langword="null"/> means the first one.</summary>
    public string? SelectedCategoryId { get; init; }

    /// <summary>Returns the first-run state: one empty category.</summary>
    public static WidgetState CreateDefault(string categoryId) =>
        new(CurrentSchemaVersion, [new Category(categoryId, DefaultCategoryName)], []);
}
