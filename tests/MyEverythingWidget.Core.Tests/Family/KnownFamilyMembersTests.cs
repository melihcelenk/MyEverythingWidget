using MyEverythingWidget.Core.Family;

namespace MyEverythingWidget.Core.Tests.Family;

public sealed class KnownFamilyMembersTests
{
    [Fact]
    public void TaskTimerWidget_IsOfferedWithItsStoreProduct()
    {
        var timer = Assert.Single(KnownFamilyMembers.All, known => known.Member.Id == "tasktimer");

        Assert.Equal("Task Timer Widget", timer.Member.DisplayName);
        Assert.Equal("9NF0N9LN349G", timer.StoreProductId);
    }

    [Fact]
    public void EveryKnownMember_HasAUniqueIdAndAStoreProduct()
    {
        Assert.Equal(KnownFamilyMembers.All.Count, KnownFamilyMembers.All.Select(known => known.Member.Id).Distinct().Count());
        Assert.All(KnownFamilyMembers.All, known => Assert.False(string.IsNullOrWhiteSpace(known.StoreProductId)));
    }
}
