using WidgetFamily;

namespace MyEverythingWidget.Core.Family;

/// <summary>A family widget the hub offers for download when it is not installed.</summary>
/// <param name="Member">The member as it declares itself once installed.</param>
/// <param name="StoreProductId">Its Microsoft Store product id.</param>
public sealed record KnownFamilyMember(FamilyMember Member, string StoreProductId);

/// <summary>
/// The published widgets of the family. The menu offers each one that is not installed with a link to its Store page;
/// a newly published family widget is added here.
/// </summary>
public static class KnownFamilyMembers
{
    /// <summary>All published family widgets.</summary>
    public static IReadOnlyList<KnownFamilyMember> All { get; } =
    [
        new(new FamilyMember("tasktimer", "Task Timer Widget", "tasktimer-widget", Edge.Right), "9NF0N9LN349G"),
    ];
}
