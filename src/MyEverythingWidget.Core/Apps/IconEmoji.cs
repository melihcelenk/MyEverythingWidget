using System.Globalization;

namespace MyEverythingWidget.Core.Apps;

/// <summary>
/// The emoji (or any single symbol) an app card can show instead of its icon.
/// </summary>
public static class IconEmoji
{
    /// <summary>
    /// Returns the first symbol of <paramref name="text"/> (a whole emoji, including skin tones and joined
    /// sequences), or <see langword="null"/> when it is blank.
    /// </summary>
    public static string? Normalize(string? text)
    {
        var trimmed = text?.Trim();
        return string.IsNullOrEmpty(trimmed) ? null : StringInfo.GetNextTextElement(trimmed);
    }
}
