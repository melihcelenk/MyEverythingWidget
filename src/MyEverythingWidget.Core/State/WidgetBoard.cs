using Microsoft.Extensions.Logging;
using MyEverythingWidget.Core.Grid;

namespace MyEverythingWidget.Core.State;

/// <summary>Result of adding an item.</summary>
/// <param name="Outcome">What happened.</param>
/// <param name="Item">The new item when <paramref name="Outcome"/> is <see cref="GridOutcome.Success"/>.</param>
public sealed record AddResult(GridOutcome Outcome, WidgetItem? Item);

/// <summary>Data of <see cref="WidgetBoard.SaveFailed"/>.</summary>
/// <param name="exception">Why the state could not be written.</param>
public sealed class SaveFailedEventArgs(Exception exception) : EventArgs
{
    /// <summary>Gets why the state could not be written.</summary>
    public Exception Exception { get; } = exception;
}

/// <summary>
/// The widget's state and the operations on it. Grid rules come from <see cref="GridLayout"/>;
/// every successful change is saved through <see cref="IWidgetStateStore"/>.
/// </summary>
public sealed partial class WidgetBoard
{
    private readonly IWidgetStateStore _store;
    private readonly Func<string> _newId;
    private readonly ILogger<WidgetBoard> _logger;

    /// <summary>Loads the stored state, or creates and saves the first-run state.</summary>
    public WidgetBoard(IWidgetStateStore store, Func<string> newId, GridSize gridSize, ILogger<WidgetBoard> logger)
    {
        ArgumentNullException.ThrowIfNull(store);
        ArgumentNullException.ThrowIfNull(newId);
        ArgumentNullException.ThrowIfNull(logger);

        _store = store;
        _newId = newId;
        _logger = logger;
        GridSize = gridSize;

        var loaded = store.Load();
        CorruptBackupPath = loaded.CorruptBackupPath;
        if (loaded.State is { } existing)
        {
            State = existing;
        }
        else
        {
            State = WidgetState.CreateDefault(newId());
            Save();
        }
    }

    /// <summary>Raised after every successful change.</summary>
    public event EventHandler? Changed;

    /// <summary>Raised when a change could not be written; the change stays in memory.</summary>
    public event EventHandler<SaveFailedEventArgs>? SaveFailed;

    /// <summary>Gets the current state.</summary>
    public WidgetState State { get; private set; }

    /// <summary>Longest category name kept; longer names are cut.</summary>
    public const int MaxCategoryNameLength = 30;

    /// <summary>Gets the categories in tab order.</summary>
    public IReadOnlyList<Category> Categories => State.Categories;

    /// <summary>Gets the category whose tab is open; falls back to the first category.</summary>
    public string SelectedCategoryId =>
        State.SelectedCategoryId is { } id && State.Categories.Any(category => category.Id == id)
            ? id
            : State.Categories[0].Id;

    /// <summary>Gets where an unreadable state file was moved on startup, if that happened.</summary>
    public string? CorruptBackupPath { get; }

    /// <summary>Gets the grid size of every category.</summary>
    public GridSize GridSize { get; }

    /// <summary>Returns the item with <paramref name="itemId"/>, or <see langword="null"/>.</summary>
    public WidgetItem? Find(string itemId) => State.Items.FirstOrDefault(item => item.Id == itemId);

    /// <summary>Returns the items of <paramref name="categoryId"/>.</summary>
    public IEnumerable<WidgetItem> ItemsIn(string categoryId) => State.Items.Where(item => item.CategoryId == categoryId);

    /// <summary>Returns the grid of <paramref name="categoryId"/>.</summary>
    public GridLayout LayoutOf(string categoryId)
    {
        EnsureCategory(categoryId);
        return new GridLayout(GridSize, ItemsIn(categoryId).ToDictionary(item => item.Id, item => item.Placement, StringComparer.Ordinal));
    }

    /// <summary>Adds a 1x1 app shortcut at the first free cell of the category.</summary>
    public AddResult AddApp(string categoryId, string name, string target, LaunchKind launchKind, string? iconPath)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(name);
        ArgumentException.ThrowIfNullOrWhiteSpace(target);

        return Add(categoryId, DefaultSpans.For(ItemKind.App), (id, placement) =>
            new AppItem(id, categoryId, placement, name.Trim(), target.Trim(), launchKind, iconPath));
    }

    /// <summary>Adds a 2x1 note at the first free cells of the category; <paramref name="text"/> must not be blank.</summary>
    public AddResult AddNote(string categoryId, string text)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(text);

        return Add(categoryId, DefaultSpans.For(ItemKind.Note), (id, placement) =>
            new NoteItem(id, categoryId, placement, text.Trim()));
    }

    /// <summary>Adds an image with <paramref name="span"/> at the first free cells of the category.</summary>
    public AddResult AddImage(string categoryId, string imagePath, int pixelWidth, int pixelHeight, GridSpan span)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(imagePath);

        return Add(categoryId, span, (id, placement) =>
            new ImageItem(id, categoryId, placement, imagePath, pixelWidth, pixelHeight));
    }

    /// <summary>Drops an item at <paramref name="target"/> following the grid rules.</summary>
    public GridOutcome Move(string itemId, GridCell target) =>
        ApplyToLayout(itemId, layout => layout.Move(itemId, target));

    /// <summary>Changes the span of an item.</summary>
    public GridOutcome Resize(string itemId, GridSpan span) =>
        ApplyToLayout(itemId, layout => layout.Resize(itemId, span));

    /// <summary>Removes an item; returns <see langword="false"/> when it does not exist.</summary>
    public bool Delete(string itemId)
    {
        if (Find(itemId) is null)
        {
            return false;
        }

        Commit(State with { Items = State.Items.Where(item => item.Id != itemId).ToList() });
        return true;
    }

    /// <summary>Replaces the text of a note; blank text, unknown ids and non-notes are refused.</summary>
    public bool UpdateNoteText(string itemId, string text)
    {
        if (string.IsNullOrWhiteSpace(text) || Find(itemId) is not NoteItem note)
        {
            return false;
        }

        Replace(note with { Text = text.Trim() });
        return true;
    }

    /// <summary>Renames an app card; blank names, unknown ids and non-apps are refused.</summary>
    public bool RenameApp(string itemId, string name)
    {
        if (string.IsNullOrWhiteSpace(name) || Find(itemId) is not AppItem app)
        {
            return false;
        }

        Replace(app with { Name = name.Trim() });
        return true;
    }

    private void Replace(WidgetItem updated) =>
        Commit(State with { Items = State.Items.Select(item => item.Id == updated.Id ? updated : item).ToList() });

    /// <summary>Opens the tab of <paramref name="categoryId"/> and remembers it for the next start.</summary>
    public void SelectCategory(string categoryId)
    {
        EnsureCategory(categoryId);
        if (State.SelectedCategoryId != categoryId)
        {
            Commit(State with { SelectedCategoryId = categoryId });
        }
    }

    /// <summary>Adds a category at the end of the tabs.</summary>
    public Category AddCategory(string name)
    {
        var category = new Category(_newId(), CleanName(name));
        Commit(State with { Categories = [.. State.Categories, category] });
        return category;
    }

    /// <summary>Renames a category; returns <see langword="false"/> when it does not exist.</summary>
    public bool RenameCategory(string categoryId, string name)
    {
        var cleanName = CleanName(name);
        if (!State.Categories.Any(category => category.Id == categoryId))
        {
            return false;
        }

        Commit(State with
        {
            Categories = State.Categories.Select(category => category.Id == categoryId ? category with { Name = cleanName } : category).ToList(),
        });
        return true;
    }

    /// <summary>
    /// Deletes a category and its items. The last category cannot be deleted; returns <see langword="false"/> then,
    /// or when the category does not exist. When the open tab is deleted, its neighbour opens.
    /// </summary>
    public bool DeleteCategory(string categoryId)
    {
        var index = State.Categories.ToList().FindIndex(category => category.Id == categoryId);
        if (index < 0 || State.Categories.Count == 1)
        {
            return false;
        }

        var remaining = State.Categories.Where(category => category.Id != categoryId).ToList();
        var selected = SelectedCategoryId == categoryId ? remaining[Math.Max(0, index - 1)].Id : State.SelectedCategoryId;
        Commit(State with
        {
            Categories = remaining,
            Items = State.Items.Where(item => item.CategoryId != categoryId).ToList(),
            SelectedCategoryId = selected,
        });
        return true;
    }

    /// <summary>Puts the categories in the order of <paramref name="categoryIds"/>, which must list each category once.</summary>
    public void ReorderCategories(IReadOnlyList<string> categoryIds)
    {
        ArgumentNullException.ThrowIfNull(categoryIds);

        var byId = State.Categories.ToDictionary(category => category.Id, StringComparer.Ordinal);
        if (categoryIds.Count != byId.Count || categoryIds.Distinct(StringComparer.Ordinal).Count() != byId.Count || !categoryIds.All(byId.ContainsKey))
        {
            throw new ArgumentException("The order must list every category exactly once.", nameof(categoryIds));
        }

        Commit(State with { Categories = categoryIds.Select(id => byId[id]).ToList() });
    }

    /// <summary>Moves an item to the first free cells of another category; the item stays when there is no room.</summary>
    public GridOutcome MoveItemToCategory(string itemId, string categoryId)
    {
        EnsureCategory(categoryId);
        if (Find(itemId) is not { } item)
        {
            return GridOutcome.UnknownItem;
        }

        if (item.CategoryId == categoryId)
        {
            return GridOutcome.Success;
        }

        var result = LayoutOf(categoryId).Add(itemId, item.Placement.Span);
        if (!result.Succeeded)
        {
            return result.Outcome;
        }

        var moved = item with { CategoryId = categoryId, Placement = result.Layout.Items[itemId] };
        Commit(State with { Items = State.Items.Select(existing => existing.Id == itemId ? moved : existing).ToList() });
        return GridOutcome.Success;
    }

    private static string CleanName(string name)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(name);

        var trimmed = name.Trim();
        return trimmed.Length <= MaxCategoryNameLength ? trimmed : trimmed[..MaxCategoryNameLength].TrimEnd();
    }

    private AddResult Add(string categoryId, GridSpan span, Func<string, GridPlacement, WidgetItem> create)
    {
        var id = _newId();
        var result = LayoutOf(categoryId).Add(id, span);
        if (!result.Succeeded)
        {
            return new AddResult(result.Outcome, null);
        }

        var item = create(id, result.Layout.Items[id]);
        Commit(State with { Items = [.. State.Items, item] });
        return new AddResult(GridOutcome.Success, item);
    }

    private GridOutcome ApplyToLayout(string itemId, Func<GridLayout, GridResult> operation)
    {
        if (Find(itemId) is not { } item)
        {
            return GridOutcome.UnknownItem;
        }

        var result = operation(LayoutOf(item.CategoryId));
        if (!result.Succeeded)
        {
            return result.Outcome;
        }

        var placements = result.Layout.Items;
        var items = State.Items
            .Select(existing => placements.TryGetValue(existing.Id, out var placement) && existing.CategoryId == item.CategoryId
                ? existing with { Placement = placement }
                : existing)
            .ToList();
        Commit(State with { Items = items });
        return GridOutcome.Success;
    }

    private void EnsureCategory(string categoryId)
    {
        if (!State.Categories.Any(category => category.Id == categoryId))
        {
            throw new ArgumentException($"Category '{categoryId}' does not exist.", nameof(categoryId));
        }
    }

    private void Commit(WidgetState state)
    {
        State = state;
        Save();
        Changed?.Invoke(this, EventArgs.Empty);
    }

    private void Save()
    {
        try
        {
            _store.Save(State);
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            LogSaveFailed(exception);
            SaveFailed?.Invoke(this, new SaveFailedEventArgs(exception));
        }
    }

    [LoggerMessage(Level = LogLevel.Error, Message = "Widget state could not be saved; the change is kept in memory")]
    private partial void LogSaveFailed(Exception exception);
}
