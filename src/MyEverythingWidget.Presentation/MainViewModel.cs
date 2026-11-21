using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MyEverythingWidget.Core.Geometry;
using MyEverythingWidget.Core.Grid;
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

    /// <summary>Gets or sets the colour theme; changes are saved.</summary>
    public AppTheme Theme
    {
        get => _settings.Theme;
        set
        {
            if (value != _settings.Theme)
            {
                Update(_settings with { Theme = value });
                OnPropertyChanged();
            }
        }
    }

    /// <summary>Gets the language code the user chose; <see langword="null"/> follows the Windows display language.</summary>
    public string? Language => _settings.Language;

    /// <summary>
    /// Saves <paramref name="language"/> (<see langword="null"/> for the Windows language); returns whether it changed.
    /// The new language is shown after the app restarts.
    /// </summary>
    public bool SetLanguage(string? language)
    {
        if (string.Equals(language, _settings.Language, StringComparison.Ordinal))
        {
            return false;
        }

        Update(_settings with { Language = language });
        OnPropertyChanged(nameof(Language));
        return true;
    }

    /// <summary>Gets the app version, for the About section.</summary>
    public string Version { get; } = typeof(MainViewModel).Assembly.GetName().Version?.ToString(3) ?? "0.0.0";

    /// <summary>Gets the bounds the window had when it was last saved, if any.</summary>
    public PixelRect? SavedWindowBounds => _settings.WindowBounds;

    /// <summary>Records the current window bounds so the next launch reopens there.</summary>
    public void SaveWindowBounds(PixelRect bounds) => Update(_settings with { WindowBounds = bounds });

    /// <summary>Gets the grid size the window reopens with.</summary>
    public GridSize SavedGridSize => _settings.GridSize ?? GridSize.Default;

    /// <summary>Records the grid size the user resized the window to.</summary>
    public void SaveGridSize(GridSize size)
    {
        if (size != _settings.GridSize)
        {
            Update(_settings with { GridSize = size });
        }
    }

    /// <summary>Gets a value indicating whether the widget is shrunk to its one-cell icon.</summary>
    public bool IsCompact => _settings.IsCompact;

    [RelayCommand]
    private void ToggleCompact()
    {
        Update(_settings with { IsCompact = !_settings.IsCompact });
        OnPropertyChanged(nameof(IsCompact));
    }

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
