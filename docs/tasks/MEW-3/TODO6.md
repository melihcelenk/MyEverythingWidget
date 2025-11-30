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
- [x] Note oluşturma ✅
- [x] `Create(APP, "name", ID)` formatını parse et ✅
- [x] App oluşturma ✅

**Completed Tasks:**

1. **Create App Action:** ✅
    - [x] `Create(APP, "name", ID)` formatını parse et
    - [x] FAB butonuna tıkla (Add Item Dialog açılır)
    - [x] "App" sekmesine geç
    - [x] App name input'una ismi yaz
    - [x] Mock executable dosya oluştur (geçici dizinde)
    - [x] Path input'una mock dosya yolunu yaz
    - [x] Add butonuna tıkla
    - [x] Oluşturulan app'i ID ile eşleştir

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

