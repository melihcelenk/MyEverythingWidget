using System.Collections.ObjectModel;
using System.Globalization;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.Presentation;

/// <summary>Severity of the message in the status bar.</summary>
public enum StatusSeverity
{
    /// <summary>Neutral information.</summary>
    Informational,

    /// <summary>Something did not happen, but nothing is lost.</summary>
    Warning,

    /// <summary>Something failed and the user should know.</summary>
    Error,
}

/// <summary>Where an item would land and whether it can land there.</summary>
/// <param name="Placement">Cells to highlight.</param>
/// <param name="CanDrop">Whether releasing now would apply the change.</param>
public sealed record DropPreview(GridPlacement Placement, bool CanDrop);

/// <summary>
/// The grid of the selected category: its cards, drag-and-drop and resize, and the status message.
/// </summary>
public sealed partial class BoardViewModel : ObservableObject
{
    /// <summary>Message when displaced items have nowhere to go.</summary>
    public static string NoRoomMessage => Strings.NoRoom;

    /// <summary>Message when a category has no free place left.</summary>
    public static string GridFullMessage => Strings.GridFull;

    /// <summary>Name given to a category created with the "+" button, before the user renames it.</summary>
    public static string NewCategoryName => Strings.NewCategoryName;

    /// <summary>Message when an image file or pasted picture cannot be decoded.</summary>
    public static string ImageNotReadMessage => Strings.ImageNotRead;

    /// <summary>Message when some dropped or pasted things could not be turned into cards.</summary>
    public static string SomeNotAddedMessage => Strings.SomeNotAdded;

    private readonly WidgetBoard _board;
    private readonly IIconStore _icons;
    private readonly IAppLauncher _launcher;
    private readonly IImageStore? _images;

    [ObservableProperty]
    public partial string? StatusMessage { get; private set; }

    [ObservableProperty]
    public partial StatusSeverity StatusSeverity { get; private set; }

    [ObservableProperty]
    public partial string SelectedCategoryId { get; private set; }

    /// <summary>Creates the view model over <paramref name="board"/> and shows its open category.</summary>
    public BoardViewModel(WidgetBoard board, IIconStore? icons = null, IAppLauncher? launcher = null, IImageStore? images = null)
    {
        ArgumentNullException.ThrowIfNull(board);

        _board = board;
        _icons = icons ?? NoAppServices.Instance;
        _launcher = launcher ?? NoAppServices.Instance;
        _images = images;
        SelectedCategoryId = board.SelectedCategoryId;
        Synchronize();

        board.Changed += (_, _) => Synchronize();
        board.SaveFailed += (_, e) => ShowStatus(
            Strings.SaveFailed(e.Exception.Message),
            StatusSeverity.Error);

        if (board.CorruptBackupPath is { } backupPath)
        {
            ShowStatus(
                Strings.StateUnreadable(backupPath),
                StatusSeverity.Warning);
        }
    }

    /// <summary>Gets the cards of the selected category.</summary>
    public ObservableCollection<GridItemViewModel> Items { get; } = [];

    /// <summary>Shows the result of importing the previous version's data, when there is something to tell.</summary>
    public void ShowMigrationResult(MigrationResult result)
    {
        ArgumentNullException.ThrowIfNull(result);

        if (result.Message is { } message)
        {
            var severity = result.Outcome == MigrationOutcome.Imported && result.MissingImages == 0
                ? StatusSeverity.Informational
                : StatusSeverity.Warning;
            ShowStatus(message, severity);
        }
    }

    /// <summary>Gets the category tabs in order.</summary>
    public ObservableCollection<CategoryViewModel> Categories { get; } = [];

    /// <summary>Gets a value indicating whether a category may be deleted (the last one may not).</summary>
    public bool CanDeleteCategory => Categories.Count > 1;

    /// <summary>Gets the grid size.</summary>
    public GridSize GridSize => _board.GridSize;

    /// <summary>Gets the smallest grid that still holds every item.</summary>
    public GridSize MinimumGridSize => _board.MinimumGridSize;

    /// <summary>Changes the grid size (kept between <see cref="MinimumGridSize"/> and the maximum); returns the size applied.</summary>
    public GridSize ResizeGrid(GridSize requested)
    {
        var before = _board.GridSize;
        var applied = _board.ResizeGrid(requested);
        if (applied != before)
        {
            OnPropertyChanged(nameof(GridSize));
        }

        return applied;
    }

    /// <summary>Opens the tab of <paramref name="categoryId"/>.</summary>
    public void SelectCategory(string categoryId) => _board.SelectCategory(categoryId);

    /// <summary>Adds a category at the end of the tabs and opens it.</summary>
    public CategoryViewModel AddCategory(string name)
    {
        var category = _board.AddCategory(name);
        _board.SelectCategory(category.Id);
        return Categories.Single(tab => tab.Id == category.Id);
    }

    /// <summary>Renames a category; a blank name is ignored and returns <see langword="false"/>.</summary>
    public bool RenameCategory(string categoryId, string name) =>
        !string.IsNullOrWhiteSpace(name) && _board.RenameCategory(categoryId, name);

    /// <summary>Deletes a category and its items; returns <see langword="false"/> for the last category.</summary>
    public bool DeleteCategory(string categoryId) => _board.DeleteCategory(categoryId);

    /// <summary>Puts the tabs in the order of <paramref name="categoryIds"/>.</summary>
    public void ReorderCategories(IReadOnlyList<string> categoryIds) => _board.ReorderCategories(categoryIds);

    /// <summary>Returns the categories other than the open one, for "Move to".</summary>
    public IReadOnlyList<CategoryViewModel> OtherCategories() =>
        Categories.Where(category => category.Id != SelectedCategoryId).ToList();

    /// <summary>Moves a card to another category; shows a warning when that category is full.</summary>
    public bool MoveItemToCategory(string itemId, string categoryId)
    {
        var outcome = _board.MoveItemToCategory(itemId, categoryId);
        if (outcome == GridOutcome.GridFull)
        {
            var name = Categories.FirstOrDefault(category => category.Id == categoryId)?.Name ?? categoryId;
            ShowStatus(Strings.NoRoomIn(name), StatusSeverity.Warning);
            return false;
        }

        return Report(outcome);
    }

    /// <summary>Returns where item <paramref name="itemId"/> would land if dropped at <paramref name="target"/>.</summary>
    public DropPreview PreviewDrop(string itemId, GridCell target)
    {
        var placement = PlacementOf(itemId).MovedTo(target);
        return new DropPreview(placement, _board.LayoutOf(SelectedCategoryId).Move(itemId, target).Succeeded);
    }

    /// <summary>Drops item <paramref name="itemId"/> at <paramref name="target"/>; returns whether it moved.</summary>
    public bool Drop(string itemId, GridCell target) => Report(_board.Move(itemId, target));

    /// <summary>Returns the cells item <paramref name="itemId"/> would cover with <paramref name="span"/>.</summary>
    public DropPreview PreviewResize(string itemId, GridSpan span)
    {
        var placement = PlacementOf(itemId) with { Span = span };
        return new DropPreview(placement, _board.LayoutOf(SelectedCategoryId).Resize(itemId, span).Succeeded);
    }

    /// <summary>Gives item <paramref name="itemId"/> a new span; returns whether it changed.</summary>
    public bool Resize(string itemId, GridSpan span) => Report(_board.Resize(itemId, span));

    [RelayCommand]
    private void Delete(string itemId)
    {
        var item = _board.Find(itemId);
        if (!_board.Delete(itemId))
        {
            return;
        }

        switch (item)
        {
            case AppItem { IconPath: { } iconPath }:
                _icons.DeleteIcon(iconPath);
                break;
            case ImageItem image:
                _images?.Delete(image.ImagePath);
                break;
        }
    }

    /// <summary>Adds a 2x1 note to the open category; blank text adds nothing.</summary>
    public bool AddNote(string text) =>
        !string.IsNullOrWhiteSpace(text) && Report(_board.AddNote(SelectedCategoryId, text).Outcome);

    /// <summary>Replaces a note's text; blank text is ignored.</summary>
    public bool EditNote(string itemId, string text) => _board.UpdateNoteText(itemId, text);

    /// <summary>Uses a picked image as the icon of an app card; the previous icon file is deleted.</summary>
    public async Task<bool> ChangeIconAsync(string itemId, Stream image, CancellationToken cancellationToken = default)
    {
        var iconPath = await _icons.ImportIconAsync(image, cancellationToken).ConfigureAwait(true);
        if (iconPath is null)
        {
            ShowStatus(ImageNotReadMessage, StatusSeverity.Warning);
            return false;
        }

        ReplaceIcon(itemId, iconPath);
        return true;
    }

    /// <summary>Gives an app card its own icon again (of the program, folder or site).</summary>
    public async Task<bool> ResetIconAsync(string itemId, CancellationToken cancellationToken = default)
    {
        if (_board.Find(itemId) is not AppItem app)
        {
            return false;
        }

        var target = new LaunchTarget(app.LaunchKind, app.Target, app.Name);
        ReplaceIcon(itemId, await _icons.CreateIconAsync(target, cancellationToken).ConfigureAwait(true));
        return true;
    }

    /// <summary>
    /// Shows an emoji as the icon of an app card; only its first symbol is kept. Blank text changes nothing.
    /// The previous icon file is deleted.
    /// </summary>
    public bool SetEmoji(string itemId, string text)
    {
        if (IconEmoji.Normalize(text) is not { } emoji || _board.Find(itemId) is not AppItem)
        {
            return false;
        }

        if (_board.SetAppEmoji(itemId, emoji) is { } oldIcon)
        {
            _icons.DeleteIcon(oldIcon);
        }

        return true;
    }

    private void ReplaceIcon(string itemId, string? iconPath)
    {
        if (_board.SetAppIcon(itemId, iconPath) is { } oldIcon && oldIcon != iconPath)
        {
            _icons.DeleteIcon(oldIcon);
        }
    }

    /// <summary>Renames an app card; a blank name is ignored.</summary>
    public bool RenameApp(string itemId, string name) => _board.RenameApp(itemId, name);

    /// <summary>Adds an image card sized by the image's aspect ratio; returns whether it was added.</summary>
    public async Task<bool> AddImageAsync(Stream image, CancellationToken cancellationToken = default)
    {
        if (_images is null)
        {
            return false;
        }

        var stored = await _images.ImportAsync(image, cancellationToken).ConfigureAwait(true);
        if (stored is null)
        {
            ShowStatus(ImageNotReadMessage, StatusSeverity.Warning);
            return false;
        }

        var span = ImageSpan.FromPixelSize(stored.PixelWidth, stored.PixelHeight);
        var result = _board.AddImage(SelectedCategoryId, stored.RelativePath, stored.PixelWidth, stored.PixelHeight, span);
        if (result.Outcome != GridOutcome.Success)
        {
            _images.Delete(stored.RelativePath);
        }

        return Report(result.Outcome);
    }

    /// <summary>Adds an image card from an image file.</summary>
    public async Task<bool> AddImageFileAsync(string path, CancellationToken cancellationToken = default)
    {
        try
        {
            await using var stream = File.OpenRead(path);
            return await AddImageAsync(stream, cancellationToken).ConfigureAwait(true);
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException)
        {
            ShowStatus(ImageNotReadMessage, StatusSeverity.Warning);
            return false;
        }
    }

    /// <summary>
    /// Ctrl+V: a picture becomes an image card; image files become image cards; other files, folders and a
    /// single web address become app cards; any other text becomes a note.
    /// </summary>
    public async Task PasteAsync(PastedContent content, Func<string, bool> isDirectory)
    {
        ArgumentNullException.ThrowIfNull(content);

        if (content.OpenBitmap is not null && await content.OpenBitmap(CancellationToken.None).ConfigureAwait(true) is { } bitmap)
        {
            await using (bitmap.ConfigureAwait(true))
            {
                await AddImageAsync(bitmap).ConfigureAwait(true);
            }

            return;
        }

        if (content.FilePaths.Count > 0)
        {
            foreach (var image in content.FilePaths.Where(ImageFiles.IsImage))
            {
                await AddImageFileAsync(image).ConfigureAwait(true);
            }

            var others = content.FilePaths.Where(path => !ImageFiles.IsImage(path)).ToList();
            if (others.Count > 0)
            {
                await AddDroppedAsync(others, isDirectory).ConfigureAwait(true);
            }

            return;
        }

        var text = content.Text?.Trim();
        if (string.IsNullOrEmpty(text))
        {
            return;
        }

        var isSingleLine = text.IndexOfAny(['\r', '\n']) < 0;
        if (isSingleLine && LaunchTarget.Classify(text, isDirectory) is { } target)
        {
            await AddAppAsync(target, target.SuggestedName).ConfigureAwait(true);
        }
        else
        {
            AddNote(text);
        }
    }

    /// <summary>Adds an app card for <paramref name="target"/> with its icon; returns whether it was added.</summary>
    public async Task<bool> AddAppAsync(LaunchTarget target, string name, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(target);

        var iconPath = await _icons.CreateIconAsync(target, cancellationToken).ConfigureAwait(true);
        var label = string.IsNullOrWhiteSpace(name) ? target.SuggestedName : name;
        var result = _board.AddApp(SelectedCategoryId, label, target.Target, target.Kind, iconPath);
        if (result.Outcome != GridOutcome.Success && iconPath is not null)
        {
            _icons.DeleteIcon(iconPath);
        }

        return Report(result.Outcome);
    }

    /// <summary>Adds the picture itself that was dropped (for example an image dragged from a web page).</summary>
    public async Task<bool> AddDroppedPictureAsync(Func<CancellationToken, Task<Stream?>> openPicture)
    {
        ArgumentNullException.ThrowIfNull(openPicture);

        if (await openPicture(CancellationToken.None).ConfigureAwait(true) is not { } picture)
        {
            return false;
        }

        await using (picture.ConfigureAwait(true))
        {
            return await AddImageAsync(picture).ConfigureAwait(true);
        }
    }

    /// <summary>
    /// Adds a card for every dropped path or web address: image files become image cards, other files, folders and
    /// web addresses become app cards; shows a warning for the rest. Returns how many cards were added.
    /// </summary>
    public async Task<int> AddDroppedAsync(IReadOnlyList<string> texts, Func<string, bool> isDirectory)
    {
        ArgumentNullException.ThrowIfNull(texts);

        var added = 0;
        var skipped = false;
        foreach (var text in texts)
        {
            var path = text.Trim().Trim('"');
            if (Path.IsPathFullyQualified(path) && ImageFiles.IsImage(path) && File.Exists(path))
            {
                if (await AddImageFileAsync(path).ConfigureAwait(true))
                {
                    added++;
                }

                continue;
            }

            if (LaunchTarget.Classify(text, isDirectory) is { } target)
            {
                if (!await AddAppAsync(target, target.SuggestedName).ConfigureAwait(true))
                {
                    return added;
                }

                added++;
            }
            else
            {
                skipped = true;
            }
        }

        if (skipped)
        {
            ShowStatus(SomeNotAddedMessage, StatusSeverity.Warning);
        }

        return added;
    }

    /// <summary>Opens an app card; other cards are ignored. Shows why when it cannot be opened.</summary>
    public void Launch(string itemId)
    {
        if (_board.Find(itemId) is not AppItem app)
        {
            return;
        }

        switch (_launcher.Launch(app))
        {
            case LaunchOutcome.Started:
                break;
            case LaunchOutcome.TargetMissing:
                ShowStatus(
                    Strings.AppNotFound(app.Name),
                    StatusSeverity.Warning);
                break;
            case LaunchOutcome.Failed:
                ShowStatus(Strings.AppNotOpened(app.Name), StatusSeverity.Error);
                break;
            default:
                throw new InvalidOperationException("Unknown launch outcome.");
        }
    }

    [RelayCommand]
    private void DismissStatus() => StatusMessage = null;

    private GridPlacement PlacementOf(string itemId) =>
        _board.Find(itemId)?.Placement ?? throw new ArgumentException($"Item '{itemId}' does not exist.", nameof(itemId));

    private bool Report(GridOutcome outcome)
    {
        switch (outcome)
        {
            case GridOutcome.Success:
                return true;
            case GridOutcome.NoRoom:
                ShowStatus(NoRoomMessage, StatusSeverity.Warning);
                break;
            case GridOutcome.GridFull:
                ShowStatus(GridFullMessage, StatusSeverity.Warning);
                break;
            case GridOutcome.OutOfBounds:
            case GridOutcome.InvalidSpan:
            case GridOutcome.UnknownItem:
                // The drop preview already showed that the target was not allowed.
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(outcome), outcome, "Unknown grid outcome.");
        }

        return false;
    }

    /// <summary>Shows a warning that the view could not do something the user asked for.</summary>
    public void ReportProblem(string message)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(message);
        ShowStatus(message, StatusSeverity.Warning);
    }

    private void ShowStatus(string message, StatusSeverity severity)
    {
        StatusSeverity = severity;
        StatusMessage = message;
    }

    /// <summary>Brings the open tab, the tabs and the cards in line with the board.</summary>
    private void Synchronize()
    {
        if (SelectedCategoryId != _board.SelectedCategoryId)
        {
            SelectedCategoryId = _board.SelectedCategoryId;
            Items.Clear();
        }

        SynchronizeCategories();
        SynchronizeItems();
    }

    /// <summary>Brings <see cref="Categories"/> in line with the board, reusing existing tab view models.</summary>
    private void SynchronizeCategories()
    {
        var existing = Categories.ToDictionary(category => category.Id, StringComparer.Ordinal);
        var ordered = _board.Categories.Select(category =>
        {
            if (!existing.TryGetValue(category.Id, out var tab))
            {
                tab = new CategoryViewModel(category.Id, category.Name);
            }

            tab.Name = category.Name;
            tab.ItemCount = _board.ItemsIn(category.Id).Count();
            tab.IsSelected = category.Id == SelectedCategoryId;
            return tab;
        }).ToList();

        for (var index = Categories.Count - 1; index >= 0; index--)
        {
            if (!ordered.Contains(Categories[index]))
            {
                Categories.RemoveAt(index);
            }
        }

        for (var index = 0; index < ordered.Count; index++)
        {
            var position = Categories.IndexOf(ordered[index]);
            if (position < 0)
            {
                Categories.Insert(index, ordered[index]);
            }
            else if (position != index)
            {
                Categories.Move(position, index);
            }
        }

        OnPropertyChanged(nameof(CanDeleteCategory));
    }

    /// <summary>Brings <see cref="Items"/> in line with the open category, reusing existing card view models.</summary>
    private void SynchronizeItems()
    {
        var current = _board.ItemsIn(SelectedCategoryId).ToDictionary(item => item.Id, StringComparer.Ordinal);

        for (var index = Items.Count - 1; index >= 0; index--)
        {
            if (!current.ContainsKey(Items[index].Id))
            {
                Items.RemoveAt(index);
            }
        }

        var existing = Items.ToDictionary(item => item.Id, StringComparer.Ordinal);
        foreach (var item in current.Values)
        {
            if (existing.TryGetValue(item.Id, out var viewModel))
            {
                viewModel.Update(item);
            }
            else
            {
                Items.Add(new GridItemViewModel(item));
            }
        }
    }
}
