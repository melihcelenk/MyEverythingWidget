# Import Fix Explanation

## Problem
Python relative imports (`from ..module`) don't work when running a script directly with `python main.py` because Python doesn't treat the directory as a package.

## Solution
Changed all relative imports to absolute imports and added project root to `sys.path` in `main.py`.

### Changes Made:
1. **main.py**: Added project root to `sys.path` before imports
2. **All modules**: Changed `from ..module` to `from module` (absolute imports)

### Example:
```python
# Before (relative import - doesn't work with python main.py)
from ..models.app_shortcut import AppShortcut

# After (absolute import - works!)
from models.app_shortcut import AppShortcut
```

## Files Modified:
- `main.py` - Added sys.path setup
- `window/app_state.py` - Fixed imports
- `window/main_window.py` - Fixed imports
- `widgets/app_card.py` - Fixed imports
- `widgets/app_picker_dialog.py` - Fixed imports
- `services/app_launcher_service.py` - Fixed imports

## Why This Works:
When `main.py` runs, it adds the project root (`pyside6_version/`) to `sys.path`, making all top-level packages (`models`, `window`, `widgets`, `services`) directly importable.

## Alternative Solutions (Not Used):
1. Run as module: `python -m window.main_window` (requires restructuring)
2. Use PYTHONPATH environment variable (less portable)
3. Install as package (overkill for this project)

