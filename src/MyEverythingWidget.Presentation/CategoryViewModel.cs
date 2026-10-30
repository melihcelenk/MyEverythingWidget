using CommunityToolkit.Mvvm.ComponentModel;

namespace MyEverythingWidget.Presentation;

/// <summary>
/// One category tab. Instances are kept while the category exists and change in place.
/// </summary>
public sealed partial class CategoryViewModel : ObservableObject
{
    [ObservableProperty]
    public partial string Name { get; set; }

    [ObservableProperty]
    public partial int ItemCount { get; set; }

    [ObservableProperty]
    public partial bool IsSelected { get; set; }

    /// <summary>Creates the tab view model of category <paramref name="id"/>.</summary>
    public CategoryViewModel(string id, string name)
    {
        Id = id;
        Name = name;
    }

    /// <summary>Gets the category id.</summary>
    public string Id { get; }
}
