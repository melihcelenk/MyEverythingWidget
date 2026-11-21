using System.Globalization;
using System.Reflection;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>
/// Guarantees that every language stays complete: all text shown by the app comes from the string resources, and
/// every resource has a translation in every supported language. Adding a feature with an untranslated or hard-coded
/// text fails one of these tests.
/// </summary>
public sealed partial class LocalizationCoverageTests
{
    private static readonly string RepoRoot = FindRepoRoot();
    private static readonly string ResourceFolder = Path.Combine(RepoRoot, "src", "MyEverythingWidget.Presentation", "Localization");

    /// <summary>Text that is the same in every language: names and the copyright year.</summary>
    private static readonly HashSet<string> LanguageNeutralText = ["2026", "Melih Çelenk", "melihcelenk.com"];

    /// <summary>Projects whose code may show text to the user.</summary>
    private static readonly string[] UiProjects = ["MyEverythingWidget.App", "MyEverythingWidget.Presentation"];

    private static string FindRepoRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "MyEverythingWidget.slnx")))
        {
            directory = directory.Parent;
        }

        return directory?.FullName ?? throw new InvalidOperationException("Repository root not found.");
    }

    private static Dictionary<string, string> ReadResx(string path) =>
        XDocument.Load(path).Root!.Elements("data").ToDictionary(
            data => (string)data.Attribute("name")!,
            data => (string?)data.Element("value") ?? "");

    private static Dictionary<string, string> English => ReadResx(Path.Combine(ResourceFolder, "Strings.resx"));

    public static TheoryData<string> Translations()
    {
        var data = new TheoryData<string>();
        foreach (var language in AppLanguages.Supported.Where(language => language.Code != "en"))
        {
            data.Add(language.Code);
        }

        return data;
    }

    [Theory]
    [MemberData(nameof(Translations))]
    public void EveryLanguage_HasEveryText_AndNothingElse(string code)
    {
        var path = Path.Combine(ResourceFolder, $"Strings.{code}.resx");
        Assert.True(File.Exists(path), $"Missing translation file {path}.");
        var translation = ReadResx(path);

        Assert.Empty(English.Keys.Except(translation.Keys));
        Assert.Empty(translation.Keys.Except(English.Keys));
        Assert.Empty(translation.Where(entry => string.IsNullOrWhiteSpace(entry.Value)).Select(entry => entry.Key));
    }

    [Theory]
    [MemberData(nameof(Translations))]
    public void EveryTranslation_KeepsThePlaceholders(string code)
    {
        var translation = ReadResx(Path.Combine(ResourceFolder, $"Strings.{code}.resx"));
        foreach (var (key, english) in English)
        {
            Assert.True(
                Placeholders(english).SequenceEqual(Placeholders(translation[key])),
                $"{code}: '{key}' has placeholders {string.Join(",", Placeholders(translation[key]))}, English has {string.Join(",", Placeholders(english))}.");
        }
    }

    [Fact]
    public void EveryResourceFile_IsASupportedLanguage()
    {
        var codes = AppLanguages.Supported.Select(language => language.Code).ToHashSet();
        var files = Directory.GetFiles(ResourceFolder, "Strings.*.resx").Select(file => Path.GetFileName(file).Split('.')[1]);

        Assert.All(files, code => Assert.Contains(code, codes));
    }

    [Theory]
    [MemberData(nameof(Translations))]
    public void EveryLanguage_IsBuiltIntoTheApp(string code)
    {
        var set = Strings.ResourceManager.GetResourceSet(CultureInfo.GetCultureInfo(code), createIfNotExists: true, tryParents: false);

        Assert.NotNull(set);
    }

    [Fact]
    public void EveryText_HasATypedAccessor_AndEveryAccessorHasAText()
    {
        var properties = typeof(Strings).GetProperties(BindingFlags.Public | BindingFlags.Static)
            .Where(property => property.PropertyType == typeof(string))
            .Select(property => property.Name)
            .ToHashSet();
        var formats = typeof(Strings).GetMethods(BindingFlags.Public | BindingFlags.Static)
            .Where(method => method.ReturnType == typeof(string) && !method.IsSpecialName && method.Name != nameof(Strings.Get))
            .Select(method => method.Name);
        var accessors = properties.Concat(formats).ToHashSet();

        Assert.Empty(English.Keys.Except(accessors));
        Assert.Empty(accessors.Except(English.Keys));
    }

    [Fact]
    public void EveryTextUsedInXaml_Exists()
    {
        var keys = English.Keys.ToHashSet();
        var used = XamlFiles()
            .SelectMany(file => LocalizedKey().Matches(File.ReadAllText(file)).Select(match => (file, key: match.Groups["key"].Value)));

        Assert.Empty(used.Where(use => !keys.Contains(use.key)).Select(use => $"{Path.GetFileName(use.file)}: {use.key}"));
    }

    [Fact]
    public void Xaml_HasNoHardCodedText()
    {
        var found = XamlFiles()
            .SelectMany(file => File.ReadAllLines(file).Select((line, index) => (file, line, number: index + 1)))
            .SelectMany(entry => XamlTextAttribute().Matches(entry.line)
                .Select(match => match.Groups["value"].Value)
                .Where(value => !value.StartsWith('{') && HasLetter(CharacterReference().Replace(value, "")) && !LanguageNeutralText.Contains(value))
                .Select(value => $"{Path.GetFileName(entry.file)}:{entry.number} \"{value}\""))
            .ToList();

        Assert.Empty(found);
    }

    [Fact]
    public void Code_HasNoHardCodedText()
    {
        var found = CodeFiles()
            .SelectMany(file => File.ReadAllLines(file).Select((line, index) => (file, line, number: index + 1)))
            .Where(entry => !entry.line.TrimStart().StartsWith("//", StringComparison.Ordinal))
            .Where(entry => CodeText().Matches(entry.line).Any(match => HasLetter(match.Groups["value"].Value)))
            .Select(entry => $"{Path.GetFileName(entry.file)}:{entry.number} {entry.line.Trim()}")
            .ToList();

        Assert.Empty(found);
    }

    private static IEnumerable<string> XamlFiles() =>
        Directory.GetFiles(Path.Combine(RepoRoot, "src", "MyEverythingWidget.App"), "*.xaml", SearchOption.AllDirectories)
            .Where(file => !file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}", StringComparison.Ordinal)
                && !file.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}", StringComparison.Ordinal));

    private static IEnumerable<string> CodeFiles() =>
        UiProjects
            .SelectMany(project => Directory.GetFiles(Path.Combine(RepoRoot, "src", project), "*.cs", SearchOption.AllDirectories))
            .Where(file => !file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}", StringComparison.Ordinal)
                && !file.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}", StringComparison.Ordinal));

    private static bool HasLetter(string value) => value.Any(char.IsLetter);

    private static List<string> Placeholders(string text) =>
        Placeholder().Matches(text).Select(match => match.Value).Order(StringComparer.Ordinal).ToList();

    /// <summary>An XML character reference such as <c>&amp;#x2709;</c> (an emoji or symbol, not words).</summary>
    [GeneratedRegex(@"&#x?[0-9A-Fa-f]+;")]
    private static partial Regex CharacterReference();

    [GeneratedRegex(@"\{\d+\}")]
    private static partial Regex Placeholder();

    [GeneratedRegex(@"\{l:Str\s+(Key=)?(?<key>\w+)\}")]
    private static partial Regex LocalizedKey();

    [GeneratedRegex(@"(?<![\w.:])(Text|Content|Header|PlaceholderText|ToolTipService\.ToolTip|AutomationProperties\.Name|AutomationProperties\.HelpText|Title|PrimaryButtonText|SecondaryButtonText|CloseButtonText|OnContent|OffContent|Label|Description)=""(?<value>[^""]*)""")]
    private static partial Regex XamlTextAttribute();

    /// <summary>
    /// A string literal assigned to a property that shows text, passed to a method that shows it, or kept in a constant
    /// named like a message.
    /// </summary>
    [GeneratedRegex(@"(\b(Text|Content|Title|Caption|Header|PlaceholderText|\w*ButtonText|Message)\s*=\s*\$?""(?<value>[^""]*)""|\b(SetName|SetToolTip|SetHelpText)\([^,]+,\s*\$?""(?<value>[^""]*)""|\b(ShowStatus|ShowNotice|ShowAsync)\((\$?""(?<value>[^""]*)""|[^,""]+,\s*\$?""(?<value>[^""]*)"")|\bconst string \w*(Message|Text|Title)\s*=\s*""(?<value>[^""]*)"")")]
    private static partial Regex CodeText();
}
