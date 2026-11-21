using System.Globalization;
using System.Runtime.CompilerServices;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.Presentation.Tests;

/// <summary>The tests compare messages with their English text, whatever the language of the machine running them.</summary>
internal static class EnglishTexts
{
    [ModuleInitializer]
    internal static void Use() => Strings.Culture = CultureInfo.InvariantCulture;
}
