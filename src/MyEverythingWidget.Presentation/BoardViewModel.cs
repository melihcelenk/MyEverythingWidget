using System.Collections.ObjectModel;
using System.Globalization;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

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
    public const string NoRoomMessage = "There is no room to move the other items there.";

    /// <summary>Message when a category has no free place left.</summary>
    public const string GridFullMessage = "This category is full. Remove or shrink something first.";

    private readonly WidgetBoard _board;

    [ObservableProperty]
    public partial string? StatusMessage { get; private set; }

    [ObservableProperty]
    public partial StatusSeverity StatusSeverity { get; private set; }

    [ObservableProperty]
    public partial string SelectedCategoryId { get; private set; }

    /// <summary>Creates the view model over <paramref name="board"/> and shows its first category.</summary>
    public BoardViewModel(WidgetBoard board)
    {
        ArgumentNullException.ThrowIfNull(board);

        _board = board;
        SelectedCategoryId = board.Categories[0].Id;
        Synchronize();

        board.Changed += (_, _) => Synchronize();
        board.SaveFailed += (_, e) => ShowStatus(
            string.Create(CultureInfo.InvariantCulture, $"Changes could not be saved: {e.Exception.Message}"),
            StatusSeverity.Error);

        if (board.CorruptBackupPath is { } backupPath)
        {
            ShowStatus(
                string.Create(CultureInfo.InvariantCulture, $"Your saved items could not be read, so the widget started empty. A copy was kept at {backupPath}."),
                StatusSeverity.Warning);
        }
    }

    /// <summary>Gets the cards of the selected category.</summary>
    public ObservableCollection<GridItemViewModel> Items { get; } = [];

    /// <summary>Gets the grid size.</summary>
    public GridSize GridSize => _board.GridSize;

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
    private void Delete(string itemId) => _board.Delete(itemId);

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

    private void ShowStatus(string message, StatusSeverity severity)
    {
        StatusSeverity = severity;
        StatusMessage = message;
    }

    /// <summary>Brings <see cref="Items"/> in line with the board, reusing existing view models.</summary>
    private void Synchronize()
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
