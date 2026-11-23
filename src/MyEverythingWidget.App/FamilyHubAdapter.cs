using MyEverythingWidget.Core.Family;
using WidgetFamily;

namespace MyEverythingWidget.App;

/// <summary>Sends the view model's family messages through the running hub (MEW-5).</summary>
internal sealed class FamilyHubAdapter(HubServer hub) : IFamilyHub
{
    /// <inheritdoc />
    public Task<bool> SendAsync(string memberId, FamilyMessage message) =>
        hub.SendAsync(memberId, message, CancellationToken.None);
}
