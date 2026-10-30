using System.Globalization;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Apps;

/// <summary>
/// What a typed, pasted or dropped text points to: a web address, a folder or a file/app.
/// </summary>
/// <param name="Kind">How the target is opened.</param>
/// <param name="Target">Normalized target (URL with scheme, path without quotes).</param>
/// <param name="SuggestedName">Label to propose for the card.</param>
public sealed record LaunchTarget(LaunchKind Kind, string Target, string SuggestedName)
{
    private const string AppsFolderPrefix = @"shell:AppsFolder\";

    /// <summary>
    /// Classifies <paramref name="text"/>; returns <see langword="null"/> when it is not a web address, a full
    /// path or an apps-folder item. <paramref name="isDirectory"/> tells whether a path is an existing folder.
    /// </summary>
    public static LaunchTarget? Classify(string text, Func<string, bool> isDirectory)
    {
        ArgumentNullException.ThrowIfNull(isDirectory);

        var value = (text ?? "").Trim().Trim('"').Trim();
        if (value.Length == 0)
        {
            return null;
        }

        if (value.StartsWith(AppsFolderPrefix, StringComparison.OrdinalIgnoreCase))
        {
            return new LaunchTarget(LaunchKind.Executable, value, value[AppsFolderPrefix.Length..]);
        }

        if (TryParseWebAddress(value) is { } url)
        {
            return new LaunchTarget(LaunchKind.Url, url.OriginalString, SiteName(url));
        }

        if (!Path.IsPathFullyQualified(value))
        {
            return null;
        }

        if (isDirectory(value))
        {
            var name = Path.GetFileName(Path.TrimEndingDirectorySeparator(value));
            return new LaunchTarget(LaunchKind.Folder, value, name.Length > 0 ? name : value);
        }

        return new LaunchTarget(LaunchKind.Executable, value, Capitalize(Path.GetFileNameWithoutExtension(value)));
    }

    private static Uri? TryParseWebAddress(string value)
    {
        var candidate = value.StartsWith("www.", StringComparison.OrdinalIgnoreCase) ? "https://" + value : value;
        return Uri.TryCreate(candidate, UriKind.Absolute, out var uri)
            && (uri.Scheme == Uri.UriSchemeHttps || uri.Scheme == Uri.UriSchemeHttp)
            && uri.Host.Contains('.', StringComparison.Ordinal)
                ? uri
                : null;
    }

    /// <summary>"www.youtube.com" → "Youtube", "docs.microsoft.com" → "Docs.microsoft".</summary>
    private static string SiteName(Uri url)
    {
        var host = url.Host.StartsWith("www.", StringComparison.OrdinalIgnoreCase) ? url.Host[4..] : url.Host;
        var lastDot = host.LastIndexOf('.');
        return Capitalize(lastDot > 0 ? host[..lastDot] : host);
    }

    private static string Capitalize(string text) =>
        text.Length == 0 ? text : char.ToUpper(text[0], CultureInfo.InvariantCulture) + text[1..];
}
