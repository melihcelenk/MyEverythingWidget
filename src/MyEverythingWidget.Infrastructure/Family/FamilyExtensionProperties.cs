namespace MyEverythingWidget.Infrastructure.Family;

/// <summary>
/// Turns an app extension's properties into strings. Each element under <c>uap3:Properties</c> arrives as a nested
/// property set with its text under <c>#text</c>; a plain string value is taken as it is.
/// </summary>
public static class FamilyExtensionProperties
{
    private const string TextKey = "#text";

    /// <summary>Reads the text of every property that has one.</summary>
    /// <param name="properties">The extension's property set.</param>
    /// <returns>The property texts by name.</returns>
    public static IReadOnlyDictionary<string, string> ToStrings(IEnumerable<KeyValuePair<string, object>> properties)
    {
        ArgumentNullException.ThrowIfNull(properties);
        var strings = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var (name, value) in properties)
        {
            var text = value switch
            {
                string plain => plain,
                IDictionary<string, object> element when element.TryGetValue(TextKey, out var inner) => inner as string,
                _ => null,
            };
            if (text is not null)
            {
                strings[name] = text;
            }
        }

        return strings;
    }
}
