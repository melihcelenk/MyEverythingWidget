using MyEverythingWidget.Infrastructure.Family;
using Windows.Foundation.Collections;
using WidgetFamily;

namespace MyEverythingWidget.Infrastructure.Tests;

/// <summary>
/// App extension properties arrive as a property set: an element such as <c>&lt;Protocol&gt;x&lt;/Protocol&gt;</c>
/// becomes a nested property set whose text is under <c>#text</c>.
/// </summary>
public sealed class FamilyExtensionPropertiesTests
{
    private static PropertySet Text(string value) => new() { ["#text"] = value };

    [Fact]
    public void ElementText_IsRead()
    {
        var properties = new PropertySet
        {
            [FamilyContract.ProtocolProperty] = Text("tasktimer-widget"),
            [FamilyContract.PreferredEdgeProperty] = Text("Right"),
        };

        var strings = FamilyExtensionProperties.ToStrings(properties);

        Assert.Equal("tasktimer-widget", strings[FamilyContract.ProtocolProperty]);
        Assert.Equal("Right", strings[FamilyContract.PreferredEdgeProperty]);
    }

    [Fact]
    public void PlainStringValue_IsRead()
    {
        var properties = new PropertySet { [FamilyContract.ProtocolProperty] = "tasktimer-widget" };

        Assert.Equal("tasktimer-widget", FamilyExtensionProperties.ToStrings(properties)[FamilyContract.ProtocolProperty]);
    }

    [Fact]
    public void ElementWithoutText_IsLeftOut()
    {
        var properties = new PropertySet { ["Empty"] = new PropertySet() };

        Assert.Empty(FamilyExtensionProperties.ToStrings(properties));
    }

    [Fact]
    public void ReadProperties_MakeAMember()
    {
        var properties = new PropertySet { [FamilyContract.ProtocolProperty] = Text("tasktimer-widget") };

        Assert.True(FamilyMember.TryRead("tasktimer", "Task Timer Widget", FamilyExtensionProperties.ToStrings(properties), out var member));
        Assert.Equal(Edge.Right, member!.PreferredEdge);
    }
}
