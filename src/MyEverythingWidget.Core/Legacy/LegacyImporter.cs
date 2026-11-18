using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Legacy;

/// <summary>An imported app card whose icon still has to be created.</summary>
public sealed record PendingIcon(string ItemId, LaunchTarget Target);

/// <summary>An imported image whose file still has to be copied; its cells are already reserved.</summary>
public sealed record PendingImage(string ItemId, string CategoryId, GridPlacement Placement, string SourcePath);

/// <summary>The converted state plus the icon and image work left for Windows services.</summary>
public sealed record LegacyImport(WidgetState State, IReadOnlyList<PendingIcon> AppsNeedingIcons, IReadOnlyList<PendingImage> Images);

/// <summary>
/// Converts the Python version's data into a <see cref="WidgetState"/>. Items keep their cells when those are valid
/// and free; the rest go to the first free cells of their category. Emoji icons are dropped (real icons are created
/// afterwards); link and file notes become app cards.
/// </summary>
public static class LegacyImporter
{
    /// <summary>Builds the new state from <paramref name="data"/>.</summary>
    public static LegacyImport Build(LegacyData data, Func<string> newId, GridSize gridSize)
    {
        ArgumentNullException.ThrowIfNull(data);
        ArgumentNullException.ThrowIfNull(newId);

        var categories = data.Categories.Distinct(StringComparer.Ordinal).Select(name => new Category(newId(), name)).ToList();
        if (categories.Count == 0)
        {
            categories.Add(new Category(newId(), WidgetState.DefaultCategoryName));
        }

        var categoryIdByName = categories.ToDictionary(category => category.Name, category => category.Id, StringComparer.Ordinal);
        string CategoryId(string name) => categoryIdByName.TryGetValue(name, out var id) ? id : categories[0].Id;

        var candidates = Candidates(data, newId, CategoryId);
        var placements = Place(candidates, gridSize);

        var items = new List<WidgetItem>();
        var icons = new List<PendingIcon>();
        var images = new List<PendingImage>();
        foreach (var candidate in candidates)
        {
            var placement = placements[candidate.Id];
            switch (candidate.Source)
            {
                case LegacyApp app:
                    var appTarget = LaunchTarget.NormalizeTarget(app.Kind, app.Target);
                    items.Add(new AppItem(candidate.Id, candidate.CategoryId, placement, app.Name, appTarget, app.Kind, null));
                    icons.Add(new PendingIcon(candidate.Id, new LaunchTarget(app.Kind, appTarget, app.Name)));
                    break;
                case LegacyNote { Kind: LegacyNoteKind.Image } image:
                    images.Add(new PendingImage(candidate.Id, candidate.CategoryId, placement, image.Content));
                    break;
                case LegacyNote { Kind: LegacyNoteKind.Link or LegacyNoteKind.File } link:
                    var kind = link.Kind == LegacyNoteKind.Link ? LaunchKind.Url : LaunchKind.Executable;
                    var target = LaunchTarget.NormalizeTarget(kind, link.Content);
                    items.Add(new AppItem(candidate.Id, candidate.CategoryId, placement, NameOf(kind, target), target, kind, null));
                    icons.Add(new PendingIcon(candidate.Id, new LaunchTarget(kind, target, NameOf(kind, target))));
                    break;
                case LegacyNote note:
                    items.Add(new NoteItem(candidate.Id, candidate.CategoryId, placement, note.Content.Trim()));
                    break;
            }
        }

        return new LegacyImport(new WidgetState(WidgetState.CurrentSchemaVersion, categories, items), icons, images);
    }

    private sealed record Candidate(string Id, string CategoryId, GridSpan Span, GridPlacement? Wanted, object Source);

    private static List<Candidate> Candidates(LegacyData data, Func<string> newId, Func<string, string> categoryId)
    {
        var candidates = data.Apps
            .Select(app => new Candidate(newId(), categoryId(app.CategoryName), GridSpan.One, app.Placement, app))
            .ToList();
        candidates.AddRange(data.Notes.Select(note =>
        {
            var span = note.Kind switch
            {
                LegacyNoteKind.Text or LegacyNoteKind.Image => Clamp(note.Placement?.Span ?? DefaultSpans.For(ItemKind.Note)),
                _ => GridSpan.One,
            };
            return new Candidate(newId(), categoryId(note.CategoryName), span, note.Placement, note);
        }));
        return candidates;
    }

    /// <summary>First pass: every item whose own cells are valid and free keeps them. Second pass: the rest take the first free cells.</summary>
    private static Dictionary<string, GridPlacement> Place(List<Candidate> candidates, GridSize gridSize)
    {
        var layouts = new Dictionary<string, GridLayout>(StringComparer.Ordinal);
        GridLayout LayoutOf(string categoryId) =>
            layouts.TryGetValue(categoryId, out var layout) ? layout : layouts[categoryId] = GridLayout.Empty(gridSize);

        var homeless = new List<Candidate>();
        foreach (var candidate in candidates)
        {
            var layout = LayoutOf(candidate.CategoryId);
            if (candidate.Wanted is { } wanted && TryPlaceAt(layout, candidate.Id, wanted with { Span = candidate.Span }) is { } placed)
            {
                layouts[candidate.CategoryId] = placed;
            }
            else
            {
                homeless.Add(candidate);
            }
        }

        foreach (var candidate in homeless)
        {
            var result = LayoutOf(candidate.CategoryId).Add(candidate.Id, candidate.Span);
            if (!result.Succeeded)
            {
                result = LayoutOf(candidate.CategoryId).Add(candidate.Id, GridSpan.One);
            }

            if (result.Succeeded)
            {
                layouts[candidate.CategoryId] = result.Layout;
            }
        }

        var placements = layouts.Values.SelectMany(layout => layout.Items).ToDictionary(pair => pair.Key, pair => pair.Value, StringComparer.Ordinal);
        candidates.RemoveAll(candidate => !placements.ContainsKey(candidate.Id));
        return placements;
    }

    private static GridLayout? TryPlaceAt(GridLayout layout, string id, GridPlacement placement)
    {
        var items = new Dictionary<string, GridPlacement>(layout.Items, StringComparer.Ordinal) { [id] = placement };
        try
        {
            return new GridLayout(layout.Size, items);
        }
        catch (ArgumentException)
        {
            return null;
        }
    }

    private static GridSpan Clamp(GridSpan span) => new(
        Math.Clamp(span.Columns, GridSpan.Min, GridSpan.Max),
        Math.Clamp(span.Rows, GridSpan.Min, GridSpan.Max));

    private static string NameOf(LaunchKind kind, string target) =>
        LaunchTarget.Classify(target, _ => kind == LaunchKind.Folder)?.SuggestedName ?? target;
}
