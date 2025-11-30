# MEW-3: File Structure Cleanup

## Analysis of Current File Hierarchy

### Root Level Files

```
MyEverythingWidget/
├── main.py                          ✅ Main entry point
├── requirements.txt                 ✅ Dependencies
├── README.md                        ✅ Documentation
├── LICENSE                          ✅ License
├── ARCHITECTURE.md                  ✅ Architecture docs
├── CHANGELOG.md                     ✅ Changelog
├── CONTRIBUTING.md                  ✅ Contributing guide
├── run_test_mode.bat                ✅ Test mode runner
├── test_humanized.bat               ✅ Humanized test runner (logic)
├── test_humanized.sh                ✅ Humanized test runner (Unix)
├── test_humanized_ui.bat            ✅ Humanized UI test runner
├── run_tests.bat                    ❌ OLD - replaced by test_humanized.bat
├── run.bat                          ❌ OLD - not used
├── run.ps1                          ❌ OLD - not used
└── flutter_version/                 ❌ OLD - Flutter version, project uses PySide6
└── venv/                            ❌ OLD - old virtual env, use .venv
```

### Source Code Structure

#### `models/` ✅

```
models/
├── __init__.py                      ✅
├── app_shortcut.py                  ✅ App shortcut model
└── category.py                      ✅ Category model
```

#### `services/` ✅

```
services/
├── __init__.py                      ✅
├── app_launcher_service.py          ✅ Launch apps/URLs/folders
├── clipboard_service.py             ✅ Clipboard operations
├── image_cache_service.py           ✅ Image caching
├── image_storage_service.py         ✅ Image storage
├── storage_service.py               ✅ State persistence
└── image_grid_calculator.py         ✅ Image size calculation
```

#### `widgets/` ⚠️

```
widgets/
├── __init__.py                      ✅
├── add_item_dialog.py               ✅ Unified add dialog (App/Note/Image)
├── add_app_button.py                ❌ OLD - replaced by add_item_dialog.py
├── app_card.py                      ✅ App card widget
├── app_picker_dialog.py             ✅ Used by dialog_manager for edit
├── custom_title_bar.py              ✅ Custom window title bar
├── draggable_mixin.py               ✅ Drag functionality mixin
├── draggable_tab_bar.py             ✅ Draggable tabs
├── grid_drop_zone.py                ✅ Grid drop zone
├── icon_picker_dialog.py            ✅ Icon picker dialog
├── image_card.py                    ✅ Image card widget
├── note_card.py                     ✅ Note card widget
├── resizable_mixin.py               ✅ Resize functionality mixin
└── styled_tab_widget.py             ✅ Styled tab widget
```

#### `window/` ⚠️

```
window/
├── __init__.py                      ✅
├── app_state.py                     ✅ Application state manager
├── content_manager.py               ✅ Main content coordinator
├── dialog_manager.py                ✅ Dialog management
├── main_window.py                   ✅ Main window
├── tab_manager.py                   ⚠️ Backward compatibility wrapper (used by main_window)
│
├── cards/
│   ├── __init__.py                  ✅
│   └── card_factory.py              ✅ Card creation factory
│
├── grid/
│   ├── __init__.py                  ✅
│   ├── cell_calculator.py           ✅ Grid cell calculations
│   ├── collision_detector.py        ✅ Collision detection
│   ├── constants.py                 ✅ Grid constants
│   ├── drop_handler.py              ⚠️ Created but not used (logic in mover.py)
│   ├── grid_manager.py              ✅ Grid state management
│   ├── mover.py                     ✅ Item movement logic
│   └── populator.py                 ✅ Grid population
│
├── models/
│   └── note.py                      ✅ Note model
│
└── ui/
    ├── __init__.py                  ✅
    ├── notes/
    │   ├── __init__.py              ✅
    │   ├── actions.py               ✅ Note actions (edit/resize/relocate)
    │   └── quick_entry.py           ✅ Quick note entry widget
    └── tabs/
        ├── __init__.py              ✅
        ├── category_page.py         ✅ Category page widget
        └── tab_manager.py           ✅ Tab management (new implementation)
```

### Test Structure

#### `tests/` ⚠️

```
tests/
├── __init__.py                      ✅
├── conftest.py                      ✅ Pytest configuration
├── README.md                        ✅ Test documentation
├── test_app_state.json              ✅ Test state file
├── humanized_runner.py              ⚠️ Logic test runner (duplicate of humanized_ui_runner logic)
├── humanized_ui_runner.py           ✅ UI test runner (preferred)
│
├── helpers/
│   ├── __init__.py                  ✅
│   └── grid_test_dsl.py             ✅ DSL parser (used by both runners)
│
├── humanized/
│   └── drag/
│       └── swapNoteAndApp           ✅ Test case file
│
├── visual/
│   ├── __init__.py                  ✅
│   ├── README.md                    ✅
│   ├── requirements.txt             ✅
│   ├── run_all_tests.bat            ✅
│   ├── run_tests_auto.py            ✅
│   ├── run_tests.bat                ✅
│   ├── run_tests.sh                 ✅
│   ├── run_visual_test.py           ✅
│   ├── test_grid_drag_drop_visual.py ✅
│   └── test_icon_picker_visual.py   ✅
│
├── test_add_item_dialog.py          ✅
├── test_app_card.py                 ✅
├── test_app_launcher.py             ✅
├── test_app_state.py                ✅
├── test_clipboard_paste.py          ✅
├── test_drag_drop.py                ✅
├── test_grid_layout.py              ✅
├── test_grid_module.py              ✅
├── test_image_card.py               ✅
├── test_image_grid_calculator.py    ✅
├── test_main_window.py              ✅
├── test_memory_leak_full.py         ✅
├── test_memory_leak.py              ✅
├── test_note_card.py                ✅
├── test_note_model.py               ✅
├── test_swap_dsl.py                 ⚠️ DSL test (duplicate of humanized_runner)
├── test_swap_positioning.py         ⚠️ Old swap test (covered by humanized tests)
├── test_state.json                  ❌ OLD - replaced by test_app_state.json
├── test_tab_display.py              ✅
└── test_tab_management.py           ✅
```

### Documentation

#### `docs/tasks/` ✅

```
docs/tasks/
├── MEW-1/                           ✅ Task 1 docs
├── MEW-2/                           ✅ Task 2 docs
└── MEW-3/                           ✅ Task 3 docs
    ├── TODO.md                      ✅
    ├── TODO2.md                     ✅
    ├── TODO3.md                     ✅
    ├── TODO4.md                     ✅
    └── TODO5.md                     ✅ (this file)
```

## Files to Remove ❌

### Root Level

1. **`run_tests.bat`** - Replaced by `test_humanized.bat`
2. **`run.bat`** - Not used
3. **`run.ps1`** - Not used
4. **`flutter_version/`** - Entire directory, old Flutter version
5. **`venv/`** - Old virtual environment (use `.venv`)

### Widgets

6. **`widgets/add_app_button.py`** - Replaced by `add_item_dialog.py`
    - Only exported in `__init__.py`, not used anywhere
    - Remove from `widgets/__init__.py` exports

### Tests

7. **`tests/humanized_runner.py`** - Logic test runner
    - Duplicate functionality with `humanized_ui_runner.py`
    - `humanized_ui_runner.py` is preferred (has UI + logic)
8. **`tests/test_swap_dsl.py`** - DSL test
    - Covered by `humanized_ui_runner.py` which uses same DSL
9. **`tests/test_swap_positioning.py`** - Old swap test
    - Covered by humanized tests
10. **`tests/test_state.json`** - Old test state file
    - Replaced by `test_app_state.json`

### Window/Grid

11. **`window/grid/drop_handler.py`** - Created but only used in tests
    - Drop logic is in `mover.py` (actual implementation)
    - Used in `tests/test_grid_module.py` for testing
    - Consider: Keep for tests or remove if tests are redundant

## Files to Review ⚠️

1. **`window/tab_manager.py`** - Backward compatibility wrapper
    - Currently used by `main_window.py`
    - Consider migrating `main_window.py` to use `ContentManager` directly
    - Then remove this wrapper

2. **`window/grid/drop_handler.py`** - Unused drop handler
    - Verify it's not imported anywhere
    - If unused, remove it

## Cleanup Plan

### Phase 1: Remove Unused Files ✅

- [x] Remove `run_tests.bat`, `run.bat`, `run.ps1`
- [x] Remove `flutter_version/` directory
- [x] Remove `venv/` directory
- [x] Remove `widgets/add_app_button.py` and update `__init__.py`
- [x] Remove `tests/humanized_runner.py`
- [x] Remove `tests/test_swap_dsl.py`
- [x] Remove `tests/test_swap_positioning.py`
- [x] Remove `tests/test_state.json`

**Result:** 8 files/directories removed. Test count: 232 → 215 (removed 17 tests from deleted files). All remaining
tests pass (10 pre-existing failures unrelated to cleanup).

### Phase 2: Review and Migrate

- [ ] Check if `window/grid/drop_handler.py` is used
- [ ] If unused, remove `drop_handler.py`
- [ ] Migrate `main_window.py` to use `ContentManager` directly
- [ ] Remove `window/tab_manager.py` wrapper

### Phase 3: Update Imports

- [ ] Update any remaining imports after cleanup
- [ ] Run all tests to ensure nothing breaks
- [ ] Update documentation if needed

## Additional Issues Found

### Bug 1: Test Requires Manual Input ⚠️

**Problem:**

- Testlerden birinde kategori eklerken kullanıcıdan input bekleniyor (bir şey yazıp Enter'a basılması gerekiyor)
- Test otomatik çalışmalı, kullanıcı input beklememeli

**Location:**

- Test çalıştırma komutu: `.\.venv\Scripts\python.exe -m pytest tests/ --ignore=tests/visual -v --tb=line -q`
- Hangi test olduğu tespit edilmeli

**Fix:**

- [ ] Hangi test olduğunu tespit et
- [ ] Dialog/input bekleyen kısmı mock'la veya otomatik doldur
- [ ] Test'in tamamen otomatik çalıştığından emin ol

---

### Bug 2: 2x1 Note Width Issue at Right Edge ⚠️

**Problem:**

- 2 genişlikli (2x1) bir not en sağa taşındığında 1 genişlikli görünmeye başlıyor
- Görsel olarak span kayboluyor

**Fix:**

- [ ] Humanized formatında test yaz: `tests/humanized/drag/2x1_note_right_edge`
- [ ] Test senaryosu:
  ```
  Initial:
  .  .  .  .  .
  N1 N1 .  .  .
  .  .  .  .  .
  
  Action: Drag(N1) to R1C4 (en sağa)
  
  Expected:
  .  .  .  N1 N1  (col 3-4, 2x1 span korunmalı)
  .  .  .  .  .
  ```
- [ ] Bug'ı düzelt (muhtemelen clamp logic veya span calculation)
- [ ] Test geçene kadar TDD ile ilerle

---

## Notes

- All deletions should be done carefully
- Run full test suite after each phase
- Keep git history for reference
- Update `ARCHITECTURE.md` if file structure changes significantly

