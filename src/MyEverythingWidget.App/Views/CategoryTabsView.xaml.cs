using System.Collections.Specialized;
using System.ComponentModel;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using Microsoft.UI.Xaml.Input;
using MyEverythingWidget.Presentation;
using Windows.Foundation.Collections;
using Windows.System;

namespace MyEverythingWidget.App.Views;

/// <summary>
/// Category tabs: select, add, rename, delete and reorder. The tab items mirror
/// <see cref="BoardViewModel.Categories"/>; user actions go to the view model, which then updates the tabs.
/// </summary>
public sealed partial class CategoryTabsView : UserControl
{
    private BoardViewModel? _board;
    private bool _isSyncing;

    /// <summary>Creates the view.</summary>
    public CategoryTabsView()
    {
        InitializeComponent();
    }

    /// <summary>Gets or sets what is shown before the tabs (the compact button).</summary>
    public object? LeadingContent
    {
        get => LeadingPresenter.Content;
        set => LeadingPresenter.Content = value;
    }

    /// <summary>Gets or sets what is shown at the right end of the strip (the window buttons).</summary>
    public object? TrailingContent
    {
        get => TrailingPresenter.Content;
        set => TrailingPresenter.Content = value;
    }

    /// <summary>Gets the empty part of the strip, which drags the window.</summary>
    public UIElement DragRegion => DragArea;

    /// <summary>Gets or sets the board whose categories are shown; set once after construction.</summary>
    public BoardViewModel? Board
    {
        get => _board;
        set
        {
            if (_board is not null)
            {
                _board.Categories.CollectionChanged -= OnCategoriesChanged;
                _board.PropertyChanged -= OnBoardPropertyChanged;
            }

            _board = value;
            if (_board is not null)
            {
                _board.Categories.CollectionChanged += OnCategoriesChanged;
                _board.PropertyChanged += OnBoardPropertyChanged;
            }

            RebuildTabs();
        }
    }

    private void OnCategoriesChanged(object? sender, NotifyCollectionChangedEventArgs e) => RebuildTabs();

    private void OnBoardPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(BoardViewModel.SelectedCategoryId))
        {
            SelectOpenTab();
        }
    }

    /// <summary>Recreates the tab items from the view model; cheap, as there are only a few categories.</summary>
    private void RebuildTabs()
    {
        _isSyncing = true;
        try
        {
            foreach (var tab in Tabs.TabItems.OfType<TabViewItem>())
            {
                ((CategoryViewModel)tab.Tag).PropertyChanged -= OnCategoryPropertyChanged;
            }

            Tabs.TabItems.Clear();
            foreach (var category in _board?.Categories ?? [])
            {
                Tabs.TabItems.Add(CreateTab(category));
            }

            SelectOpenTab();
        }
        finally
        {
            _isSyncing = false;
        }
    }

    private TabViewItem CreateTab(CategoryViewModel category)
    {
        var tab = new TabViewItem
        {
            Header = category.Name,
            Tag = category,
            IsClosable = false,
            ContextFlyout = CreateTabMenu(category),
        };
        AutomationProperties.SetAutomationId(tab, "Tab_" + category.Id);
        AutomationProperties.SetName(tab, category.Name);
        tab.DoubleTapped += (_, _) => ShowRenameEditor(tab);
        category.PropertyChanged += OnCategoryPropertyChanged;
        return tab;
    }

    private void OnCategoryPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(CategoryViewModel.Name) && sender is CategoryViewModel category && FindTab(category.Id) is { } tab)
        {
            tab.Header = category.Name;
            AutomationProperties.SetName(tab, category.Name);
        }
    }

    private MenuFlyout CreateTabMenu(CategoryViewModel category)
    {
        var rename = new MenuFlyoutItem { Text = "Rename", Icon = new FontIcon { Glyph = "\uE8AC" } };
        AutomationProperties.SetAutomationId(rename, "RenameCategoryMenuItem");
        rename.Click += (_, _) =>
        {
            if (FindTab(category.Id) is { } tab)
            {
                ShowRenameEditor(tab);
            }
        };

        var delete = new MenuFlyoutItem { Text = "Delete", Icon = new FontIcon { Glyph = "\uE74D" } };
        AutomationProperties.SetAutomationId(delete, "DeleteCategoryMenuItem");
        delete.Click += async (_, _) => await ConfirmAndDeleteAsync(category);

        var menu = new MenuFlyout();
        menu.Items.Add(rename);
        menu.Items.Add(delete);
        menu.Opening += (_, _) => delete.IsEnabled = _board?.CanDeleteCategory == true;
        return menu;
    }

    private void SelectOpenTab()
    {
        var open = _board is null ? null : FindTab(_board.SelectedCategoryId);
        if (open is not null && !ReferenceEquals(Tabs.SelectedItem, open))
        {
            var wasSyncing = _isSyncing;
            _isSyncing = true;
            Tabs.SelectedItem = open;
            _isSyncing = wasSyncing;
        }
    }

    private TabViewItem? FindTab(string categoryId) =>
        Tabs.TabItems.OfType<TabViewItem>().FirstOrDefault(tab => ((CategoryViewModel)tab.Tag).Id == categoryId);

    private void OnSelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (!_isSyncing && Tabs.SelectedItem is TabViewItem { Tag: CategoryViewModel category })
        {
            _board?.SelectCategory(category.Id);
        }
    }

    /// <summary>The user dragged a tab to a new position; pass the new order to the view model.</summary>
    private void OnTabItemsChanged(TabView sender, IVectorChangedEventArgs args)
    {
        if (_isSyncing || _board is null || args.CollectionChange != CollectionChange.ItemInserted)
        {
            return;
        }

        var order = Tabs.TabItems.OfType<TabViewItem>().Select(tab => ((CategoryViewModel)tab.Tag).Id).ToList();
        if (order.Count == _board.Categories.Count && !order.SequenceEqual(_board.Categories.Select(category => category.Id)))
        {
            // Applied after the drag finishes, so the tab strip is not rebuilt in the middle of it.
            DispatcherQueue.TryEnqueue(() => _board.ReorderCategories(order));
        }
    }

    private void OnAddClicked(object sender, RoutedEventArgs e)
    {
        if (_board is null)
        {
            return;
        }

        var added = _board.AddCategory(BoardViewModel.NewCategoryName);
        if (FindTab(added.Id) is not { } tab)
        {
            return;
        }

        // The editor is attached to the tab, so wait until the new tab is in the visual tree.
        if (tab.IsLoaded)
        {
            ShowRenameEditor(tab);
        }
        else
        {
            void ShowWhenLoaded(object sender, RoutedEventArgs args)
            {
                tab.Loaded -= ShowWhenLoaded;
                ShowRenameEditor(tab);
            }

            tab.Loaded += ShowWhenLoaded;
        }
    }

    private void ShowRenameEditor(TabViewItem tab)
    {
        var category = (CategoryViewModel)tab.Tag;
        var editor = new TextBox
        {
            Text = category.Name,
            MinWidth = 160,
            MaxLength = Core.State.WidgetBoard.MaxCategoryNameLength,
        };
        AutomationProperties.SetAutomationId(editor, "CategoryNameBox");
        AutomationProperties.SetName(editor, "Category name");

        var flyout = new Flyout { Content = editor, Placement = FlyoutPlacementMode.Bottom };
        var cancelled = false;
        editor.KeyDown += (_, e) =>
        {
            if (e.Key == VirtualKey.Enter)
            {
                flyout.Hide();
                e.Handled = true;
            }
            else if (e.Key == VirtualKey.Escape)
            {
                cancelled = true;
                flyout.Hide();
                e.Handled = true;
            }
        };
        editor.Loaded += (_, _) =>
        {
            editor.Focus(FocusState.Programmatic);
            editor.SelectAll();
        };
        flyout.Closed += (_, _) =>
        {
            if (!cancelled)
            {
                _board?.RenameCategory(category.Id, editor.Text);
            }
        };
        flyout.ShowAt(tab);
    }

    private async Task ConfirmAndDeleteAsync(CategoryViewModel category)
    {
        if (_board is null || !_board.CanDeleteCategory)
        {
            return;
        }

        if (category.ItemCount > 0)
        {
            var dialog = new ContentDialog
            {
                XamlRoot = XamlRoot,
                Title = "Delete category?",
                Content = category.ItemCount == 1
                    ? $"“{category.Name}” and its item will be deleted."
                    : $"“{category.Name}” and its {category.ItemCount} items will be deleted.",
                PrimaryButtonText = "Delete",
                CloseButtonText = "Cancel",
                DefaultButton = ContentDialogButton.Close,
            };
            AutomationProperties.SetAutomationId(dialog, "DeleteCategoryDialog");
            DialogSizing.FitToWindow(dialog, XamlRoot);
            if (await dialog.ShowAsync() != ContentDialogResult.Primary)
            {
                return;
            }
        }

        _board.DeleteCategory(category.Id);
    }
}
