using MyEverythingWidget.Core.Family;
using WidgetFamily;

namespace MyEverythingWidget.Presentation.Tests;

public sealed class FamilyMenuViewModelTests
{
    private static readonly PixelRect Icon = new(900, 500, 64, 64);

    private sealed class FakeCatalog : IFamilyCatalog
    {
        public List<InstalledMember> Members { get; } = [];

        public Task<IReadOnlyList<InstalledMember>> GetMembersAsync(CancellationToken cancellationToken) =>
            Task.FromResult<IReadOnlyList<InstalledMember>>(Members.ToList());
    }

    private sealed class FakeLauncher : IFamilyLauncher
    {
        public List<(FamilyMember Member, Edge Edge, PixelRect Anchor)> Opened { get; } = [];

        public Task<bool> OpenAsync(FamilyMember member, Edge edge, PixelRect anchor)
        {
            Opened.Add((member, edge, anchor));
            return Task.FromResult(true);
        }
    }

    private sealed class FakeHub : IFamilyHub
    {
        public List<(string MemberId, FamilyMessage Message)> Sent { get; } = [];

        public Task<bool> SendAsync(string memberId, FamilyMessage message)
        {
            Sent.Add((memberId, message));
            return Task.FromResult(true);
        }
    }

    private readonly FakeCatalog _catalog = new();
    private readonly FakeLauncher _launcher = new();
    private readonly FakeHub _hub = new();

    private static InstalledMember TaskTimer() =>
        new(new FamilyMember("tasktimer", "Task Timer Widget", "tasktimer-widget", Edge.Right), DateTimeOffset.UnixEpoch);

    [Fact]
    public async Task InstalledMember_AppearsOnItsEdge()
    {
        _catalog.Members.Add(TaskTimer());
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);

        await menu.RefreshAsync(TestContext.Current.CancellationToken);

        Assert.True(menu.HasMembers);
        Assert.Equal("Task Timer Widget", menu.Right?.Name);
        Assert.Null(menu.Top);
        Assert.Null(menu.Bottom);
        Assert.Null(menu.Left);
    }

    [Fact]
    public async Task NoMembers_ShowsNothing()
    {
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);

        await menu.RefreshAsync(TestContext.Current.CancellationToken);

        Assert.False(menu.HasMembers);
        Assert.Null(menu.Right);
    }

    [Fact]
    public async Task UninstalledMember_LeavesTheMenuOnTheNextRefresh()
    {
        _catalog.Members.Add(TaskTimer());
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);
        await menu.RefreshAsync(TestContext.Current.CancellationToken);

        _catalog.Members.Clear();
        await menu.RefreshAsync(TestContext.Current.CancellationToken);

        Assert.False(menu.HasMembers);
        Assert.Null(menu.Right);
    }

    [Fact]
    public async Task OpeningAnEdge_LaunchesItsMemberNextToTheIcon()
    {
        _catalog.Members.Add(TaskTimer());
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);
        await menu.RefreshAsync(TestContext.Current.CancellationToken);

        Assert.True(await menu.OpenAsync(Edge.Right, Icon));

        var opened = Assert.Single(_launcher.Opened);
        Assert.Equal("tasktimer", opened.Member.Id);
        Assert.Equal(Edge.Right, opened.Edge);
        Assert.Equal(Icon, opened.Anchor);
    }

    [Fact]
    public async Task OpeningAnEmptyEdge_DoesNothing()
    {
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);
        await menu.RefreshAsync(TestContext.Current.CancellationToken);

        Assert.False(await menu.OpenAsync(Edge.Top, Icon));
        Assert.Empty(_launcher.Opened);
    }

    [Fact]
    public async Task MovingTheIcon_MovesTheOpenedMemberWithIt()
    {
        _catalog.Members.Add(TaskTimer());
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);
        await menu.RefreshAsync(TestContext.Current.CancellationToken);
        await menu.OpenAsync(Edge.Right, Icon);
        var moved = Icon with { Left = 100, Top = 200 };

        await menu.FollowAsync(moved);

        var sent = Assert.Single(_hub.Sent);
        Assert.Equal("tasktimer", sent.MemberId);
        Assert.Equal(FamilyMessage.Place(Edge.Right, moved), sent.Message);
    }

    [Fact]
    public async Task MovingTheIcon_LeavesMembersThatWereNotOpenedFromIt()
    {
        _catalog.Members.Add(TaskTimer());
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);
        await menu.RefreshAsync(TestContext.Current.CancellationToken);

        await menu.FollowAsync(Icon);

        Assert.Empty(_hub.Sent);
    }

    [Fact]
    public async Task HidingAndShowingTheIcon_HidesAndShowsTheOpenedMembers()
    {
        _catalog.Members.Add(TaskTimer());
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);
        await menu.RefreshAsync(TestContext.Current.CancellationToken);
        await menu.OpenAsync(Edge.Right, Icon);

        await menu.SetHiddenAsync(hidden: true);
        await menu.SetHiddenAsync(hidden: false);

        Assert.Equal([MessageTypes.Hide, MessageTypes.Show], _hub.Sent.Select(sent => sent.Message.Type));
    }

    [Fact]
    public async Task UninstalledMember_IsNoLongerFollowed()
    {
        _catalog.Members.Add(TaskTimer());
        var menu = new FamilyMenuViewModel(_catalog, _launcher, _hub);
        await menu.RefreshAsync(TestContext.Current.CancellationToken);
        await menu.OpenAsync(Edge.Right, Icon);

        _catalog.Members.Clear();
        await menu.RefreshAsync(TestContext.Current.CancellationToken);
        await menu.FollowAsync(Icon);

        Assert.Empty(_hub.Sent);
    }
}
