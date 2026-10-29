using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Presentation;

/// <summary>
/// State of the widget window: title, always-on-top and the bounds it should reopen with.
/// </summary>
public sealed partial class MainViewModel : ObservableObject
{
    private readonly ISettingsStore _settingsStore;
    private AppSettings _settings;

    /// <summary>
    /// Creates the view model and loads the saved settings from <paramref name="settingsStore"/>.
    /// </summary>
    public MainViewModel(ISettingsStore settingsStore)
    {
        ArgumentNullException.ThrowIfNull(settingsStore);

        _settingsStore = settingsStore;
        _settings = settingsStore.Load();
    }

    /// <summary>Gets the window title.</summary>
    public string Title { get; } = "My Everything Widget";

    /// <summary>Gets a value indicating whether the window stays above other windows.</summary>
    public bool IsAlwaysOnTop => _settings.IsAlwaysOnTop;

    /// <summary>Gets the bounds the window had when it was last saved, if any.</summary>
    public PixelRect? SavedWindowBounds => _settings.WindowBounds;

    /// <summary>Records the current window bounds so the next launch reopens there.</summary>
    public void SaveWindowBounds(PixelRect bounds) => Update(_settings with { WindowBounds = bounds });

    [RelayCommand]
    private void ToggleAlwaysOnTop()
    {
        Update(_settings with { IsAlwaysOnTop = !_settings.IsAlwaysOnTop });
        OnPropertyChanged(nameof(IsAlwaysOnTop));
    }

    private void Update(AppSettings settings)
    {
        _settings = settings;
        _settingsStore.Save(settings);
    }
}
