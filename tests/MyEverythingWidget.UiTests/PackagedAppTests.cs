using MyEverythingWidget.UiTests.Infrastructure;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Checks the installed MSIX package. Runs only where the package is installed (the sandbox runner sets
/// <see cref="AppUserModelIdVariable"/>); elsewhere the test is skipped.
/// </summary>
public sealed class PackagedAppTests
{
    private const string AppUserModelIdVariable = "MEW_APP_AUMID";

    [Fact]
    public void PackagedApp_LaunchesAndSavesSettingsInPackageFolder()
    {
        var appUserModelId = Environment.GetEnvironmentVariable(AppUserModelIdVariable);
        Assert.SkipWhen(string.IsNullOrWhiteSpace(appUserModelId), $"{AppUserModelIdVariable} is not set; the MSIX package is not installed here.");

        var packageFamilyName = appUserModelId!.Split('!')[0];
        var settingsFile = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Packages", packageFamilyName, "LocalState", "settings.json");

        using var app = AppSession.LaunchPackaged(appUserModelId);
        Assert.Equal(AppSession.WindowTitle, app.MainWindow.Title);

        app.ClickCloseAndWaitForExit();

        Assert.True(File.Exists(settingsFile), $"Expected settings in the package folder: {settingsFile}");
    }
}
