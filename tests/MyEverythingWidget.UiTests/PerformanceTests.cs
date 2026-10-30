using System.Diagnostics;
using System.Globalization;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.UiTests.Infrastructure;

namespace MyEverythingWidget.UiTests;

/// <summary>
/// Start time and idle memory with a typical grid (MEW-4 Faz 8). The limits are loose regression guards; the measured
/// values are written to <c>results\shots\performance.txt</c> and recorded in PHASE8.md.
/// </summary>
public sealed class PerformanceTests : IDisposable
{
    private static readonly TimeSpan MaxStartTime = TimeSpan.FromSeconds(5);
    private const long MaxPrivateBytes = 250L * 1024 * 1024;

    private readonly AppDataFolder _data = new();

    public void Dispose() => _data.Dispose();

    [Fact]
    public void StartTimeAndIdleMemory_StayWithinLimits()
    {
        var items = new Dictionary<string, GridPlacement>();
        for (var index = 0; index < 10; index++)
        {
            items[$"A{index}"] = new GridPlacement(index / 5, index % 5, 1, 1);
        }

        items["N1"] = new GridPlacement(2, 0, 2, 1);
        items["N2"] = new GridPlacement(2, 2, 3, 2);
        StateFiles.Seed(_data, items);

        var stopwatch = Stopwatch.StartNew();
        using var app = AppSession.Launch(_data);
        stopwatch.Stop();

        Thread.Sleep(TimeSpan.FromSeconds(5));
        using var process = Process.GetProcessById(app.ProcessId);
        process.Refresh();
        var report = string.Create(
            CultureInfo.InvariantCulture,
            $"start_ms={stopwatch.ElapsedMilliseconds} working_set_mb={process.WorkingSet64 / (1024 * 1024)} private_mb={process.PrivateMemorySize64 / (1024 * 1024)}");
        File.WriteAllText(Artifacts.PathOf("performance").Replace(".png", ".txt", StringComparison.Ordinal), report);

        Assert.True(stopwatch.Elapsed < MaxStartTime, report);
        Assert.True(process.PrivateMemorySize64 < MaxPrivateBytes, report);
    }
}
