using MyEverythingWidget.Core.Apps;

namespace MyEverythingWidget.Infrastructure.Shell;

/// <summary>
/// Lists installed apps from the shell's Apps folder (<c>shell:AppsFolder</c>), which holds both desktop
/// programs and Store apps exactly as the Start menu shows them.
/// </summary>
public sealed class ShellAppsSource : IInstalledAppsSource
{
    /// <summary>Prefix of the launch target of an Apps-folder entry.</summary>
    public const string AppsFolderPrefix = @"shell:AppsFolder\";

    private const int Success = 0;

    /// <inheritdoc />
    public Task<IReadOnlyList<InstalledApp>> GetAppsAsync(CancellationToken cancellationToken) =>
        Task.Run<IReadOnlyList<InstalledApp>>(() => ReadApps(cancellationToken), cancellationToken);

    private static List<InstalledApp> ReadApps(CancellationToken cancellationToken)
    {
        if (ShellNative.SHGetKnownFolderItem(ShellNative.AppsFolderId, 0, 0, ShellNative.ShellItemId, out var folderPointer) < 0)
        {
            return [];
        }

        var folder = ShellNative.Wrap<IShellItem>(folderPointer);
        if (folder.BindToHandler(0, ShellNative.EnumItemsHandler, ShellNative.EnumShellItemsId, out var enumPointer) < 0)
        {
            return [];
        }

        var items = ShellNative.Wrap<IEnumShellItems>(enumPointer);
        var apps = new Dictionary<string, InstalledApp>(StringComparer.OrdinalIgnoreCase);
        while (!cancellationToken.IsCancellationRequested && items.Next(1, out var itemPointer, out var fetched) == Success && fetched == 1)
        {
            var item = ShellNative.Wrap<IShellItem>(itemPointer);
            var name = ShellNative.Name(item, ShellItemName.NormalDisplay);
            var id = ShellNative.Name(item, ShellItemName.ParentRelativeParsing);
            if (!string.IsNullOrWhiteSpace(name) && !string.IsNullOrWhiteSpace(id))
            {
                apps.TryAdd(id, new InstalledApp(name, AppsFolderPrefix + id));
            }
        }

        return apps.Values.OrderBy(app => app.Name, StringComparer.CurrentCultureIgnoreCase).ToList();
    }
}
