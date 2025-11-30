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
- [ ] `Create(APP, "name", ID)` formatını parse et (henüz yapılmadı)
- [ ] App oluşturma (tüm alt görevler)

**Remaining Tasks:**

1. **Create App Action:**
    - [ ] `Create(APP, "name", ID)` formatını parse et
    - [ ] FAB butonuna tıkla (Add Item Dialog açılır)
    - [ ] "App" sekmesine geç
    - [ ] App name input'una ismi yaz
    - [ ] Mock executable dosya oluştur (geçici dizinde)
    - [ ] Path input'una mock dosya yolunu yaz
    - [ ] Icon seç (opsiyonel, default icon kullanılabilir)
    - [ ] Add butonuna tıkla
    - [ ] Oluşturulan app'i ID ile eşleştir

2. **Mock executable dosya oluşturma:**
    - [ ] Test için geçici bir `.exe` veya `.bat` dosyası oluştur
    - [ ] Dosya içeriği minimal olabilir (echo gibi)
    - [ ] Test sonunda temizlenmeli

3. **Mock app dizini oluşturma:**
    - [ ] Test için geçici bir dizin oluştur
    - [ ] İçine mock executable koy
    - [ ] Test sonunda temizlenmeli

4. **App launch testi:**
    - [ ] Oluşturulan app'e tıklandığında açılabilmeli
    - [ ] Mock executable çalıştırılabilmeli
    - [ ] Test sonunda process temizlenmeli

5. **Test formatı örneği:**
   ```
   Action:
   Create(NOTE, "Test note content", N1)
   Create(APP, "Test App", A1)
   Drag(N1, R1C2)
   ```

6. **Documentation:**
    - [ ] Mevcut testleri güncelle (gerekirse)
    - [ ] Dokümantasyon güncelle

