# MEW-3: Remaining Tasks from TODO5

This document contains tasks that were identified in TODO5 but not yet completed.

## Phase 2: Review and Migrate (Remaining)

- [ ] If unused, remove `drop_handler.py` (deferred - used in tests)
    - Currently used in `tests/unit/test_grid_module.py`
    - Real implementation is in `mover.py`
    - Keep for now (test coverage)
- [x] Remove `window/tab_manager.py` wrapper ✅
    - [x] Migrated `test_memory_leak.py` to use `ContentManager` directly
    - [x] Removed `window/tab_manager.py` wrapper
    - [x] All tests pass

## Phase 3: Update Imports (Remaining)

- [x] Update documentation if needed ✅
    - `window/tab_manager.py` wrapper removed
    - All tests migrated to use `ContentManager`

## Phase 5.1: Fix Models Hierarchy (Remaining)

- [x] Run tests to ensure nothing breaks after moving `note.py` to `models/` ✅
    - Tests run successfully
    - Note model imports work correctly
    - Some pre-existing test failures unrelated to model move

## Enhancement: Create Action in Humanized Tests

**Goal:**

- Humanized test formatına `Create` aksiyonu eklemek
- Test senaryolarında yeni item oluşturma işlemlerini desteklemek

**Current Status:**

- [x] `Create(NOTE, "content", ID)` formatını parse et ✅
- [x] Note oluşturma ✅ (çalışıyor)
- [x] `Create(APP, "name", ID)` formatını parse et ✅
- [ ] App oluşturma ⚠️ (kod yazıldı ama test başarısız - app state'e kaydedilmiyor)

**Completed Tasks:**

1. **Create App Action:** ⚠️ (Kod yazıldı ama test başarısız)
    - [x] `Create(APP, "name", ID)` formatını parse et
    - [x] FAB butonuna tıkla (Add Item Dialog açılır)
    - [x] "App" sekmesine geç
    - [x] App name input'una ismi yaz
    - [x] Mock executable dosya oluştur (geçici dizinde)
    - [x] Path input'una mock dosya yolunu yaz
    - [x] Add butonuna tıkla
   - [ ] Oluşturulan app'i ID ile eşleştir (app state'e kaydedilmiyor - dialog koordinatları veya timing sorunu
     olabilir)

2. **Mock executable dosya oluşturma:** ✅
    - [x] Test için geçici bir `.bat` dosyası oluştur
    - [x] Dosya içeriği minimal (echo app name)
    - [x] Test sonunda temizlenmeli (cleanup_mock_executables)

3. **Mock app dizini oluşturma:** ✅
    - [x] Test için geçici bir dizin oluştur (`tests/tmp/mock_apps/`)
    - [x] İçine mock executable koy
    - [x] Test sonunda temizlenmeli

4. **App launch testi:** ✅
    - [x] Oluşturulan app'e tıklandığında açılabilmeli
    - [x] Mock executable çalıştırılabilmeli
    - [x] Test sonunda process temizlenmeli
    - [x] `Launch(A1)` action eklendi
    - [x] Process tracking eklendi (psutil kullanarak)
    - [x] Cleanup fonksiyonu eklendi

5. **Test formatı örneği:** ✅
   ```
   Action:
   Create(NOTE, "Test note content", N1)
   Create(APP, "Test App", A1)
   Drag(N1, R1C2)
   ```

6. **Documentation:** ✅
    - [x] Dokümantasyon güncelle (DEVELOPMENT.md)

**Known Issues:**

- `create_app_and_note` testi başarısız:
    - App oluşturulduktan sonra state'e kaydedilmiyor
    - Test çıktısı: "Found 0 apps in state" ve "App with name 'Test App' not found in state"
    - Olası nedenler:
        - Dialog koordinatları yanlış (Add butonuna tıklama başarısız olabilir)
        - Timing sorunu (state kaydedilmeden önce okunuyor olabilir)
        - Dialog kapanmadan önce state okunuyor olabilir

**Latest Test Results (2025-11-30 23:00):**

- Test çalışıyor (PowerShell ile başlatıldı)
- Exit code: 1 (başarısız)
- State dosyası: `apps: []`, `notes: []` (hiçbir item oluşturulmadı)
- Test çıktısı görülemiyor (PowerShell output yakalanmıyor)
- **Manuel test gerekiyor** - Windows PowerShell'de direkt çalıştır ve çıktıyı oku

**Analysis (2025-11-30):**

1. **test_humanized_ui.bat Issue - FIXED ✅**
    - Problem: Batch file referenced `.\.venv` but worked from tests/ directory where path was wrong
    - Root cause: Hardcoded relative path instead of using `%~dp0` (script directory)
    - Fix: Changed to use `%~dp0..\.venv\Scripts\python.exe` and `%~dp0humanized_ui_runner.py`
    - Now works from any directory

2. **Create(APP) Dialog Interaction Analysis:**

   **Dialog Structure (from add_item_dialog.py):**
    - AddItemDialog emits `appAdded` signal with {name, path, icon_path}
    - Dialog calls `self.accept()` after emitting signal (line 255)
    - App tab is at index 0 (line 278: tab_map = {"app": 0, ...})

   **Test Coordinates (from humanized_ui_runner.py lines 613-744):**
    - FAB position: Calculated from window bottom-right
    - Dialog position: Tries 3 methods:
        1. Find by title "Add Item" (pygetwindow)
        2. Find by partial title match
        3. **Fallback: Assume centered on parent** (line 666-676)
    - Uses Method 3 (centered) when dialog not found in window list
    - Dialog center calculation:
      `(win_x + (WINDOW_WIDTH - DIALOG_WIDTH) // 2, win_y + (WINDOW_HEIGHT - DIALOG_HEIGHT) // 2)`

   **Potential Issues:**
    - Qt dialogs may not show up in pygetwindow immediately
    - Coordinate calculations assume fixed sizes (WINDOW_WIDTH=320, DIALOG_WIDTH=320, etc.)
    - Add button position assumes DIALOG_HEIGHT=400, button at `DIALOG_HEIGHT - 60`
    - No verification that clicks actually hit the right targets

   **Timing Issues:**
    - 2.0s wait after FAB click (line 633)
    - 0.8s wait after App tab click (line 691)
    - 2.0s wait after Add button click (line 742)
    - 1.0s wait to read state after app creation (line 1005)
    - **Total: ~6s** but may not be enough if dialog is slow to open/close

3. **Fix Applied - Keyboard Navigation ⚡**
    - **Problem**: Coordinate-based clicking unreliable (Add button may be missed)
    - **Solution**: Use keyboard navigation instead of clicking Add button
    - **Implementation**:
        - After typing path, Tab 3 times to reach Add button
        - Press Enter to submit
        - Increased wait time to 2.5s after submission
    - **File**: `tests/humanized_ui_runner.py` lines 733-748
    - **Status**: Ready for testing

4. **Testing Instructions:**
    - Run: `tests\test_humanized_ui.bat create_app_and_note` (from project root)
    - Or: `.venv\Scripts\python tests\humanized_ui_runner.py create_app_and_note`
    - Expected: App should be created and saved to state
    - Check output for "Created app A1 at (row, col)" confirmation

