using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using MyEverythingWidget.Core.Apps;

namespace MyEverythingWidget.Presentation;

/// <summary>
/// The "Add app" dialog: pick an installed app (searchable list) or type a path or web address.
/// </summary>
public sealed partial class AddAppViewModel : ObservableObject
{
    /// <summary>Shown when the typed text is neither a full path nor a web address.</summary>
    public const string InvalidTargetMessage = "Enter a full path (C:\\...) or a web address (https://...).";

    private readonly BoardViewModel _board;
    private readonly IInstalledAppsSource _installedApps;
    private readonly Func<string, bool> _isDirectory;
    private IReadOnlyList<InstalledApp> _allApps = [];
    private LaunchTarget? _manualTarget;

    [ObservableProperty]
    public partial string SearchText { get; set; } = "";

    [ObservableProperty]
    public partial InstalledApp? SelectedApp { get; set; }

    [ObservableProperty]
    public partial string ManualText { get; set; } = "";

    [ObservableProperty]
    public partial string ManualName { get; set; } = "";

    [ObservableProperty]
    public partial string? ManualError { get; private set; }

    [ObservableProperty]
    public partial bool IsLoading { get; private set; }

    /// <summary>Creates the dialog view model that adds to <paramref name="board"/>'s open category.</summary>
    public AddAppViewModel(BoardViewModel board, IInstalledAppsSource installedApps, Func<string, bool> isDirectory)
    {
        ArgumentNullException.ThrowIfNull(board);
        ArgumentNullException.ThrowIfNull(installedApps);
        ArgumentNullException.ThrowIfNull(isDirectory);

        _board = board;
        _installedApps = installedApps;
        _isDirectory = isDirectory;
    }

    /// <summary>Gets the installed apps whose name contains <see cref="SearchText"/>; names starting with it come first.</summary>
    public ObservableCollection<InstalledApp> FilteredApps { get; } = [];

    /// <summary>Gets a value indicating whether there is something to add.</summary>
    public bool CanAdd => SelectedApp is not null || _manualTarget is not null;

    /// <summary>Gets a value indicating whether the typed text is a valid target (the name box is then shown).</summary>
    public bool CanAddManual => _manualTarget is not null;

    /// <summary>Loads the installed apps.</summary>
    public async Task LoadAsync(CancellationToken cancellationToken)
    {
        IsLoading = true;
        try
        {
            _allApps = await _installedApps.GetAppsAsync(cancellationToken).ConfigureAwait(true);
            ApplyFilter();
        }
        finally
        {
            IsLoading = false;
        }
    }

    /// <summary>Adds the selected app or the typed target; returns whether a card was added.</summary>
    public async Task<bool> AddAsync(CancellationToken cancellationToken)
    {
        if (SelectedApp is { } app)
        {
            var target = new LaunchTarget(Core.State.LaunchKind.Executable, app.Target, app.Name);
            return await _board.AddAppAsync(target, app.Name, cancellationToken).ConfigureAwait(true);
        }

        return _manualTarget is { } manual
            && await _board.AddAppAsync(manual, ManualName, cancellationToken).ConfigureAwait(true);
    }

    partial void OnSearchTextChanged(string value) => ApplyFilter();

    partial void OnSelectedAppChanged(InstalledApp? value)
    {
        if (value is not null && ManualText.Length > 0)
        {
            ManualText = "";
        }

        OnPropertyChanged(nameof(CanAdd));
    }

    partial void OnManualTextChanged(string value)
    {
        if (value.Length > 0)
        {
            SelectedApp = null;
        }

        _manualTarget = LaunchTarget.Classify(value, _isDirectory);
        ManualError = value.Trim().Length > 0 && _manualTarget is null ? InvalidTargetMessage : null;
        ManualName = _manualTarget?.SuggestedName ?? "";
        OnPropertyChanged(nameof(CanAdd));
        OnPropertyChanged(nameof(CanAddManual));
    }

    private void ApplyFilter()
    {
        var search = SearchText.Trim();
        var matches = _allApps
            .Where(app => search.Length == 0 || app.Name.Contains(search, StringComparison.CurrentCultureIgnoreCase))
            .OrderBy(app => app.Name.StartsWith(search, StringComparison.CurrentCultureIgnoreCase) ? 0 : 1)
            .ThenBy(app => app.Name, StringComparer.CurrentCultureIgnoreCase)
            .ToList();

        FilteredApps.Clear();
        foreach (var app in matches)
        {
            FilteredApps.Add(app);
        }
    }
}
