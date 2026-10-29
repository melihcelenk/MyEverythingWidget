namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Keeps UI tests from opening windows on a developer's desktop.
/// </summary>
internal static class SandboxGuard
{
    /// <summary>Set to <c>1</c> by the sandbox runner (scripts/test-ui.ps1).</summary>
    public const string SandboxVariable = "MEW_UI_TEST_SANDBOX";

    /// <summary>Set to <c>1</c> to run UI tests outside the sandbox on purpose.</summary>
    public const string AllowDesktopVariable = "MEW_UI_TEST_ALLOW_DESKTOP";

    /// <summary>Skips the current test unless it runs inside the sandbox or desktop runs are explicitly allowed.</summary>
    public static void SkipUnlessAllowed() =>
        Assert.SkipUnless(
            IsSet(SandboxVariable) || IsSet(AllowDesktopVariable),
            $"UI tests run only in Windows Sandbox (scripts/test-ui.ps1); set {AllowDesktopVariable}=1 to run them here.");

    private static bool IsSet(string variable) => Environment.GetEnvironmentVariable(variable) == "1";
}
