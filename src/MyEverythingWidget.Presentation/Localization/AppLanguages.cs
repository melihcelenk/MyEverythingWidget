using System.Globalization;

namespace MyEverythingWidget.Presentation.Localization;

/// <summary>A language the app is translated into.</summary>
/// <param name="Code">Language code of its resources, such as <c>tr</c>.</param>
/// <param name="NativeName">Its name written in that language, as the language list shows it.</param>
public sealed record AppLanguage(string Code, string NativeName);

/// <summary>
/// The languages of the app and the choice between them: the user's choice when it is one of them, otherwise the
/// Windows display language when it is one of them, otherwise English.
/// </summary>
public static class AppLanguages
{
    /// <summary>The language used when neither the choice nor the Windows language is available.</summary>
    public const string Fallback = "en";

    /// <summary>Gets every language of the app, English first, the rest by their own names.</summary>
    public static IReadOnlyList<AppLanguage> Supported { get; } =
    [
        new("en", "English"),
        new("id", "Bahasa Indonesia"),
        new("de", "Deutsch"),
        new("es", "Español"),
        new("fil", "Filipino"),
        new("fr", "Français"),
        new("it", "Italiano"),
        new("pl", "Polski"),
        new("pt", "Português"),
        new("sv", "Svenska"),
        new("tr", "Türkçe"),
        new("ru", "Русский"),
        new("uk", "Українська"),
        new("hi", "हिन्दी"),
        new("ko", "한국어"),
    ];

    /// <summary>
    /// Returns the culture to show the app in: <paramref name="choice"/> when it is supported, otherwise
    /// <paramref name="system"/>'s language (or one of its parents) when supported, otherwise English.
    /// </summary>
    public static CultureInfo Resolve(string? choice, CultureInfo system)
    {
        ArgumentNullException.ThrowIfNull(system);

        if (Find(choice) is { } chosen)
        {
            return CultureInfo.GetCultureInfo(chosen.Code);
        }

        for (var culture = system; !string.IsNullOrEmpty(culture.Name); culture = culture.Parent)
        {
            if (Find(culture.Name) is { } language)
            {
                return CultureInfo.GetCultureInfo(language.Code);
            }
        }

        return CultureInfo.GetCultureInfo(Fallback);
    }

    private static AppLanguage? Find(string? code) =>
        string.IsNullOrEmpty(code)
            ? null
            : Supported.FirstOrDefault(language => string.Equals(language.Code, code, StringComparison.OrdinalIgnoreCase));
}
