# Visual Icon Picker Tests

This directory contains visual regression tests for the icon picker dialog.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

1. Take screenshots of the icon picker dialog:
   - Emoji tab screenshot: `emoji_grid.png`
   - Icons tab screenshot: `icon_grid.png`

2. Run the visual test:
```bash
python visual_icon_test.py --emoji-screenshot emoji_grid.png --icon-screenshot icon_grid.png
```

## What it tests

- ✅ Red borders are visible (test mode)
- ✅ No overlapping containers
- ✅ Icons/emojis are centered within their containers
- ✅ Proper padding (2-20px) around icons/emojis

