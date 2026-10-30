namespace MyEverythingWidget.Presentation;

/// <summary>
/// What the clipboard held when Ctrl+V was pressed, read by the view.
/// </summary>
/// <param name="FilePaths">Copied files and folders (for example from File Explorer).</param>
/// <param name="OpenBitmap">Opens the copied picture, when there is one (for example a screenshot).</param>
/// <param name="Text">Copied text, when there is any.</param>
public sealed record PastedContent(
    IReadOnlyList<string> FilePaths,
    Func<CancellationToken, Task<Stream?>>? OpenBitmap,
    string? Text);
