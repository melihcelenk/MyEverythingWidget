using System.ComponentModel;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Presentation.Tests;

public sealed class SettingsViewModelTests
{
    [Fact]
    public void Theme_IsLoadedFromSettings()
    {
        var viewModel = new MainViewModel(new InMemorySettingsStore(AppSettings.Default with { Theme = AppTheme.Light }));

        Assert.Equal(AppTheme.Light, viewModel.Theme);
    }

    [Fact]
    public void SetTheme_SavesAndNotifies()
    {
        var store = new InMemorySettingsStore(AppSettings.Default with { IsAlwaysOnTop = true });
        var viewModel = new MainViewModel(store);
        var changed = new List<string?>();
        ((INotifyPropertyChanged)viewModel).PropertyChanged += (_, e) => changed.Add(e.PropertyName);

        viewModel.Theme = AppTheme.Dark;

        Assert.Equal(AppTheme.Dark, store.Current.Theme);
        Assert.True(store.Current.IsAlwaysOnTop);
        Assert.Contains(nameof(MainViewModel.Theme), changed);
    }

    [Fact]
    public void SetTheme_ToSameValue_DoesNotSave()
    {
        var store = new InMemorySettingsStore(AppSettings.Default);
        var viewModel = new MainViewModel(store);

        viewModel.Theme = AppTheme.System;

        Assert.Equal(0, store.SaveCount);
    }

    [Fact]
    public void Version_IsShown()
    {
        var viewModel = new MainViewModel(new InMemorySettingsStore(AppSettings.Default));

        Assert.Matches(@"^\d+\.\d+\.\d+", viewModel.Version);
    }
}
