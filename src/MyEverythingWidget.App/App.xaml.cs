using Microsoft.Extensions.Logging;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using MyEverythingWidget.Core.Grid;
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
    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        _dispatcherQueue = DispatcherQueue.GetForCurrentThread();

        var dataDirectory = AppDataLocation.Resolve();
        var settingsStore = new JsonSettingsStore(dataDirectory, TimeProvider.System, _loggerFactory.CreateLogger<JsonSettingsStore>());
        var stateStore = new JsonWidgetStateStore(dataDirectory, TimeProvider.System, _loggerFactory.CreateLogger<JsonWidgetStateStore>());
        var board = new WidgetBoard(stateStore, () => Guid.NewGuid().ToString("N"), GridSize.Default, _loggerFactory.CreateLogger<WidgetBoard>());

        var iconStore = new ShellIconStore(dataDirectory, new FaviconSource(_httpClient), _loggerFactory.CreateLogger<ShellIconStore>());
        var launcher = new ShellLauncher(_loggerFactory.CreateLogger<ShellLauncher>());

        _mainWindow = new MainWindow(
            new MainViewModel(settingsStore),
            new BoardViewModel(board, iconStore, launcher),
            new ShellAppsSource());
        _mainWindow.Activate();
    }

    private static void OnUnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
    {
        // Last-chance record of a crash; the process is about to terminate, so write synchronously.
        CrashLog.Write(AppDataLocation.Resolve(), e.Exception);
    }
}
