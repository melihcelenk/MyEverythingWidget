<#
.SYNOPSIS
    Takes the README and Store screenshots in Windows Sandbox and lays each one out with its caption.

.DESCRIPTION
    1. Runs the ShowcaseScreenshots UI tests through scripts/test-ui.ps1 (made-up but realistic content, nothing
       from this PC).
    2. Puts each capture on a 1366x768 canvas (the Store's recommended minimum) with a title and one line of text.
    3. Writes the results to docs/images/showcase-<n>.png, used by README.md and the Store listing.

.PARAMETER SkipCapture
    Re-uses the captures already in tmp\sandbox\results\shots and only lays them out again.

.EXAMPLE
    pwsh scripts/capture-screenshots.ps1
#>
[CmdletBinding()]
param(
    [switch] $SkipCapture
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$shots = Join-Path $repoRoot "tmp\sandbox\results\shots"
$output = Join-Path $repoRoot "docs\images"

if (-not $SkipCapture) {
    & (Join-Path $PSScriptRoot "test-ui.ps1") -Filter "/*/*/ShowcaseScreenshots/*"
    if ($LASTEXITCODE -ne 0) { throw "Taking the screenshots failed; see tmp\sandbox\results\console.txt" }
}

Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force $output | Out-Null

$titleColor = [System.Drawing.Color]::FromArgb(0x1B, 0x1B, 0x1F)
$textColor = [System.Drawing.Color]::FromArgb(0x4A, 0x4F, 0x5A)

$pages = @(
    @{ Name = "showcase-1"; Shots = @("showcase-1-launcher"); Title = "Your daily launcher"
       Text = "Apps, folders and websites one click away. Group them in tabs and give any card an emoji." },
    @{ Name = "showcase-2"; Shots = @("showcase-2-snippets"); Title = "Text you copy again and again"
       Text = "Long commands, your signature, an address, a query. One click copies the whole note." },
    @{ Name = "showcase-3"; Shots = @("showcase-3-quick-notes"); Title = "Jot it down before it's gone"
       Text = "Press Ctrl+V on the widget and the text on the clipboard becomes a note." },
    @{ Name = "showcase-4"; Shots = @("showcase-4-screens"); Title = "Grab a screen the moment you see it"
       Text = "Paste an error screen or a chart. Click to see it large, copy it again or edit it in Paint." },
    @{ Name = "showcase-5"; Shots = @("showcase-5-expanded", "showcase-5-compact"); Title = "Out of the way when you don't need it"
       Text = "Shrink the widget to a small icon that stays on top; click it to open the widget again." }
)

function Write-Page([hashtable] $page) {
    $width = 1366; $height = 768
    $canvas = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($canvas)
    $graphics.SmoothingMode = "AntiAlias"
    $graphics.InterpolationMode = "HighQualityBicubic"
    $graphics.TextRenderingHint = "ClearTypeGridFit"
    # The canvas takes the colour of the capture's own corner, so the plain desktop around the windows blends in.
    $first = [System.Drawing.Bitmap]::FromFile((Join-Path $shots "$($page.Shots[0]).png"))
    $graphics.Clear($first.GetPixel(2, 2))
    $first.Dispose()

    $textArea = New-Object System.Drawing.RectangleF 72, 0, 500, $height
    $titleFont = New-Object System.Drawing.Font "Segoe UI Semibold", 28
    $bodyFont = New-Object System.Drawing.Font "Segoe UI", 15
    $titleSize = $graphics.MeasureString($page.Title, $titleFont, [int]$textArea.Width)
    $bodySize = $graphics.MeasureString($page.Text, $bodyFont, [int]$textArea.Width)
    $top = ($height - $titleSize.Height - 16 - $bodySize.Height) / 2
    $graphics.DrawString($page.Title, $titleFont, (New-Object System.Drawing.SolidBrush $titleColor),
        (New-Object System.Drawing.RectangleF 72, $top, $textArea.Width, $titleSize.Height))
    $graphics.DrawString($page.Text, $bodyFont, (New-Object System.Drawing.SolidBrush $textColor),
        (New-Object System.Drawing.RectangleF 72, ($top + $titleSize.Height + 16), $textArea.Width, $bodySize.Height))

    # Captures sit right of the text, side by side, shrunk (never enlarged) to fit.
    $images = $page.Shots | ForEach-Object { [System.Drawing.Image]::FromFile((Join-Path $shots "$_.png")) }
    $areaLeft = 580; $areaWidth = $width - $areaLeft - 24; $areaHeight = $height - 48
    $gap = 24
    $totalWidth = ($images | Measure-Object -Property Width -Sum).Sum + ($gap * ($images.Count - 1))
    $tallest = ($images | Measure-Object -Property Height -Maximum).Maximum
    $scale = [Math]::Min(1.0, [Math]::Min($areaWidth / $totalWidth, $areaHeight / $tallest))
    $x = $areaLeft + ($areaWidth - $totalWidth * $scale) / 2
    foreach ($image in $images) {
        $w = $image.Width * $scale; $h = $image.Height * $scale
        $y = ($height - $h) / 2
        # Two pixels are left out on every side: the capture's outer edge is not exactly the desktop colour.
        $source = New-Object System.Drawing.RectangleF 2, 2, ($image.Width - 4), ($image.Height - 4)
        $destination = New-Object System.Drawing.RectangleF ([float]$x), ([float]$y), ([float]$w), ([float]$h)
        # TileFlipXY stops GDI+ from blending the edge pixels with transparency when it scales the capture.
        $attributes = New-Object System.Drawing.Imaging.ImageAttributes
        $attributes.SetWrapMode([System.Drawing.Drawing2D.WrapMode]::TileFlipXY)
        $graphics.DrawImage($image, [System.Drawing.Rectangle]::Round($destination), $source.X, $source.Y, $source.Width, $source.Height,
            [System.Drawing.GraphicsUnit]::Pixel, $attributes)
        $attributes.Dispose()
        $x += $w + $gap * $scale
        $image.Dispose()
    }

    $target = Join-Path $output "$($page.Name).png"
    $canvas.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose(); $canvas.Dispose()
    Write-Host "==> $target"
}

foreach ($page in $pages) { Write-Page $page }
