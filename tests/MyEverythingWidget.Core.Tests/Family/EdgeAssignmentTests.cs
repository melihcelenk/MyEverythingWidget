using MyEverythingWidget.Core.Family;
using WidgetFamily;

namespace MyEverythingWidget.Core.Tests.Family;

/// <summary>S03 → A: each member gets its preferred edge; when taken, the next free edge clockwise.</summary>
public sealed class EdgeAssignmentTests
{
    private static readonly DateTimeOffset Day = new(2026, 11, 23, 0, 0, 0, TimeSpan.Zero);

    private static InstalledMember Member(string id, Edge preferred, int installedDay) =>
        new(new FamilyMember(id, id, id + "-widget", preferred), Day.AddDays(installedDay));

    [Fact]
    public void NoMembers_NoEdges()
    {
        Assert.Empty(EdgeAssignment.Assign([]));
    }

    [Fact]
    public void SingleMember_GetsItsPreferredEdge()
    {
        var edges = EdgeAssignment.Assign([Member("tasktimer", Edge.Right, 0)]);

        Assert.Equal("tasktimer", Assert.Single(edges).Value.Id);
        Assert.Equal(Edge.Right, edges.Single().Key);
    }

    [Fact]
    public void TwoMembersWantingTheSameEdge_TheFirstInstalledKeepsIt_TheOtherMovesClockwise()
    {
        var edges = EdgeAssignment.Assign([Member("notes", Edge.Right, 5), Member("tasktimer", Edge.Right, 1)]);

        Assert.Equal("tasktimer", edges[Edge.Right].Id);
        Assert.Equal("notes", edges[Edge.Bottom].Id);
    }

    [Fact]
    public void Clockwise_WrapsFromLeftToTop()
    {
        var edges = EdgeAssignment.Assign([Member("a", Edge.Left, 0), Member("b", Edge.Left, 1)]);

        Assert.Equal("a", edges[Edge.Left].Id);
        Assert.Equal("b", edges[Edge.Top].Id);
    }

    [Fact]
    public void FifthMember_HasNoEdge()
    {
        var edges = EdgeAssignment.Assign(
        [
            Member("a", Edge.Top, 0), Member("b", Edge.Top, 1), Member("c", Edge.Top, 2), Member("d", Edge.Top, 3), Member("e", Edge.Top, 4),
        ]);

        Assert.Equal(4, edges.Count);
        Assert.DoesNotContain(edges.Values, member => member.Id == "e");
    }

    [Fact]
    public void SameInstallTime_OrdersById_SoTheResultIsStable()
    {
        var edges = EdgeAssignment.Assign([Member("b", Edge.Top, 0), Member("a", Edge.Top, 0)]);

        Assert.Equal("a", edges[Edge.Top].Id);
        Assert.Equal("b", edges[Edge.Right].Id);
    }
}
