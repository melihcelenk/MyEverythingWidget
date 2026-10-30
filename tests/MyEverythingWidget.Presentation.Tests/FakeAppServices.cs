using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

internal sealed class FakeAppServices : IIconStore, IAppLauncher, IInstalledAppsSource
{
    public List<InstalledApp> Apps { get; } = [];

    public List<LaunchTarget> IconRequests { get; } = [];

    public List<string> DeletedIcons { get; } = [];

    public List<AppItem> Launched { get; } = [];

    public LaunchOutcome NextLaunchOutcome { get; set; } = LaunchOutcome.Started;

    public string? IconToReturn { get; set; } = "icons/fake.png";

    public string? ImportedIcon { get; set; } = "icons/imported.png";

    public Task<string?> ImportIconAsync(Stream image, CancellationToken cancellationToken) => Task.FromResult(ImportedIcon);

    public Task<IReadOnlyList<InstalledApp>> GetAppsAsync(CancellationToken cancellationToken) =>
        Task.FromResult<IReadOnlyList<InstalledApp>>(Apps);

    public Task<string?> CreateIconAsync(LaunchTarget target, CancellationToken cancellationToken)
    {
        IconRequests.Add(target);
        return Task.FromResult(IconToReturn);
    }

    public void DeleteIcon(string relativePath) => DeletedIcons.Add(relativePath);

    public LaunchOutcome Launch(AppItem app)
    {
        Launched.Add(app);
        return NextLaunchOutcome;
    }
}
