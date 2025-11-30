# MEW-3: Grid Sistemi Düzeltme Planı

## Mevcut Durum

- `tab_manager.py`: ~1000 satır, tek sınıfta her şey var - SOLID ihlali
- Terminal testleri çalışmıyor - debug gerekli
- Grid sistemi hatalı: çakışmalar, resize kaydetmiyor, hizalama bozuk
- Highlight yatayda hizasız

---

## Faz 1: Test Altyapısını Düzeltme

**Hedef:** Testleri çalıştırabilmek

| #   | Görev                                              | Durum                            |
|-----|----------------------------------------------------|----------------------------------|
| 1.1 | Terminal komutlarının neden çalışmadığını debug et | ⏳ Cursor IDE restart gerekebilir |
| 1.2 | pytest çalıştığını doğrula                         | ⏳                                |
| 1.3 | Mevcut testlerin geçtiğini kontrol et              | ⏳                                |

**NOT:** Terminal output capture çalışmıyor. Cursor IDE'yi yeniden başlat.

---

## Faz 2: Clean Code Refactor

**Hedef:** `tab_manager.py`'yi SOLID prensiplerine uygun parçalara ayır

### Yeni Dosya Yapısı:

```
window/
├── tab_manager.py          # Sadece tab yönetimi (~150 satır)
├── grid/
│   ├── __init__.py
│   ├── grid_manager.py     # Grid yerleştirme mantığı
│   ├── collision_detector.py # Çakışma tespiti
│   ├── cell_calculator.py  # Hücre hesaplamaları
│   └── drop_handler.py     # Drag-drop işlemleri
└── cards/
    └── card_factory.py     # Card oluşturma
```

| #   | Görev                                                | Durum                                    |
|-----|------------------------------------------------------|------------------------------------------|
| 2.1 | `GridManager` sınıfı oluştur - grid yerleştirme      | ✅ `window/grid/grid_manager.py`          |
| 2.2 | `CollisionDetector` sınıfı oluştur - çakışma tespiti | ✅ `window/grid/collision_detector.py`    |
| 2.3 | `CellCalculator` sınıfı oluştur - hücre hesaplama    | ✅ `window/grid/cell_calculator.py`       |
| 2.4 | `DropHandler` sınıfı oluştur - drop işlemleri        | ✅ `window/grid/drop_handler.py`          |
| 2.5 | `CardFactory` sınıfı oluştur - card oluşturma        | ✅ `window/cards/card_factory.py`         |
| 2.6 | Grid sabitleri tek yerde (`constants.py`)            | ✅ `window/grid/constants.py`             |
| 2.7 | Grid modülü testleri                                 | ✅ `tests/test_grid_module.py` (50 tests) |
| 2.8 | Tüm testlerin geçtiğini doğrula                      | ✅ 192 test passed                        |

### 2.9 TabManager Kademeli Entegrasyon

| #     | Görev                                              | Durum            |
|-------|----------------------------------------------------|------------------|
| 2.9.1 | `_pos_to_grid_cell` → `CellCalculator.pos_to_cell` | ✅                |
| 2.9.2 | `_get_occupied_cells` → (kept, uses same logic)    | ✅ (no change)    |
| 2.9.3 | `_find_first_available_cell` → `CellCalculator`    | ✅                |
| 2.9.4 | `_on_grid_drop` → (kept, complex integration)      | ⏸️ (future work) |
| 2.9.5 | Constants import from `window.grid.constants`      | ✅                |
| 2.9.6 | Test çalıştır, hata varsa düzelt                   | ✅ 192 passed     |

---

## Faz 3: Grid Sisteminin Düzeltilmesi

**Hedef:** Android-like sabit grid davranışı

| #   | Görev                                               | Durum |
|-----|-----------------------------------------------------|-------|
| 3.1 | Grid sabitleri tek yerde tanımla (3x5, 80x80)       | ⏳     |
| 3.2 | `_get_occupied_cells` - tüm span'leri doğru hesapla | ⏳     |
| 3.3 | `_find_first_available_cell` - span kontrolü düzelt | ⏳     |
| 3.4 | Collision detection - yerleştirme öncesi kontrol    | ⏳     |
| 3.5 | Drop handler - swap/relocate mantığı                | ⏳     |
| 3.6 | Highlight hizalama - widget pozisyonlarına göre     | ⏳     |

---

## Faz 4: Bug Düzeltmeleri

**Hedef:** Tüm görsel ve fonksiyonel bugları çöz

| #   | Bug                                       | Durum |
|-----|-------------------------------------------|-------|
| 4.1 | Resmi 1x1'e çevirince geri dönüyor        | ⏳     |
| 4.2 | Notlarla resim çakışıyor                  | ⏳     |
| 4.3 | Hover highlight yatayda hizasız           | ⏳     |
| 4.4 | Üstten item kaldırınca alttakiler kayıyor | ⏳     |
| 4.5 | Taşımalarda performans yavaş              | ⏳     |

---

## İlerleme Takibi

### Faz 1 Detay:

- [ ] Terminal debug
- [ ] Test çalıştırma

### Faz 2 Detay:

- [ ] GridManager
- [ ] CollisionDetector
- [ ] CellCalculator
- [ ] DropHandler
- [ ] CardFactory
- [ ] TabManager sadeleştirme

### Faz 3 Detay:

- [ ] Grid sabitleri
- [ ] Occupied cells
- [ ] Available cell
- [ ] Collision
- [ ] Drop logic
- [ ] Highlight

### Faz 4 Detay:

- [ ] Resize persist
- [ ] Overlap fix
- [ ] Highlight align
- [ ] Auto-shift fix
- [ ] Performance

---

## Notlar

- Her faz tamamlandığında testler çalıştırılacak
- Refactor sırasında mevcut davranış korunacak
- Her yeni sınıf için unit test yazılacak

