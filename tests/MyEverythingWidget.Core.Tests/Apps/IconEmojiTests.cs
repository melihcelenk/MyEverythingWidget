using MyEverythingWidget.Core.Apps;

namespace MyEverythingWidget.Core.Tests.Apps;

/// <summary>What the user types as an emoji icon is reduced to one symbol.</summary>
public sealed class IconEmojiTests
{
    [Theory]
    [InlineData("🚀", "🚀")]
    [InlineData("  🚀  ", "🚀")]
    [InlineData("🚀🔥", "🚀")]
    [InlineData("👍🏽", "👍🏽")]
    [InlineData("👨‍👩‍👧", "👨‍👩‍👧")]
    [InlineData("★", "★")]
    [InlineData("A", "A")]
    public void Normalize_KeepsFirstSymbol(string typed, string expected)
    {
        Assert.Equal(expected, IconEmoji.Normalize(typed));
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public void Normalize_Blank_IsNull(string? typed)
    {
        Assert.Null(IconEmoji.Normalize(typed));
    }
}
