using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation.Tests;

internal sealed class InMemoryWidgetStateStore(WidgetState? initial) : IWidgetStateStore
{
    public WidgetState? Current { get; private set; } = initial;

    public int SaveCount { get; private set; }

    public string? CorruptBackupPath { get; init; }

    public Exception? FailNextSaveWith { get; set; }

    public StateLoadResult Load() => new(Current, CorruptBackupPath);

    public void Save(WidgetState state)
    {
        if (FailNextSaveWith is { } failure)
        {
            FailNextSaveWith = null;
            throw failure;
        }

        Current = state;
        SaveCount++;
    }
}
