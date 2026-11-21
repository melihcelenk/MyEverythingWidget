using System.Globalization;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.Presentation.Tests;

public sealed class AppLanguagesTests
{
    private static CultureInfo Culture(string name) => CultureInfo.GetCultureInfo(name);

    [Fact]
    public void Supported_AreEnglishAndTheFourteenTranslations()
    {
        string[] expected = ["en", "tr", "uk", "pl", "de", "es", "hi", "fil", "fr", "pt", "id", "it", "ru", "ko", "sv"];

        Assert.Equal(expected.Order(), AppLanguages.Supported.Select(language => language.Code).Order());
        Assert.Equal("en", AppLanguages.Supported[0].Code);
    }

    [Fact]
    public void EveryLanguage_IsListedUnderItsOwnName()
    {
        Assert.All(AppLanguages.Supported, language => Assert.False(string.IsNullOrWhiteSpace(language.NativeName)));
        Assert.Equal("Türkçe", AppLanguages.Supported.Single(language => language.Code == "tr").NativeName);
        Assert.Equal("Deutsch", AppLanguages.Supported.Single(language => language.Code == "de").NativeName);
    }

    [Theory]
    [InlineData("tr-TR", "tr")]
    [InlineData("pt-BR", "pt")]
    [InlineData("pt-PT", "pt")]
    [InlineData("fil-PH", "fil")]
    [InlineData("sv-FI", "sv")]
    [InlineData("en-GB", "en")]
    [InlineData("de-CH", "de")]
    [InlineData("uk-UA", "uk")]
    public void SystemLanguage_IsUsedWhenItIsOneOfOurs(string system, string expected)
    {
        Assert.Equal(expected, AppLanguages.Resolve(choice: null, Culture(system)).Name);
    }

    [Theory]
    [InlineData("ja-JP")]
    [InlineData("zh-CN")]
    [InlineData("ar-SA")]
    [InlineData("")]
    public void SystemLanguageWeDoNotHave_FallsBackToEnglish(string system)
    {
        Assert.Equal("en", AppLanguages.Resolve(choice: null, Culture(system)).Name);
    }

    [Fact]
    public void ChosenLanguage_WinsOverTheSystemLanguage()
    {
        Assert.Equal("de", AppLanguages.Resolve("de", Culture("tr-TR")).Name);
    }

    [Fact]
    public void UnknownSavedChoice_FollowsTheSystemLanguage()
    {
        Assert.Equal("tr", AppLanguages.Resolve("xx", Culture("tr-TR")).Name);
    }

    [Fact]
    public void Language_DefaultsToSystem_AndAChoiceIsSaved()
    {
        var store = new InMemorySettingsStore(AppSettings.Default);
        var viewModel = new MainViewModel(store);
        Assert.Null(viewModel.Language);

        Assert.True(viewModel.SetLanguage("tr"));

        Assert.Equal("tr", store.Current.Language);
        Assert.Equal("tr", viewModel.Language);
        Assert.False(viewModel.SetLanguage("tr"), "Choosing the same language again changes nothing.");
        Assert.True(viewModel.SetLanguage(null), "Going back to the system language is a change.");
        Assert.Null(store.Current.Language);
    }
}
