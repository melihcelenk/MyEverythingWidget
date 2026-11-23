using Microsoft.Extensions.Logging;
using MyEverythingWidget.Core.Family;
using WidgetFamily;

namespace MyEverythingWidget.Infrastructure.Family;

/// <summary>Opens a member through its protocol with an <see cref="ActivationUri"/> open request.</summary>
public sealed partial class UriFamilyLauncher(ILogger<UriFamilyLauncher> logger) : IFamilyLauncher
{
    /// <inheritdoc />
    public async Task<bool> OpenAsync(FamilyMember member, Edge edge, PixelRect anchor)
    {
        ArgumentNullException.ThrowIfNull(member);
        var uri = ActivationUri.BuildOpen(member.Protocol, edge, anchor);
        var launched = await Windows.System.Launcher.LaunchUriAsync(uri);
        if (!launched)
        {
            LogLaunchFailed(member.Id, uri);
        }

        return launched;
    }

    /// <inheritdoc />
    public async Task<bool> OpenStorePageAsync(string productId)
    {
        var uri = new Uri("ms-windows-store://pdp/?ProductId=" + Uri.EscapeDataString(productId));
        var launched = await Windows.System.Launcher.LaunchUriAsync(uri);
        if (!launched)
        {
            LogLaunchFailed(productId, uri);
        }

        return launched;
    }

    [LoggerMessage(Level = LogLevel.Warning, Message = "Widget family member {MemberId} could not be opened with {Uri}")]
    private partial void LogLaunchFailed(string memberId, Uri uri);
}
