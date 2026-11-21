using System.Globalization;
using Microsoft.Extensions.Logging;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Legacy;
using MyEverythingWidget.Core.Settings;
using MyEverythingWidget.Core.State;
using MyEverythingWidget.Infrastructure.Shell;
using MyEverythingWidget.Presentation;
using MyEverythingWidget.Presentation.Localization;

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

        var mainViewModel = new MainViewModel(settingsStore);
        UseLanguage(mainViewModel.Language);
        var board = new WidgetBoard(stateStore, NewId, mainViewModel.SavedGridSize, _loggerFactory.CreateLogger<WidgetBoard>(), Strings.DefaultCategoryName);
        var boardViewModel = new BoardViewModel(board, iconStore, launcher, imageStore);
        if (migration is not null)
        {
            boardViewModel.ShowMigrationResult(migration);
        }

        _mainWindow = new MainWindow(mainViewModel, boardViewModel, new ShellAppsSource());
        _mainWindow.RestartRequested += (_, _) => _dispatcherQueue?.TryEnqueue(DispatcherQueuePriority.Low, Restart);
        _mainWindow.Activate();
    }

    /// <summary>
    /// Shows the app in <paramref name="choice"/> (a language code), or in the Windows display language when that is
    /// <see langword="null"/> or not one of the app's languages, falling back to English. WinUI's own texts (such as
    /// the text box menu) follow the same language.
    /// </summary>
    private static void UseLanguage(string? choice)
    {
        var system = Environment.GetEnvironmentVariable(SystemLanguageVariable) is { Length: > 0 } tested
            ? CultureInfo.GetCultureInfo(tested)
            : CultureInfo.CurrentUICulture;
        var culture = AppLanguages.Resolve(choice, system);
        CultureInfo.DefaultThreadCurrentUICulture = culture;
        CultureInfo.CurrentUICulture = culture;
        Strings.Culture = culture;
        try
        {
            Microsoft.Windows.Globalization.ApplicationLanguages.PrimaryLanguageOverride = culture.Name;
        }
        catch (Exception exception) when (exception is InvalidOperationException or System.Runtime.InteropServices.COMException)
        {
            // Without package identity Windows may refuse the override; the app's own texts are already in the language.
        }
    }

    /// <summary>Restarts the app, so every text is created again in the newly chosen language.</summary>
    private void Restart()
    {
        _mainWindow?.SaveWindowBounds();
        var arguments = AppDataLocation.Override() is { } dataDirectory ? $"\"{AppDataLocation.OverrideArgument}{dataDirectory}\"" : "";
        Microsoft.Windows.AppLifecycle.AppInstance.Restart(arguments);
    }

    /// <summary>Environment variable that stands in for the Windows display language; used by UI tests.</summary>
    private const string SystemLanguageVariable = "MEW_SYSTEM_LANGUAGE";

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

        return AppDataLocation.Override() is null ? LegacyStateReader.DefaultPath : null;
    }

    private static void OnUnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
    {
        // Last-chance record of a crash; the process is about to terminate, so write synchronously.
        CrashLog.Write(AppDataLocation.Resolve(), e.Exception);
    }
}
