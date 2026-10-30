using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.Apps;

public sealed class LaunchTargetTests
{
    private static readonly HashSet<string> Folders = new(StringComparer.OrdinalIgnoreCase) { @"C:\Projects", @"D:\Music\" };

    private static LaunchTarget? Classify(string text) => LaunchTarget.Classify(text, Folders.Contains);

    [Theory]
    [InlineData("https://github.com/melihcelenk", "https://github.com/melihcelenk", "Github")]
    [InlineData("http://example.org/a?b=1", "http://example.org/a?b=1", "Example")]
    [InlineData("www.youtube.com", "https://www.youtube.com", "Youtube")]
    [InlineData("  https://docs.microsoft.com  ", "https://docs.microsoft.com", "Docs.microsoft")]
    public void Url_IsRecognisedWithSiteName(string text, string target, string name)
    {
        var result = Classify(text);

        Assert.Equal(new LaunchTarget(LaunchKind.Url, target, name), result);
    }

    [Fact]
    public void ExistingFolder_IsFolderNamedAfterIt()
    {
        Assert.Equal(new LaunchTarget(LaunchKind.Folder, @"C:\Projects", "Projects"), Classify(@"C:\Projects"));
        Assert.Equal(new LaunchTarget(LaunchKind.Folder, @"D:\Music\", "Music"), Classify(@"D:\Music\"));
    }

    [Theory]
    [InlineData(@"C:\Windows\notepad.exe", "Notepad")]
    [InlineData(@"""C:\Program Files\Mozilla Firefox\firefox.exe""", "Firefox")]
    [InlineData(@"C:\Users\me\Desktop\Visual Studio Code.lnk", "Visual Studio Code")]
    [InlineData(@"C:\tools\build-all.bat", "Build-all")]
    public void FilePath_IsExecutableNamedAfterFile(string text, string name)
    {
        var result = Classify(text);

        Assert.NotNull(result);
        Assert.Equal(LaunchKind.Executable, result.Kind);
        Assert.Equal(text.Trim('"'), result.Target);
        Assert.Equal(name, result.SuggestedName);
    }

    [Fact]
    public void AppsFolderItem_IsExecutable()
    {
        var result = Classify(@"shell:AppsFolder\Microsoft.WindowsNotepad_8wekyb3d8bbwe!App");

        Assert.Equal(new LaunchTarget(LaunchKind.Executable, @"shell:AppsFolder\Microsoft.WindowsNotepad_8wekyb3d8bbwe!App", "Microsoft.WindowsNotepad_8wekyb3d8bbwe!App"), result);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("hello world")]
    [InlineData("notepad")]
    [InlineData("ftp://files.example.org")]
    [InlineData("javascript:alert(1)")]
    public void Unrecognised_ReturnsNull(string text)
    {
        Assert.Null(Classify(text));
    }
}
