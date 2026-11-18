using System.ComponentModel;
using System.Diagnostics;
using Microsoft.Extensions.Logging;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Infrastructure.Shell;

/// <summary>
/// Opens app cards through the Windows shell, the same way as a double-click in Explorer would.
/// </summary>
public sealed partial class ShellLauncher(ILogger<ShellLauncher> logger) : IAppLauncher
{
    /// <inheritdoc />
    public LaunchOutcome Launch(AppItem app)
    {
        ArgumentNullException.ThrowIfNull(app);

        app = app with { Target = LaunchTarget.NormalizeTarget(app.LaunchKind, app.Target) };
        if (!Exists(app))
        {
            return LaunchOutcome.TargetMissing;
        }

        try
        {
            using var process = Process.Start(CreateStartInfo(app));
            return LaunchOutcome.Started;
        }
        catch (Exception exception) when (exception is Win32Exception or InvalidOperationException)
        {
            LogLaunchFailed(exception, app.Target);
            return LaunchOutcome.Failed;
        }
    }

    private static bool Exists(AppItem app) => app.LaunchKind switch
    {
        LaunchKind.Url => true,
        LaunchKind.Folder => Directory.Exists(app.Target),
        LaunchKind.Executable when app.Target.StartsWith(ShellAppsSource.AppsFolderPrefix, StringComparison.OrdinalIgnoreCase)
            => ShellNative.ItemFromParsingName(app.Target) is not null,
        LaunchKind.Executable => File.Exists(app.Target),
        _ => false,
    };

    private static ProcessStartInfo CreateStartInfo(AppItem app)
    {
        if (app.LaunchKind == LaunchKind.Folder || app.Target.StartsWith(ShellAppsSource.AppsFolderPrefix, StringComparison.OrdinalIgnoreCase))
        {
            // Explorer opens folders and Apps-folder entries (Store apps included).
            return new ProcessStartInfo("explorer.exe") { ArgumentList = { app.Target }, UseShellExecute = false };
        }

        var startInfo = new ProcessStartInfo(app.Target) { UseShellExecute = true };
        if (app.LaunchKind == LaunchKind.Executable && Path.GetDirectoryName(app.Target) is { Length: > 0 } directory)
        {
            startInfo.WorkingDirectory = directory;
        }

        return startInfo;
    }

    [LoggerMessage(Level = LogLevel.Error, Message = "Opening {Target} failed")]
    private partial void LogLaunchFailed(Exception exception, string target);
}
