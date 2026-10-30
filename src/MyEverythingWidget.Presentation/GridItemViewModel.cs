using CommunityToolkit.Mvvm.ComponentModel;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Presentation;

/// <summary>
/// One card on the grid. Instances are kept while their item exists, and their position properties change
/// in place, so the view can animate a move instead of recreating the card.
/// </summary>
public sealed partial class GridItemViewModel : ObservableObject
{
    [ObservableProperty]
    public partial int Row { get; set; }

    [ObservableProperty]
    public partial int Column { get; set; }

    [ObservableProperty]
    public partial int ColumnSpan { get; set; }

    [ObservableProperty]
    public partial int RowSpan { get; set; }

    [ObservableProperty]
    public partial string Title { get; set; } = "";

    [ObservableProperty]
    public partial string? Text { get; set; }

    [ObservableProperty]
    public partial string? ImagePath { get; set; }

    [ObservableProperty]
    public partial string? IconPath { get; set; }

    [ObservableProperty]
    public partial string? Emoji { get; set; }

    /// <summary>Creates the view model of <paramref name="item"/>.</summary>
    public GridItemViewModel(WidgetItem item)
    {
        ArgumentNullException.ThrowIfNull(item);

        Id = item.Id;
        Kind = item.Kind;
        Update(item);
    }

    /// <summary>Gets the id of the item.</summary>
    public string Id { get; }

    /// <summary>Gets the kind of the item.</summary>
    public ItemKind Kind { get; }

    /// <summary>Gets the current placement.</summary>
    public GridPlacement Placement => new(Row, Column, ColumnSpan, RowSpan);

    /// <summary>Copies position and content from <paramref name="item"/>.</summary>
    public void Update(WidgetItem item)
    {
        ArgumentNullException.ThrowIfNull(item);

        Row = item.Placement.Anchor.Row;
        Column = item.Placement.Anchor.Column;
        ColumnSpan = item.Placement.Span.Columns;
        RowSpan = item.Placement.Span.Rows;

        switch (item)
        {
            case AppItem app:
                Title = app.Name;
                IconPath = app.IconPath;
                Emoji = app.Emoji;
                break;
            case NoteItem note:
                Title = FirstLine(note.Text);
                Text = note.Text;
                break;
            case ImageItem image:
                Title = Path.GetFileName(image.ImagePath);
                ImagePath = image.ImagePath;
                break;
        }
    }

    private static string FirstLine(string text)
    {
        var end = text.IndexOfAny(['\r', '\n']);
        return end < 0 ? text : text[..end];
    }
}
