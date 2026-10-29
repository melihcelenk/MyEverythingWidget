namespace MyEverythingWidget.Core.State;

/// <summary>
/// Result of reading the stored state.
/// </summary>
/// <param name="State">The stored state, or <see langword="null"/> when none is stored or it could not be read.</param>
/// <param name="CorruptBackupPath">Where an unreadable file was moved to, so the user can be told; otherwise <see langword="null"/>.</param>
public sealed record StateLoadResult(WidgetState? State, string? CorruptBackupPath);

/// <summary>
/// Reads and writes <see cref="WidgetState"/>.
/// </summary>
public interface IWidgetStateStore
{
    /// <summary>Reads the stored state.</summary>
    StateLoadResult Load();

    /// <summary>Persists <paramref name="state"/>; throws <see cref="IOException"/> or <see cref="UnauthorizedAccessException"/> when the file cannot be written.</summary>
    void Save(WidgetState state);
}
