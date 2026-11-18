namespace MyEverythingWidget.Core.Settings;

/// <summary>
/// Reads and writes <see cref="AppSettings"/>.
/// </summary>
public interface ISettingsStore
{
    /// <summary>
    /// Returns the stored settings, or <see cref="AppSettings.Default"/> when nothing usable is stored.
    /// </summary>
    AppSettings Load();

    /// <summary>
    /// Persists <paramref name="settings"/>, replacing what was stored before.
    /// </summary>
    void Save(AppSettings settings);
}
