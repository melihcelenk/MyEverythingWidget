using System.ComponentModel;
using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>Grid size following the window, and the one-cell compact mode.</summary>
public sealed class WindowLayoutTests
{
    private static BoardViewModel CreateBoard(params WidgetItem[] items) => new(new WidgetBoard(
        new InMemoryWidgetStateStore(new WidgetState(WidgetState.CurrentSchemaVersion, [new Category("c1", "General")], items)),
        () => "x",
        GridSize.Default,
        NullLogger<WidgetBoard>.Instance));

    private static List<string> ChangedProperties(INotifyPropertyChanged source)
    {
        var names = new List<string>();
        source.PropertyChanged += (_, e) => names.Add(e.PropertyName!);
        return names;
    }

    [Fact]
    public void SavedGridSize_WithoutSettings_IsDefault()
    {
        Assert.Equal(GridSize.Default, new MainViewModel(new InMemorySettingsStore(AppSettings.Default)).SavedGridSize);
    }

    [Fact]
    public void SaveGridSize_IsStoredAndReadBack()
    {
        var store = new InMemorySettingsStore(AppSettings.Default);

        new MainViewModel(store).SaveGridSize(new GridSize(3, 4));

        Assert.Equal(new GridSize(3, 4), store.Current.GridSize);
        Assert.Equal(new GridSize(3, 4), new MainViewModel(store).SavedGridSize);
    }

    [Fact]
    public void ToggleCompact_SwitchesNotifiesAndSaves()
    {
        var store = new InMemorySettingsStore(AppSettings.Default);
        var viewModel = new MainViewModel(store);
        var changed = ChangedProperties(viewModel);

        viewModel.ToggleCompactCommand.Execute(null);

        Assert.True(viewModel.IsCompact);
        Assert.True(store.Current.IsCompact);
        Assert.Contains(nameof(MainViewModel.IsCompact), changed);

        viewModel.ToggleCompactCommand.Execute(null);

        Assert.False(viewModel.IsCompact);
        Assert.False(store.Current.IsCompact);
    }

    [Fact]
    public void ResizeGrid_ChangesGridSizeAndNotifies()
    {
        var board = CreateBoard();
        var changed = ChangedProperties(board);

        var applied = board.ResizeGrid(new GridSize(3, 2));

        Assert.Equal(new GridSize(3, 2), applied);
        Assert.Equal(new GridSize(3, 2), board.GridSize);
        Assert.Contains(nameof(BoardViewModel.GridSize), changed);
    }

    [Fact]
    public void ResizeGrid_StopsAtItemsAndMinimum()
    {
        var board = CreateBoard(new NoteItem("n1", "c1", new GridPlacement(2, 1, 2, 1), "x"));

        Assert.Equal(new GridSize(Rows: 3, Columns: 3), board.MinimumGridSize);
        Assert.Equal(new GridSize(Rows: 3, Columns: 3), board.ResizeGrid(new GridSize(1, 1)));
    }
}
