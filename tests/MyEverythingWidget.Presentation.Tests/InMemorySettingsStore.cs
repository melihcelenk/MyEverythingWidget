using MyEverythingWidget.Core.Settings;

namespace MyEverythingWidget.Presentation.Tests;

internal sealed class InMemorySettingsStore(AppSettings initial) : ISettingsStore
{
    public AppSettings Current { get; private set; } = initial;

    public int SaveCount { get; private set; }

    public AppSettings Load() => Current;

    public void Save(AppSettings settings)
    {
        Current = settings;
        SaveCount++;
    }
}
