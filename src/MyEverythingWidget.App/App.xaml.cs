using Microsoft.Extensions.Logging;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Legacy;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.Infrastructure.Shell;
using MyEverythingWidget.Presentation;

namespace MyEverythingWidget.App;

/// <summary>
/// Application object and composition root.
/// </summary>
public sealed partial class App : Application, IDisposable
{
    private readonly ILoggerFactory _loggerFactory;
    private readonly HttpClient _httpClient = new();
    private MainWindow? _mainWindow;
    private DispatcherQueue? _dispatcherQueue;

    /// <summary>Creates the application object.</summary>
    public App()
    {
        _loggerFactory = LoggerFactory.Create(builder => builder.AddDebug().SetMinimumLevel(LogLevel.Information));
        UnhandledException += OnUnhandledException;
        InitializeComponent();
    }

    /// <summary>
    /// Brings the main window to the front; called when a second launch is redirected to this instance.
    /// </summary>
    public static void BringMainWindowToFront()
    {
        if (Current is App app)
        {
            app._dispatcherQueue?.TryEnqueue(() => app._mainWindow?.BringToFront());
        }
    }

    /// <inheritdoc />
    public void Dispose()
    {
        _loggerFactory.Dispose();
        _httpClient.Dispose();
    }

    /// <inheritdoc />
    protected override async void OnLaunched(LaunchActivatedEventArgs args)
    {
        _dispatcherQueue = DispatcherQueue.GetForCurrentThread();

        var dataDirectory = AppDataLocation.Resolve();
        var settingsStore = new JsonSettingsStore(dataDirectory, TimeProvider.System, _loggerFactory.CreateLogger<JsonSettingsStore>());
        var stateStore = new JsonWidgetStateStore(dataDirectory, TimeProvider.System, _loggerFactory.CreateLogger<JsonWidgetStateStore>());

        var iconStore = new ShellIconStore(dataDirectory, new FaviconSource(_httpClient), _loggerFactory.CreateLogger<ShellIconStore>());
        var imageStore = new ImageStore(dataDirectory);
        var launcher = new ShellLauncher(_loggerFactory.CreateLogger<ShellLauncher>());

        // First start of this version: bring over the Python version's items.
        var migration = LegacyStatePath() is { } legacyPath
            ? await new LegacyMigrator(stateStore, iconStore, imageStore, NewId, GridSize.Default).MigrateAsync(legacyPath, CancellationToken.None)
            : null;

        var board = new WidgetBoard(stateStore, NewId, GridSize.Default, _loggerFactory.CreateLogger<WidgetBoard>());
        var boardViewModel = new BoardViewModel(board, iconStore, launcher, imageStore);
        if (migration is not null)
        {
            boardViewModel.ShowMigrationResult(migration);
        }

        _mainWindow = new MainWindow(new MainViewModel(settingsStore), boardViewModel, new ShellAppsSource());
        _mainWindow.Activate();
    }

    private static string NewId() => Guid.NewGuid().ToString("N");

    /// <summary>
    /// The Python version's state file; <c>MEW_LEGACY_STATE</c> overrides it. Test runs (<c>MEW_DATA_DIR</c> set)
    /// import only from an explicitly given file, so they never read the developer's real data.
    /// </summary>
    private static string? LegacyStatePath()
    {
        var overridePath = Environment.GetEnvironmentVariable("MEW_LEGACY_STATE");
        if (!string.IsNullOrWhiteSpace(overridePath))
        {
            return overridePath;
        }

        return Environment.GetEnvironmentVariable(AppDataLocation.OverrideVariable) is null ? LegacyStateReader.DefaultPath : null;
    }

    private static void OnUnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
    {
        // Last-chance record of a crash; the process is about to terminate, so write synchronously.
        CrashLog.Write(AppDataLocation.Resolve(), e.Exception);
    }
}
