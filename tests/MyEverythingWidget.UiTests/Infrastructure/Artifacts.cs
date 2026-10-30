using FlaUI.Core.Capturing;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Screenshots for review and failure analysis, written to <c>MEW_UI_TEST_ARTIFACTS</c> (results\shots in the sandbox).
/// </summary>
internal static class Artifacts
{
    private const string Variable = "MEW_UI_TEST_ARTIFACTS";

    public static string PathOf(string name)
    {
        var directory = Environment.GetEnvironmentVariable(Variable) ?? Path.Combine(Path.GetTempPath(), "mew-shots");
        Directory.CreateDirectory(directory);
        return Path.Combine(directory, name + ".png");
    }

    public static void CaptureScreen(string name) => Capture.Screen().ToFile(PathOf(name));
}
