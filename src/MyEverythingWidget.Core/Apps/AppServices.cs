using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Apps;

/// <summary>
/// An app the user has installed, as listed in the Start menu.
/// </summary>
/// <param name="Name">Name shown in the Start menu.</param>
/// <param name="Target">Launch target, for example <c>shell:AppsFolder\Microsoft.WindowsNotepad_8wekyb3d8bbwe!App</c>.</param>
public sealed record InstalledApp(string Name, string Target);

/// <summary>Lists installed apps.</summary>
public interface IInstalledAppsSource
{
    /// <summary>Returns the installed apps of the current user, sorted by name.</summary>
    Task<IReadOnlyList<InstalledApp>> GetAppsAsync(CancellationToken cancellationToken);
}

/// <summary>Creates and removes the icon files of app cards.</summary>
public interface IIconStore
{
    /// <summary>
    /// Saves the icon of <paramref name="target"/> and returns its path relative to the data folder, or
    /// <see langword="null"/> when no icon could be obtained (the card then shows a monogram).
    /// </summary>
    Task<string?> CreateIconAsync(LaunchTarget target, CancellationToken cancellationToken);

    /// <summary>
    /// Saves a picked image as an icon and returns its path relative to the data folder, or <see langword="null"/>
    /// when <paramref name="image"/> is not an image.
    /// </summary>
    Task<string?> ImportIconAsync(Stream image, CancellationToken cancellationToken);

    /// <summary>Deletes an icon created by this store; missing files are ignored.</summary>
    void DeleteIcon(string relativePath);
}

/// <summary>Result of opening an app card.</summary>
public enum LaunchOutcome
{
    /// <summary>The target was opened.</summary>
    Started,

    /// <summary>The file, folder or app no longer exists.</summary>
    TargetMissing,

    /// <summary>Windows refused to open the target.</summary>
    Failed,
}

/// <summary>Opens app cards.</summary>
public interface IAppLauncher
{
    /// <summary>Opens <paramref name="app"/>: runs the program, opens the URL in the browser or the folder in Explorer.</summary>
    LaunchOutcome Launch(AppItem app);
}

/// <summary>Stand-ins used when no Windows services are wired (for example in tests).</summary>
public sealed class NoAppServices : IIconStore, IAppLauncher
{
    /// <summary>Gets the shared instance.</summary>
    public static NoAppServices Instance { get; } = new();

    /// <inheritdoc />
    public Task<string?> CreateIconAsync(LaunchTarget target, CancellationToken cancellationToken) => Task.FromResult<string?>(null);

    /// <inheritdoc />
    public Task<string?> ImportIconAsync(Stream image, CancellationToken cancellationToken) => Task.FromResult<string?>(null);

    /// <inheritdoc />
    public void DeleteIcon(string relativePath)
    {
        // Nothing was created, so there is nothing to delete.
    }

    /// <inheritdoc />
    public LaunchOutcome Launch(AppItem app) => LaunchOutcome.Failed;
}
