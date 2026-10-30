using MyEverythingWidget.Core.Apps;
using MyEverythingWidget.Core.Grid;
using MyEverythingWidget.Core.Legacy;
using MyEverythingWidget.Core.State;

namespace MyEverythingWidget.Core.Tests.Apps;

/// <summary>
/// Paths written with forward slashes (as the Python version saved them) must be turned into Windows paths: the
/// Windows shell cannot create an item, and so no icon, from <c>C:/...</c>.
/// </summary>
public sealed class PathNormalizationTests
{
    [Fact]
    public void Classify_ForwardSlashPath_IsNormalized()
    {
        var target = LaunchTarget.Classify("C:/Program Files/Tool/tool.exe", _ => false);

        Assert.Equal(@"C:\Program Files\Tool\tool.exe", target!.Target);
        Assert.Equal("Tool", target.SuggestedName);
    }

    [Fact]
    public void Classify_ForwardSlashFolder_IsNormalized()
    {
        var target = LaunchTarget.Classify("D:/Music/", path => path == @"D:\Music\");

        Assert.Equal(new LaunchTarget(LaunchKind.Folder, @"D:\Music\", "Music"), target);
    }

    [Fact]
    public void Classify_Url_IsNotTouched()
    {
        Assert.Equal("https://example.org/a/b", LaunchTarget.Classify("https://example.org/a/b", _ => false)!.Target);
    }

    [Fact]
    public void LegacyImport_ForwardSlashTargets_AreNormalized()
    {
        var data = LegacyStateReader.Parse("""
            { "categories": [{ "name": "Work" }],
              "apps": [{ "name": "Tool", "target": "C:/Program Files/Tool/tool.exe", "category": "Work", "type": "exe" },
                       { "name": "Site", "target": "https://example.org/x/y", "category": "Work", "type": "url" }],
              "notes": [{ "content": "C:/Users/me/report.pdf", "type": "file", "category": "Work" }] }
            """);

        var import = LegacyImporter.Build(data, () => Guid.NewGuid().ToString("N"), GridSize.Default);

        var targets = import.State.Items.OfType<AppItem>().Select(app => app.Target).ToList();
        Assert.Contains(@"C:\Program Files\Tool\tool.exe", targets);
        Assert.Contains("https://example.org/x/y", targets);
        Assert.Contains(@"C:\Users\me\report.pdf", targets);
        Assert.All(import.AppsNeedingIcons.Where(icon => icon.Target.Kind != LaunchKind.Url), icon => Assert.DoesNotContain('/', icon.Target.Target));
    }
}
