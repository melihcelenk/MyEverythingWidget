# Store Listing (draft)

## Name

My Everything Widget

## Short description

Your apps, notes and images in one small, always-ready widget.

## Description

My Everything Widget keeps the things you reach for every day one click away: apps, folders, websites, quick notes
and images, arranged on a tidy grid that stays exactly where you put it.

- **Add apps the easy way.** Pick from the apps installed on your PC, drop a file, folder or link on the widget, or
  paste it with Ctrl+V. Every card gets the app's own icon automatically.
- **Notes and images.** Paste text to make a note, paste a screenshot to pin it. Copy a note back with one click.
- **A grid that stays put.** Drag cards anywhere; nothing slides around on its own. Make notes and images bigger by
  dragging their corner.
- **Categories.** Keep work, music and personal shortcuts on separate tabs.
- **Fits Windows 11.** Light and dark theme, Mica, and always-on-top when you want it.
- **Private.** Everything stays on your PC.

## What's new (first release)

- Completely rewritten for Windows 11.
- Items from the previous version are imported automatically.

## Keywords

launcher, shortcuts, widget, notes, quick access, productivity, desktop

Partner Center accepts at most seven keywords.

## Screenshots

Three screenshots, 1366x768 with caption, in `docs/images/` (the README uses the same files):

| File | Caption |
|------|---------|
| `store-1.png` | Everything you love, one click away |
| `store-2.png` | Copy it. Ctrl+V. Saved in a second. |
| `store-3.png` | Always at hand, always on top |

`pwsh scripts/capture-screenshots.ps1` takes the captures in Windows Sandbox (`docs/images/captures/`) and runs
`python scripts/compose-store-images.py`, which builds the three pages from them. To change only the captions or the
layout, run the Python script alone. Content is made up; the photos are from Unsplash (see
`docs/images/assets/CREDITS.md`).
