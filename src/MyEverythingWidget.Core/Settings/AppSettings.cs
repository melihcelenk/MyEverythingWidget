using MyEverythingWidget.Core.Geometry;

namespace MyEverythingWidget.Core.Settings;

/// <summary>
/// User preferences that survive restarts.
/// </summary>
/// <param name="IsAlwaysOnTop">Whether the widget window stays above other windows.</param>
/// <param name="WindowBounds">Last window bounds in physical pixels; <see langword="null"/> before the first close.</param>
public sealed record AppSettings(bool IsAlwaysOnTop, PixelRect? WindowBounds)
{
    /// <summary>Gets the settings used on first run or when the stored file cannot be read.</summary>
    public static AppSettings Default { get; } = new(IsAlwaysOnTop: false, WindowBounds: null);

    /// <summary>Gets the colour theme; <see cref="AppTheme.System"/> follows the Windows setting.</summary>
    public AppTheme Theme { get; init; } = AppTheme.System;
}

/// <summary>Colour theme of the widget.</summary>
public enum AppTheme
{
    /// <summary>Follow the Windows light/dark setting.</summary>
    System,

    /// <summary>Always light.</summary>
    Light,

    /// <summary>Always dark.</summary>
    Dark,
}
