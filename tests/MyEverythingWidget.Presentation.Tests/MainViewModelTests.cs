using System.ComponentModel;
using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Presentation.Tests;

public sealed class MainViewModelTests
{
    private static readonly PixelRect SavedBounds = new(300, 200, 404, 480);

    [Fact]
    public void Title_IsProductName()
    {
        var viewModel = new MainViewModel(new InMemorySettingsStore(AppSettings.Default));

        Assert.Equal("My Everything Widget", viewModel.Title);
    }

    [Fact]
    public void Constructor_LoadsSavedSettings()
    {
        var store = new InMemorySettingsStore(new AppSettings(IsAlwaysOnTop: true, WindowBounds: SavedBounds));

        var viewModel = new MainViewModel(store);

        Assert.True(viewModel.IsAlwaysOnTop);
        Assert.Equal(SavedBounds, viewModel.SavedWindowBounds);
    }

    [Fact]
    public void ToggleAlwaysOnTop_WhenOff_TurnsOnAndSavesKeepingBounds()
    {
        var store = new InMemorySettingsStore(new AppSettings(IsAlwaysOnTop: false, WindowBounds: SavedBounds));
        var viewModel = new MainViewModel(store);

        viewModel.ToggleAlwaysOnTopCommand.Execute(null);

        Assert.True(viewModel.IsAlwaysOnTop);
        Assert.Equal(new AppSettings(IsAlwaysOnTop: true, WindowBounds: SavedBounds), store.Current);
    }

    [Fact]
    public void ToggleAlwaysOnTop_Twice_TurnsBackOffAndSaves()
    {
        var store = new InMemorySettingsStore(AppSettings.Default);
        var viewModel = new MainViewModel(store);

        viewModel.ToggleAlwaysOnTopCommand.Execute(null);
        viewModel.ToggleAlwaysOnTopCommand.Execute(null);

        Assert.False(viewModel.IsAlwaysOnTop);
        Assert.False(store.Current.IsAlwaysOnTop);
        Assert.Equal(2, store.SaveCount);
    }

    [Fact]
    public void ToggleAlwaysOnTop_RaisesPropertyChanged()
    {
        var viewModel = new MainViewModel(new InMemorySettingsStore(AppSettings.Default));
        var changed = new List<string?>();
        ((INotifyPropertyChanged)viewModel).PropertyChanged += (_, e) => changed.Add(e.PropertyName);

        viewModel.ToggleAlwaysOnTopCommand.Execute(null);

        Assert.Contains(nameof(MainViewModel.IsAlwaysOnTop), changed);
    }

    [Fact]
    public void SaveWindowBounds_SavesBoundsKeepingAlwaysOnTop()
    {
        var store = new InMemorySettingsStore(new AppSettings(IsAlwaysOnTop: true, WindowBounds: null));
        var viewModel = new MainViewModel(store);
        var moved = new PixelRect(10, 20, 404, 480);

        viewModel.SaveWindowBounds(moved);

        Assert.Equal(new AppSettings(IsAlwaysOnTop: true, WindowBounds: moved), store.Current);
        Assert.Equal(moved, viewModel.SavedWindowBounds);
    }
}
