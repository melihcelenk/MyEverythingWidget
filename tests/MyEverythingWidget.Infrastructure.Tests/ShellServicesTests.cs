using System.Net;
using Microsoft.Extensions.Logging.Abstractions;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.Infrastructure.Shell;

namespace MyEverythingWidget.Infrastructure.Tests;

/// <summary>
/// Read-only checks against the real Windows shell: listing apps and rendering icons. Nothing is launched,
/// so these run on any machine without opening windows.
/// </summary>
public sealed class ShellServicesTests : IDisposable
{
    private static readonly byte[] PngSignature = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];
    private readonly string _dataDirectory = Path.Combine(Path.GetTempPath(), "mew-infra-tests", Guid.NewGuid().ToString("N"));

    public void Dispose()
    {
        if (Directory.Exists(_dataDirectory))
        {
            Directory.Delete(_dataDirectory, recursive: true);
        }
    }

    private ShellIconStore CreateIconStore(ISiteIconSource? siteIcons = null) =>
        new(_dataDirectory, siteIcons ?? new FaviconSource(new HttpClient(new StubHandler(HttpStatusCode.NotFound, []))), NullLogger<ShellIconStore>.Instance);

    private void AssertIsPng(string? relativePath)
    {
        Assert.NotNull(relativePath);
        var bytes = File.ReadAllBytes(Path.Combine(_dataDirectory, relativePath));
        Assert.Equal(PngSignature, bytes.Take(PngSignature.Length));
    }

    [Fact]
    public async Task InstalledApps_AreListedWithAppsFolderTargets()
    {
        var apps = await new ShellAppsSource().GetAppsAsync(TestContext.Current.CancellationToken);

        Assert.NotEmpty(apps);
        Assert.All(apps, app => Assert.StartsWith(ShellAppsSource.AppsFolderPrefix, app.Target, StringComparison.Ordinal));
        Assert.Contains(apps, app => app.Name.Contains("Settings", StringComparison.OrdinalIgnoreCase)
            || app.Name.Contains("Notepad", StringComparison.OrdinalIgnoreCase)
            || app.Name.Contains("Explorer", StringComparison.OrdinalIgnoreCase));
    }

    [Fact]
    public async Task Icon_ForProgram_IsSavedAsPng()
    {
        var explorer = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "explorer.exe");

        var icon = await CreateIconStore().CreateIconAsync(new LaunchTarget(LaunchKind.Executable, explorer, "Explorer"), TestContext.Current.CancellationToken);

        AssertIsPng(icon);
        Assert.StartsWith("icons", icon, StringComparison.Ordinal);
    }

    [Fact]
    public async Task Icon_ForInstalledApp_IsSavedAsPng()
    {
        var app = (await new ShellAppsSource().GetAppsAsync(TestContext.Current.CancellationToken))[0];

        var icon = await CreateIconStore().CreateIconAsync(new LaunchTarget(LaunchKind.Executable, app.Target, app.Name), TestContext.Current.CancellationToken);

        AssertIsPng(icon);
    }

    [Fact]
    public async Task Icon_ForFolder_IsSavedAsPng()
    {
        var icon = await CreateIconStore().CreateIconAsync(new LaunchTarget(LaunchKind.Folder, Path.GetTempPath(), "Temp"), TestContext.Current.CancellationToken);

        AssertIsPng(icon);
    }

    [Fact]
    public async Task Icon_ForPathWithForwardSlashes_IsSavedAsPng()
    {
        var explorer = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "explorer.exe").Replace(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);

        var icon = await CreateIconStore().CreateIconAsync(new LaunchTarget(LaunchKind.Executable, explorer, "Explorer"), TestContext.Current.CancellationToken);

        AssertIsPng(icon);
    }

    [Fact]
    public async Task Icon_ForMissingFile_IsNull()
    {
        var icon = await CreateIconStore().CreateIconAsync(
            new LaunchTarget(LaunchKind.Executable, @"C:\does\not\exist\tool.exe", "Tool"), TestContext.Current.CancellationToken);

        Assert.Null(icon);
    }

    [Fact]
    public async Task Icon_ForWebsite_UsesItsFavicon()
    {
        var explorer = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "explorer.exe");
        var programIcon = await CreateIconStore().CreateIconAsync(new LaunchTarget(LaunchKind.Executable, explorer, "Explorer"), TestContext.Current.CancellationToken);
        var faviconBytes = File.ReadAllBytes(Path.Combine(_dataDirectory, programIcon!));
        var handler = new StubHandler(HttpStatusCode.OK, faviconBytes);
        var store = CreateIconStore(new FaviconSource(new HttpClient(handler)));

        var icon = await store.CreateIconAsync(new LaunchTarget(LaunchKind.Url, "https://example.org/some/page", "Example"), TestContext.Current.CancellationToken);

        AssertIsPng(icon);
        Assert.Equal(new Uri("https://example.org/favicon.ico"), handler.LastRequest);
    }

    [Fact]
    public async Task Icon_ForUnreachableWebsite_IsNull()
    {
        var icon = await CreateIconStore().CreateIconAsync(new LaunchTarget(LaunchKind.Url, "https://example.org", "Example"), TestContext.Current.CancellationToken);

        Assert.Null(icon);
    }

    [Fact]
    public async Task DeleteIcon_RemovesFile()
    {
        var store = CreateIconStore();
        var icon = await store.CreateIconAsync(new LaunchTarget(LaunchKind.Folder, Path.GetTempPath(), "Temp"), TestContext.Current.CancellationToken);

        store.DeleteIcon(icon!);

        Assert.False(File.Exists(Path.Combine(_dataDirectory, icon!)));
    }

    [Fact]
    public void DeleteIcon_OutsideIconFolder_IsIgnored()
    {
        Directory.CreateDirectory(_dataDirectory);
        var state = Path.Combine(_dataDirectory, "state.json");
        File.WriteAllText(state, "{}");

        CreateIconStore().DeleteIcon(@"..\" + Path.GetFileName(_dataDirectory) + @"\state.json");

        Assert.True(File.Exists(state));
    }

    [Theory]
    [InlineData(LaunchKind.Executable, @"C:\does\not\exist\tool.exe")]
    [InlineData(LaunchKind.Folder, @"C:\does\not\exist")]
    [InlineData(LaunchKind.Executable, @"shell:AppsFolder\No.Such.App_0000000000000!App")]
    public void Launch_MissingTarget_ReportsMissingWithoutStartingAnything(LaunchKind kind, string target)
    {
        var app = new AppItem("a1", "c1", new GridPlacement(0, 0, 1, 1), "Tool", target, kind, null);

        Assert.Equal(LaunchOutcome.TargetMissing, new ShellLauncher(NullLogger<ShellLauncher>.Instance).Launch(app));
    }

    private sealed class StubHandler(HttpStatusCode status, byte[] body) : HttpMessageHandler
    {
        public Uri? LastRequest { get; private set; }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            LastRequest = request.RequestUri;
            return Task.FromResult(new HttpResponseMessage(status) { Content = new ByteArrayContent(body) });
        }
    }
}
