using WidgetFamily;

namespace MyEverythingWidget.Core.Family;

/// <summary>
/// Which member sits on which side of the hub (S03 → A): each member gets its preferred edge; when it is taken, the
/// next free edge clockwise (top → right → bottom → left). Members are served in install order, so the one installed
/// first keeps a contested edge. With more than four members, the later ones get no edge.
/// </summary>
public static class EdgeAssignment
{
    private static readonly Edge[] Clockwise = [Edge.Top, Edge.Right, Edge.Bottom, Edge.Left];

    /// <summary>Assigns the edges.</summary>
    /// <param name="members">The installed members, in any order.</param>
    /// <returns>The member on each assigned edge.</returns>
    public static IReadOnlyDictionary<Edge, FamilyMember> Assign(IEnumerable<InstalledMember> members)
    {
        ArgumentNullException.ThrowIfNull(members);
        var edges = new Dictionary<Edge, FamilyMember>();
        var ordered = members
            .OrderBy(installed => installed.InstalledAt)
            .ThenBy(installed => installed.Member.Id, StringComparer.Ordinal);
        foreach (var installed in ordered)
        {
            if (FirstFreeFrom(installed.Member.PreferredEdge, edges) is { } edge)
            {
                edges[edge] = installed.Member;
            }
        }

        return edges;
    }

    private static Edge? FirstFreeFrom(Edge preferred, Dictionary<Edge, FamilyMember> taken)
    {
        var start = Array.IndexOf(Clockwise, preferred);
        for (var step = 0; step < Clockwise.Length; step++)
        {
            var edge = Clockwise[(start + step) % Clockwise.Length];
            if (!taken.ContainsKey(edge))
            {
                return edge;
            }
        }

        return null;
    }
}
