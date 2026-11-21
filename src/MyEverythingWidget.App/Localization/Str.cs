using Microsoft.UI.Xaml.Markup;
using MyEverythingWidget.Presentation.Localization;

namespace MyEverythingWidget.App.Localization;

/// <summary>
/// A text from the string resources in XAML: <c>Text="{l:Str Key=AddNote}"</c>. The text is read in the app's
/// language when the element is created.
/// </summary>
[MarkupExtensionReturnType(ReturnType = typeof(string))]
public sealed partial class Str : MarkupExtension
{
    /// <summary>Gets or sets the name of the text in <c>Strings.resx</c>.</summary>
    public string Key { get; set; } = "";

    /// <inheritdoc />
    protected override object ProvideValue() => Strings.Get(Key);
}
