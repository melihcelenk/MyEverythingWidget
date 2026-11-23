using WidgetFamily;

namespace MyEverythingWidget.Core.Family;

/// <summary>A family member installed on this PC.</summary>
/// <param name="Member">The member's declaration.</param>
/// <param name="InstalledAt">When its package was installed; the earlier one keeps a contested edge.</param>
public sealed record InstalledMember(FamilyMember Member, DateTimeOffset InstalledAt);

/// <summary>Finds the widget family members installed on this PC.</summary>
public interface IFamilyCatalog
{
    /// <summary>Lists the installed members whose declaration is complete.</summary>
    /// <param name="cancellationToken">Cancels the lookup.</param>
    /// <returns>The members; empty when none is installed or the lookup is not available.</returns>
    Task<IReadOnlyList<InstalledMember>> GetMembersAsync(CancellationToken cancellationToken);
}

/// <summary>Sends messages to the family members connected to the hub.</summary>
public interface IFamilyHub
{
    /// <summary>Sends <paramref name="message"/> to the member <paramref name="memberId"/>.</summary>
    /// <param name="memberId">The member's id.</param>
    /// <param name="message">The message.</param>
    /// <returns>False when the member is not connected.</returns>
    Task<bool> SendAsync(string memberId, FamilyMessage message);
}

/// <summary>Opens a family member next to the hub.</summary>
public interface IFamilyLauncher
{
    /// <summary>Opens <paramref name="member"/> on the <paramref name="edge"/> side of <paramref name="anchor"/>.</summary>
    /// <param name="member">The member.</param>
    /// <param name="edge">The side of the hub.</param>
    /// <param name="anchor">The hub's window bounds in physical pixels.</param>
    /// <returns>Whether Windows accepted the launch.</returns>
    Task<bool> OpenAsync(FamilyMember member, Edge edge, PixelRect anchor);
}
