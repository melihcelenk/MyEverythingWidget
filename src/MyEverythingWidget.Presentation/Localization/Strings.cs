using System.Globalization;
using System.Resources;

namespace MyEverythingWidget.Presentation.Localization;

/// <summary>
/// Every text the app shows, in the current language. The texts live in <c>Strings.resx</c> (English) and
/// <c>Strings.&lt;language&gt;.resx</c>; <c>LocalizationCoverageTests</c> keeps this class, the XAML and every
/// translation in step with them.
/// </summary>
public static class Strings
{
    /// <summary>Gets the resources of all languages.</summary>
    public static ResourceManager ResourceManager { get; } = new("MyEverythingWidget.Presentation.Localization.Strings", typeof(Strings).Assembly);

    /// <summary>
    /// Gets or sets the language of the texts; <see langword="null"/> uses <see cref="CultureInfo.CurrentUICulture"/>.
    /// </summary>
    public static CultureInfo? Culture { get; set; }

    /// <summary>Returns the text named <paramref name="key"/>, falling back to English when a language lacks it.</summary>
    public static string Get(string key) => ResourceManager.GetString(key, Culture) ?? key;

    private static string Format(string key, params object[] values) =>
        string.Format(Culture ?? CultureInfo.CurrentUICulture, Get(key), values);

    /// <summary>"Add"</summary>
    public static string Add => Get(nameof(Add));

    /// <summary>"Add app"</summary>
    public static string AddApp => Get(nameof(AddApp));

    /// <summary>"Add app…"</summary>
    public static string AddAppMenu => Get(nameof(AddAppMenu));

    /// <summary>"Add category"</summary>
    public static string AddCategory => Get(nameof(AddCategory));

    /// <summary>"Add image…"</summary>
    public static string AddImageMenu => Get(nameof(AddImageMenu));

    /// <summary>"App…"</summary>
    public static string AddMenuApp => Get(nameof(AddMenuApp));

    /// <summary>"Image…"</summary>
    public static string AddMenuImage => Get(nameof(AddMenuImage));

    /// <summary>"Note"</summary>
    public static string AddMenuNote => Get(nameof(AddMenuNote));

    /// <summary>"Add note"</summary>
    public static string AddNote => Get(nameof(AddNote));

    /// <summary>"Add to widget"</summary>
    public static string AddToWidget => Get(nameof(AddToWidget));

    /// <summary>"Always on top"</summary>
    public static string AlwaysOnTop => Get(nameof(AlwaysOnTop));

    /// <summary>"“{0}” could not be found. It may have been moved or uninstalled."</summary>
    public static string AppNotFound(string name) => Format(nameof(AppNotFound), name);

    /// <summary>"“{0}” could not be opened."</summary>
    public static string AppNotOpened(string name) => Format(nameof(AppNotOpened), name);

    /// <summary>"Browse…"</summary>
    public static string Browse => Get(nameof(Browse));

    /// <summary>"Cancel"</summary>
    public static string Cancel => Get(nameof(Cancel));

    /// <summary>"Categories"</summary>
    public static string Categories => Get(nameof(Categories));

    /// <summary>"Category name"</summary>
    public static string CategoryName => Get(nameof(CategoryName));

    /// <summary>"Change icon"</summary>
    public static string ChangeIcon => Get(nameof(ChangeIcon));

    /// <summary>"Change icon…"</summary>
    public static string ChangeIconMenu => Get(nameof(ChangeIconMenu));

    /// <summary>"Close"</summary>
    public static string Close => Get(nameof(Close));

    /// <summary>"Compact mode"</summary>
    public static string CompactMode => Get(nameof(CompactMode));

    /// <summary>"Shrink to an icon"</summary>
    public static string CompactModeTip => Get(nameof(CompactModeTip));

    /// <summary>"Copied"</summary>
    public static string Copied => Get(nameof(Copied));

    /// <summary>"Copy"</summary>
    public static string Copy => Get(nameof(Copy));

    /// <summary>"Copy {0}"</summary>
    public static string CopyEmail(string address) => Format(nameof(CopyEmail), address);

    /// <summary>"Copy image"</summary>
    public static string CopyImage => Get(nameof(CopyImage));

    /// <summary>"Copy note"</summary>
    public static string CopyNote => Get(nameof(CopyNote));

    /// <summary>"General"</summary>
    public static string DefaultCategoryName => Get(nameof(DefaultCategoryName));

    /// <summary>"Delete"</summary>
    public static string Delete => Get(nameof(Delete));

    /// <summary>"“{0}” and its {1} items will be deleted."</summary>
    public static string DeleteCategoryMany(string category, int count) => Format(nameof(DeleteCategoryMany), category, count);

    /// <summary>"“{0}” and its item will be deleted."</summary>
    public static string DeleteCategoryOne(string category) => Format(nameof(DeleteCategoryOne), category);

    /// <summary>"Delete category?"</summary>
    public static string DeleteCategoryTitle => Get(nameof(DeleteCategoryTitle));

    /// <summary>"allowed"</summary>
    public static string DropAllowed => Get(nameof(DropAllowed));

    /// <summary>"Drop or paste (Ctrl+V) files, links, text or images"</summary>
    public static string DropHint => Get(nameof(DropHint));

    /// <summary>"Drop an image here / or paste it with Ctrl+V" (two lines)</summary>
    public static string DropImageHere => Get(nameof(DropImageHere));

    /// <summary>"not allowed"</summary>
    public static string DropNotAllowed => Get(nameof(DropNotAllowed));

    /// <summary>"Drop target"</summary>
    public static string DropTarget => Get(nameof(DropTarget));

    /// <summary>"Edit"</summary>
    public static string Edit => Get(nameof(Edit));

    /// <summary>"Edit in Paint"</summary>
    public static string EditInPaint => Get(nameof(EditInPaint));

    /// <summary>"Edit note"</summary>
    public static string EditNote => Get(nameof(EditNote));

    /// <summary>"This category is full. Remove or shrink something first."</summary>
    public static string GridFull => Get(nameof(GridFull));

    /// <summary>"Image drop area"</summary>
    public static string ImageDropArea => Get(nameof(ImageDropArea));

    /// <summary>"Image not found"</summary>
    public static string ImageNotFound => Get(nameof(ImageNotFound));

    /// <summary>"That image could not be read."</summary>
    public static string ImageNotRead => Get(nameof(ImageNotRead));

    /// <summary>"Items of the previous version could not be read, so they were not imported."</summary>
    public static string ImportFailed => Get(nameof(ImportFailed));

    /// <summary>"Imported {0} items from the previous version of My Everything Widget."</summary>
    public static string Imported(int items) => Format(nameof(Imported), items);

    /// <summary>"Imported {0} items from the previous version of My Everything Widget. {1} image could not be found."</summary>
    public static string ImportedMissingImage(int items, int missingImages) => Format(nameof(ImportedMissingImage), items, missingImages);

    /// <summary>"Imported {0} items from the previous version of My Everything Widget. {1} images could not be found."</summary>
    public static string ImportedMissingImages(int items, int missingImages) => Format(nameof(ImportedMissingImages), items, missingImages);

    /// <summary>"Installed apps"</summary>
    public static string InstalledApps => Get(nameof(InstalledApps));

    /// <summary>"Enter a full path (C:\...) or a web address (https://...)."</summary>
    public static string InvalidTarget => Get(nameof(InvalidTarget));

    /// <summary>"Language"</summary>
    public static string Language => Get(nameof(Language));

    /// <summary>"System language"</summary>
    public static string LanguageSystem => Get(nameof(LanguageSystem));

    /// <summary>"Move to"</summary>
    public static string MoveTo => Get(nameof(MoveTo));

    /// <summary>"Name"</summary>
    public static string Name => Get(nameof(Name));

    /// <summary>"New category"</summary>
    public static string NewCategoryName => Get(nameof(NewCategoryName));

    /// <summary>"There is no room to move the other items there."</summary>
    public static string NoRoom => Get(nameof(NoRoom));

    /// <summary>"There is no room in {0}."</summary>
    public static string NoRoomIn(string category) => Format(nameof(NoRoomIn), category);

    /// <summary>"That is not an image."</summary>
    public static string NotAnImage => Get(nameof(NotAnImage));

    /// <summary>"Open"</summary>
    public static string Open => Get(nameof(Open));

    /// <summary>Offers a family widget that is not installed; {0} is its name.</summary>
    public static string FamilyGet(string name) => Format(nameof(FamilyGet), name);

    /// <summary>Shown on right-click of the compact icon when no other family widget is installed.</summary>
    public static string FamilyEmpty => Get(nameof(FamilyEmpty));

    /// <summary>"Open My Everything Widget"</summary>
    public static string OpenWidget => Get(nameof(OpenWidget));

    /// <summary>"Paint could not be opened."</summary>
    public static string PaintNotAvailable => Get(nameof(PaintNotAvailable));

    /// <summary>"Path or web address"</summary>
    public static string PathOrAddress => Get(nameof(PathOrAddress));

    /// <summary>"Or enter a path or web address"</summary>
    public static string PathOrAddressLabel => Get(nameof(PathOrAddressLabel));

    /// <summary>"C:\... or https://..."</summary>
    public static string PathPlaceholder => Get(nameof(PathPlaceholder));

    /// <summary>"Rate"</summary>
    public static string Rate => Get(nameof(Rate));

    /// <summary>"Rename"</summary>
    public static string Rename => Get(nameof(Rename));

    /// <summary>"Reset to original"</summary>
    public static string ResetToOriginal => Get(nameof(ResetToOriginal));

    /// <summary>"Resize"</summary>
    public static string Resize => Get(nameof(Resize));

    /// <summary>"Save"</summary>
    public static string Save => Get(nameof(Save));

    /// <summary>"Changes could not be saved: {0}"</summary>
    public static string SaveFailed(string error) => Format(nameof(SaveFailed), error);

    /// <summary>"Search installed apps"</summary>
    public static string SearchInstalledApps => Get(nameof(SearchInstalledApps));

    /// <summary>"Select icon"</summary>
    public static string SelectIcon => Get(nameof(SelectIcon));

    /// <summary>"Select image"</summary>
    public static string SelectImage => Get(nameof(SelectImage));

    /// <summary>"Settings"</summary>
    public static string Settings => Get(nameof(Settings));

    /// <summary>"Some items could not be added. Use a full path or a web address."</summary>
    public static string SomeNotAdded => Get(nameof(SomeNotAdded));

    /// <summary>"Your saved items could not be read, so the widget started empty. A copy was kept at {0}."</summary>
    public static string StateUnreadable(string backupPath) => Format(nameof(StateUnreadable), backupPath);

    /// <summary>"Theme"</summary>
    public static string Theme => Get(nameof(Theme));

    /// <summary>"Dark"</summary>
    public static string ThemeDark => Get(nameof(ThemeDark));

    /// <summary>"Light"</summary>
    public static string ThemeLight => Get(nameof(ThemeLight));

    /// <summary>"System"</summary>
    public static string ThemeSystem => Get(nameof(ThemeSystem));

    /// <summary>"Follow the Windows setting"</summary>
    public static string ThemeSystemTip => Get(nameof(ThemeSystemTip));

    /// <summary>"Use as icon"</summary>
    public static string UseAsIcon => Get(nameof(UseAsIcon));

    /// <summary>"Version {0}"</summary>
    public static string Version(string version) => Format(nameof(Version), version);

    /// <summary>"Website"</summary>
    public static string Website => Get(nameof(Website));
}
