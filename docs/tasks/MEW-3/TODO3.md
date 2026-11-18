# MEW-3: Unified Add Button - Tek FAB ile App/Note/Image Ekleme

## Hedef

Mevcut 2 FAB butonunu (Add App + Add Image) tek bir FAB'a indirgemek.
Tıklandığında App | Note | Image sekmeleri olan bir modal açılacak.

## Mevcut Durum

- `AddAppButton` → App ekleme dialogu açıyor
- `_add_image_button` → Image ekleme dialogu açıyor
- Not ekleme → QuickNoteEntry (her kategori sayfasında inline)

## Hedef Durum

```
[+] FAB → Modal açılır:
    ┌─────────────────────────┐
    │  App | Note | Image     │  ← Sekmeler (mevcut tab sistemi)
    ├─────────────────────────┤
    │                         │
    │  [Sekme içeriği]        │
    │                         │
    └─────────────────────────┘
```

## Teknik Gereksinim

Mevcut sekme sistemi (`TabManager`, `CategoryPage`) yapısını yeniden kullanmalıyız.
Duplicate kod olmamalı - ortak bir `TabWidget` base class veya helper olmalı.

---

## Faz 1: Ortak Tab Yapısı için Refactor ✅

**Hedef:** Mevcut sekme yapısını hem kategori sekmeleri hem de Add modal sekmeleri için kullanılabilir hale getirmek.

| #   | Görev                                                      | Durum |
|-----|------------------------------------------------------------|-------|
| 1.1 | Mevcut `TabManager` yapısını analiz et                     | ✅     |
| 1.2 | `StyledTabWidget` oluştur (`widgets/styled_tab_widget.py`) | ✅     |
| 1.3 | Kategori sekmelerini yeni yapıya migrate et                | ✅     |
| 1.4 | Testleri güncelle ve çalıştır (192 passed)                 | ✅     |

**Oluşturulan:** `widgets/styled_tab_widget.py`

- `StyledTabWidget(compact=False)` - Normal sekmeler için
- `StyledTabWidget(compact=True)` - Modal sekmeler için
- Ortak stylesheet, `add_tab_with_icon()` metodu

---

## Faz 2: Image Eklemeyi Taşıma ✅

**Hedef:** Image ekleme işlevini yeni unified modal'a taşımak.

| #   | Görev                                                                 | Durum |
|-----|-----------------------------------------------------------------------|-------|
| 2.1 | `AddItemDialog` modal yapısını oluştur (`widgets/add_item_dialog.py`) | ✅     |
| 2.2 | "Image" sekmesi içeriğini oluştur                                     | ✅     |
| 2.3 | MainWindow'da tek FAB ile entegrasyon                                 | ✅     |
| 2.4 | Eski `_add_image_button` ve `AddAppButton` kaldırıldı                 | ✅     |
| 2.5 | Testler geçiyor (192 passed)                                          | ✅     |

**Değişiklikler:**

- `widgets/add_item_dialog.py` oluşturuldu (App | Note | Image tabs)
- `main_window.py` tek FAB (+) butonu kullanıyor
- `dialog_manager.py`'a `add_app_from_data()` eklendi

---

## Faz 3: Note Eklemeyi Taşıma ✅

**Hedef:** Not ekleme işlevini yeni unified modal'a taşımak.

| #   | Görev                                                       | Durum |
|-----|-------------------------------------------------------------|-------|
| 3.1 | "Note" sekmesi içeriğini oluştur                            | ✅     |
| 3.2 | Not ekleme mantığı modal'da                                 | ✅     |
| 3.3 | Kategori sayfalarında `QuickNoteEntry` kaldı (hızlı erişim) | ✅     |
| 3.4 | "App" sekmesi - basit form (name + path)                    | ✅     |
| 3.5 | Tek FAB (+) butonu aktif                                    | ✅     |
| 3.6 | Testler geçiyor (192 passed)                                | ✅     |

**Not:** QuickNoteEntry kategori sayfalarında kaldı - kullanıcı isterse kaldırılabilir.

---

## Dosya Yapısı (Önerilen)

```
widgets/
├── add_item_dialog.py      # Unified modal (App|Note|Image tabs)
├── tabs/
│   ├── base_tab_widget.py  # Ortak tab yapısı
│   └── ...
window/
├── ui/
│   ├── tabs/
│   │   └── tab_manager.py  # BaseTabWidget kullanan
│   └── add_item/
│       ├── app_tab.py      # App ekleme sekmesi
│       ├── note_tab.py     # Note ekleme sekmesi
│       └── image_tab.py    # Image ekleme sekmesi
```

---

## Notlar

- `QuickNoteEntry` kategori sayfalarında kalabilir (hızlı erişim için)
- Modal sadece detaylı ekleme için kullanılabilir
- Sekme stili mevcut kategori sekmeleriyle tutarlı olmalı

