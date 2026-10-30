using System.Globalization;
using System.Text.Json;
using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Legacy;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation;

/// <summary>What happened to the Python version's data on this start.</summary>
public enum MigrationOutcome
{
    /// <summary>This version already has its own data; nothing was imported.</summary>
    NotNeeded,

    /// <summary>There is no data of the Python version.</summary>
    NoLegacyData,

    /// <summary>The data was imported.</summary>
    Imported,

    /// <summary>The Python version's file could not be read; nothing was written.</summary>
    Failed,
}

/// <summary>Result of <see cref="LegacyMigrator.MigrateAsync"/>.</summary>
/// <param name="Outcome">What happened.</param>
/// <param name="ImportedItems">Cards created.</param>
/// <param name="MissingImages">Image notes whose file no longer exists.</param>
public sealed record MigrationResult(MigrationOutcome Outcome, int ImportedItems, int MissingImages)
{
    /// <summary>Gets the message for the status bar, or <see langword="null"/> when there is nothing to tell.</summary>
    public string? Message => Outcome switch
    {
        MigrationOutcome.Imported when MissingImages == 0 =>
            string.Create(CultureInfo.InvariantCulture, $"Imported {ImportedItems} items from the previous version of My Everything Widget."),
        MigrationOutcome.Imported =>
            string.Create(CultureInfo.InvariantCulture, $"Imported {ImportedItems} items from the previous version of My Everything Widget. {MissingImages} {(MissingImages == 1 ? "image" : "images")} could not be found."),
        MigrationOutcome.Failed => "Items of the previous version could not be read, so they were not imported.",
        _ => null,
    };
}

/// <summary>
/// Imports the Python version's data once, on the first start of this version: converts it, creates real icons for
/// app cards, copies images that still exist, and saves the result. Existing data of this version is never touched.
/// </summary>
public sealed class LegacyMigrator(IWidgetStateStore store, IIconStore icons, IImageStore images, Func<string> newId, GridSize gridSize)
{
    /// <summary>Imports from <paramref name="legacyPath"/> when this version has no data yet.</summary>
    public async Task<MigrationResult> MigrateAsync(string legacyPath, CancellationToken cancellationToken)
    {
        if (store.Load().State is not null)
        {
            return new MigrationResult(MigrationOutcome.NotNeeded, 0, 0);
        }

        if (!File.Exists(legacyPath))
        {
            return new MigrationResult(MigrationOutcome.NoLegacyData, 0, 0);
        }

        LegacyImport import;
        try
        {
            import = LegacyImporter.Build(LegacyStateReader.Parse(await File.ReadAllTextAsync(legacyPath, cancellationToken).ConfigureAwait(false)), newId, gridSize);
        }
        catch (Exception exception) when (exception is JsonException or IOException or UnauthorizedAccessException)
        {
            return new MigrationResult(MigrationOutcome.Failed, 0, 0);
        }

        var items = await WithIconsAsync(import, cancellationToken).ConfigureAwait(false);
        var missingImages = 0;
        foreach (var pending in import.Images)
        {
            if (await ImportImageAsync(pending, Path.GetDirectoryName(legacyPath)!, cancellationToken).ConfigureAwait(false) is { } image)
            {
                items.Add(image);
            }
            else
            {
                missingImages++;
            }
        }

        store.Save(import.State with { Items = items });
        return new MigrationResult(MigrationOutcome.Imported, items.Count, missingImages);
    }

    private async Task<List<WidgetItem>> WithIconsAsync(LegacyImport import, CancellationToken cancellationToken)
    {
        var iconTargets = import.AppsNeedingIcons.ToDictionary(pending => pending.ItemId, pending => pending.Target, StringComparer.Ordinal);
        var items = new List<WidgetItem>();
        foreach (var item in import.State.Items)
        {
            if (item is AppItem app && iconTargets.TryGetValue(app.Id, out var target))
            {
                items.Add(app with { IconPath = await icons.CreateIconAsync(target, cancellationToken).ConfigureAwait(false) });
            }
            else
            {
                items.Add(item);
            }
        }

        return items;
    }

    /// <summary>The Python version stored image paths relative to its working folder; they are tried next to its state file too.</summary>
    private async Task<ImageItem?> ImportImageAsync(PendingImage pending, string legacyDirectory, CancellationToken cancellationToken)
    {
        var candidates = Path.IsPathRooted(pending.SourcePath)
            ? [pending.SourcePath]
            : new[] { Path.Combine(legacyDirectory, pending.SourcePath), Path.GetFullPath(pending.SourcePath) };
        if (candidates.FirstOrDefault(File.Exists) is not { } source)
        {
            return null;
        }

        await using var stream = File.OpenRead(source);
        return await images.ImportAsync(stream, cancellationToken).ConfigureAwait(false) is { } stored
            ? new ImageItem(pending.ItemId, pending.CategoryId, pending.Placement, stored.RelativePath, stored.PixelWidth, stored.PixelHeight)
            : null;
    }
}
