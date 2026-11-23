using Microsoft.Extensions.Logging;
using MyEverythingWidget.Core.Family;
using Windows.ApplicationModel.AppExtensions;
using WidgetFamily;

namespace MyEverythingWidget.Infrastructure.Family;

/// <summary>
/// Finds the family members through the app extension catalog <see cref="FamilyContract.ExtensionName"/>. Works only
/// in the packaged app; unpackaged (development) runs find no members.
/// </summary>
public sealed partial class AppExtensionFamilyCatalog(ILogger<AppExtensionFamilyCatalog> logger) : IFamilyCatalog
{
    /// <inheritdoc />
    public async Task<IReadOnlyList<InstalledMember>> GetMembersAsync(CancellationToken cancellationToken)
    {
        try
        {
            var catalog = AppExtensionCatalog.Open(FamilyContract.ExtensionName);
            var extensions = await catalog.FindAllAsync().AsTask(cancellationToken).ConfigureAwait(false);
            var members = new List<InstalledMember>(extensions.Count);
            foreach (var extension in extensions)
            {
                var properties = await extension.GetExtensionPropertiesAsync().AsTask(cancellationToken).ConfigureAwait(false);
                if (FamilyMember.TryRead(extension.Id, extension.DisplayName, FamilyExtensionProperties.ToStrings(properties), out var member))
                {
                    members.Add(new InstalledMember(member!, extension.Package.InstalledDate));
                }
                else
                {
                    LogIncompleteDeclaration(extension.Package.Id.FullName, extension.Id);
                }
            }

            return members;
        }
        catch (Exception exception) when (exception is not OperationCanceledException)
        {
            // Not packaged, or the catalog is unavailable: the hub simply shows no members.
            LogCatalogUnavailable(exception);
            return [];
        }
    }

    [LoggerMessage(Level = LogLevel.Warning, Message = "Widget family extension {ExtensionId} in {Package} is incomplete and is skipped")]
    private partial void LogIncompleteDeclaration(string package, string extensionId);

    [LoggerMessage(Level = LogLevel.Information, Message = "Widget family catalog is not available")]
    private partial void LogCatalogUnavailable(Exception exception);
}
