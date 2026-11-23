using System.Diagnostics;

namespace MyEverythingWidget.UiTests.Infrastructure;

/// <summary>
/// Puts text, a picture or a file on the clipboard and reads it back, through Windows PowerShell (STA, WinForms).
/// Used only inside the sandbox, where the clipboard belongs to the test.
/// </summary>
internal static class SandboxClipboard
{
    public static void SetText(string text)
    {
        var file = Path.Combine(Path.GetTempPath(), $"mew-clip-{Guid.NewGuid():N}.txt");
        File.WriteAllText(file, text);
        Run($"Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.Clipboard]::SetText([IO.File]::ReadAllText('{file}'))");
        File.Delete(file);
    }

    public static void SetPicture(int width, int height) =>
        Run("Add-Type -AssemblyName System.Windows.Forms, System.Drawing; "
            + $"$b = New-Object Drawing.Bitmap {width}, {height}; "
            + "$g = [Drawing.Graphics]::FromImage($b); $g.Clear([Drawing.Color]::SteelBlue); $g.Dispose(); "
            + "[Windows.Forms.Clipboard]::SetImage($b)");

    public static void SetFile(string path) =>
        Run("Add-Type -AssemblyName System.Windows.Forms; "
            + "$c = New-Object Collections.Specialized.StringCollection; "
            + $"[void]$c.Add('{path}'); [Windows.Forms.Clipboard]::SetFileDropList($c)");

    /// <summary>Gets a value indicating whether the clipboard holds a picture (as Paint or Word would paste it).</summary>
    public static bool HasPicture() =>
        Run("Add-Type -AssemblyName System.Windows.Forms; [Console]::Out.Write([Windows.Forms.Clipboard]::ContainsImage())")
            .Trim().Equals("True", StringComparison.OrdinalIgnoreCase);

    public static string GetText() =>
        Run("Add-Type -AssemblyName System.Windows.Forms; [Console]::Out.Write([Windows.Forms.Clipboard]::GetText())");

    private static string Run(string script)
    {
        // The clipboard is the developer's own outside the sandbox; a test that reaches here before launching the app
        // is skipped instead of overwriting it.
        SandboxGuard.SkipUnlessAllowed();
        var startInfo = new ProcessStartInfo("powershell.exe")
        {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            CreateNoWindow = true,
        };
        foreach (var argument in new[] { "-NoProfile", "-STA", "-Command", script })
        {
            startInfo.ArgumentList.Add(argument);
        }

        using var process = Process.Start(startInfo) ?? throw new InvalidOperationException("PowerShell did not start.");
        var output = process.StandardOutput.ReadToEnd();
        process.WaitForExit();
        return process.ExitCode == 0 ? output : throw new InvalidOperationException($"Clipboard script failed: {script}");
    }
}
