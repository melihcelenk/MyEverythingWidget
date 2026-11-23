using CommunityToolkit.Mvvm.ComponentModel;
using MyEverythingWidget.Core.Family;
using WidgetFamily;

namespace MyEverythingWidget.Presentation;

/// <summary>A family member shown on one side of the compact icon.</summary>
/// <param name="Edge">The side.</param>
/// <param name="MemberId">The member's id.</param>
/// <param name="Name">The member's display name.</param>
/// <param name="IsInstalled">False when the slot offers the member for download.</param>
public sealed record FamilySlot(Edge Edge, string MemberId, string Name, bool IsInstalled);

/// <summary>
/// The compact icon's right-click menu (MEW-5): the installed widget family members on the icon's four sides.
/// The list is read again every time the menu opens, so installed and removed members show up without a restart.
/// Members opened from the menu follow the icon: they move with it and hide while it hides. Published family widgets
/// that are not installed (<paramref name="known"/>) are offered for download on the edges left free.
/// </summary>
public sealed partial class FamilyMenuViewModel(
    IFamilyCatalog catalog,
    IFamilyLauncher launcher,
    IFamilyHub hub,
    IReadOnlyList<KnownFamilyMember> known) : ObservableObject
{
    private IReadOnlyDictionary<Edge, FamilyMember> _members = new Dictionary<Edge, FamilyMember>();

    /// <summary>Store product ids of the members on the menu that are not installed.</summary>
    private Dictionary<string, string> _toDownload = new(StringComparer.Ordinal);

    /// <summary>The members opened from the menu, and the side they were opened on.</summary>
    private readonly Dictionary<string, Edge> _opened = new(StringComparer.Ordinal);

    /// <summary>The member above the icon, if any.</summary>
    [ObservableProperty]
    public partial FamilySlot? Top { get; private set; }

    /// <summary>The member right of the icon, if any.</summary>
    [ObservableProperty]
    public partial FamilySlot? Right { get; private set; }

    /// <summary>The member below the icon, if any.</summary>
    [ObservableProperty]
    public partial FamilySlot? Bottom { get; private set; }

    /// <summary>The member left of the icon, if any.</summary>
    [ObservableProperty]
    public partial FamilySlot? Left { get; private set; }

    /// <summary>Whether any member is installed.</summary>
    [ObservableProperty]
    public partial bool HasMembers { get; private set; }

    /// <summary>Reads the installed members and assigns their edges.</summary>
    /// <param name="cancellationToken">Cancels the lookup.</param>
    /// <returns>A task that completes when the slots are updated.</returns>
    public async Task RefreshAsync(CancellationToken cancellationToken)
    {
        var installed = await catalog.GetMembersAsync(cancellationToken).ConfigureAwait(true);
        var installedIds = installed.Select(member => member.Member.Id).ToHashSet(StringComparer.Ordinal);
        var missing = known.Where(offer => !installedIds.Contains(offer.Member.Id)).ToList();
        _toDownload = missing.ToDictionary(offer => offer.Member.Id, offer => offer.StoreProductId, StringComparer.Ordinal);

        // Installed members choose first; members to download take the edges left.
        _members = EdgeAssignment.Assign(installed.Concat(missing.Select(offer => new InstalledMember(offer.Member, DateTimeOffset.MaxValue))));
        Top = Slot(Edge.Top);
        Right = Slot(Edge.Right);
        Bottom = Slot(Edge.Bottom);
        Left = Slot(Edge.Left);
        HasMembers = _members.Count > 0;

        // A member that was removed (or lost its edge) no longer follows the icon.
        foreach (var id in _opened.Keys.ToList())
        {
            if (!_members.Any(entry => entry.Value.Id == id && entry.Key == _opened[id]))
            {
                _opened.Remove(id);
            }
        }
    }

    /// <summary>Opens the member on <paramref name="edge"/> next to the icon.</summary>
    /// <param name="edge">The side.</param>
    /// <param name="icon">The icon's window bounds in physical pixels.</param>
    /// <returns>False when no member is on that side or Windows did not launch it.</returns>
    public async Task<bool> OpenAsync(Edge edge, PixelRect icon)
    {
        if (!_members.TryGetValue(edge, out var member))
        {
            return false;
        }

        if (_toDownload.TryGetValue(member.Id, out var productId))
        {
            return await launcher.OpenStorePageAsync(productId).ConfigureAwait(true);
        }

        if (!await launcher.OpenAsync(member, edge, icon).ConfigureAwait(true))
        {
            return false;
        }

        _opened[member.Id] = edge;
        return true;
    }

    /// <summary>The icon moved: the members opened from it move along to the same sides.</summary>
    /// <param name="icon">The icon's new window bounds in physical pixels.</param>
    /// <returns>A task that completes when the messages are sent.</returns>
    public async Task FollowAsync(PixelRect icon)
    {
        foreach (var (id, edge) in _opened.ToList())
        {
            await hub.SendAsync(id, FamilyMessage.Place(edge, icon)).ConfigureAwait(true);
        }
    }

    /// <summary>The icon was hidden (a full-screen app is in front) or shown again: the opened members follow.</summary>
    /// <param name="hidden">Whether the icon is hidden now.</param>
    /// <returns>A task that completes when the messages are sent.</returns>
    public async Task SetHiddenAsync(bool hidden)
    {
        var message = hidden ? FamilyMessage.Hide() : FamilyMessage.Show();
        foreach (var id in _opened.Keys.ToList())
        {
            await hub.SendAsync(id, message).ConfigureAwait(true);
        }
    }

    private FamilySlot? Slot(Edge edge) =>
        _members.TryGetValue(edge, out var member)
            ? new FamilySlot(edge, member.Id, member.DisplayName, !_toDownload.ContainsKey(member.Id))
            : null;
}
