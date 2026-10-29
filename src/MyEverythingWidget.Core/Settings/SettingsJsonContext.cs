using System.Text.Json.Serialization;

namespace MyEverythingWidget.Core.Settings;

/// <summary>
/// Source-generated JSON metadata for the settings file.
/// </summary>
[JsonSourceGenerationOptions(
    PropertyNamingPolicy = JsonKnownNamingPolicy.CamelCase,
    WriteIndented = true)]
[JsonSerializable(typeof(AppSettings))]
internal sealed partial class SettingsJsonContext : JsonSerializerContext;
