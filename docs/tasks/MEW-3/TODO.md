# MEW-3: Grid Drag-Drop Sistemi - Tam Düzeltme

## Açık Kaynak Referanslar ve Best Practices

### 1. react-grid-layout (GitHub: 20k+ stars)

**URL:** https://github.com/react-grid-layout/react-grid-layout

**Anahtar Özellikler:**

- `compactType: null` → İtemleri yukarı/sola sıkıştırmaz, boşluklar kalabilir
- `preventCollision: true` → Çarpışma engelleme
- Her item'ın explicit `{x, y, w, h}` pozisyonu var

**Algoritma Yaklaşımı:**

- Layout array: `[{i: 'a', x: 0, y: 0, w: 1, h: 2}, {i: 'b', x: 1, y: 0, w: 3, h: 2}]`
- Move işleminde sadece taşınan item güncellenir
- Collision detection: hedef hücreler ile mevcut itemlerin kesişimi kontrol edilir

### 2. GridStack.js (GitHub: 6k+ stars)

**URL:** https://github.com/gridstack/gridstack.js

**Anahtar Özellikler:**

- `float: true` → Android launcher gibi - itemler serbest pozisyonlanır, boşluklar kalabilir
- `staticGrid: false` → Grid dinamik, itemler taşınabilir
- Swap mode desteği

**Algoritma Yaklaşımı:**

```javascript
// float: true ile itemler yerinde kalır, otomatik sıkıştırma yok
GridStack.init({
    float: true,  // KEY: Boşluklar korunur
    cellHeight: 70,
    column: 12
});
```

### 3. Muuri (GitHub: 11k+ stars)

**URL:** https://github.com/haltu/muuri

**Anahtar Özellikler:**

- Sonsuz, responsive grid layout
- Drag sırasında gerçek boyutta placeholder
- Filtreleme ve sıralama desteği

### 4. Qt Quick Drag and Drop (Resmi Qt Örneği)

**URL:** https://doc.qt.io/qtforpython-6.5/overviews/qtquick-draganddrop-example.html

**Anahtar Özellikler:**

- QML ile drag-drop implementasyonu
- DragHandler ve DropArea kullanımı
- Visual feedback için Drag.active state

### 5. Android Launcher3 (AOSP)

**URL:** https://android.googlesource.com/platform/packages/apps/Launcher3/

**Anahtar Özellikler:**

- CellLayout: Grid hücre yönetimi
- ItemInfo: Her item'ın `cellX`, `cellY`, `spanX`, `spanY` değerleri
- `findNearestVacantArea()`: Boş alan bulma algoritması
- Swap mantığı: Hedef doluysa, kaynak boşsa swap yap

---

## Best Practices Özeti

| Kütüphane         | Boşluk Korunması    | Swap Desteği | Span Desteği       |
|-------------------|---------------------|--------------|--------------------|
| react-grid-layout | `compactType: null` | ✅            | ✅ `w`, `h`         |
| GridStack.js      | `float: true`       | ✅            | ✅ `w`, `h`         |
| Android Launcher3 | Varsayılan          | ✅            | ✅ `spanX`, `spanY` |

### Ortak Prensipler (Tüm Kütüphanelerde)

1. **Her item'ın explicit grid pozisyonu var** - (row, col, width, height)
2. **Pozisyonlar otomatik değiştirilmez** - Sadece kullanıcı eylemiyle
3. **Boşluklar korunur** - Otomatik compact/fill yok
4. **Drag visual feedback** - Gerçek boyutta placeholder/ghost
5. **Collision → Swap veya Displace** - Sadece çarpışan item etkilenir

---

## Bizim Uygulamamıza Öneriler

**react-grid-layout yaklaşımı en uygun:**

- `compactType: null` mantığını benimse
- Layout'u explicit pozisyonlarla tut
- Move işleminde sadece ilgili itemleri güncelle

**GridStack.js'den alınacak:**

- `float: true` davranışı - boşluklar korunur
- Swap mode implementasyonu

**Android Launcher3'ten alınacak:**

- `findNearestVacantArea()` algoritması
- CellLayout yaklaşımı - her hücre bağımsız

---

## Mevcut Durum ve Problemler

Önceki çalışmada (MEW-2) grid pozisyon sistemi eklenmeye çalışıldı ancak beklendiği gibi çalışmıyor. Temel problemler:

### Problem 1: Sürükleme Görsel Feedback'i Yanlış

**Sorun:**

- Bir 2x1 notu sürüklerken 1x1'lik kare görünüyor
- Sürüklenen nesne hizası bile düzgün değil (bkz: `MEW-2/img.png`)

**Teknik Analiz:**

- `draggable_mixin.py`'daki `start_drag()` metodu `widget.grab()` yapıyor
- Ama widget'ın görsel boyutu ve span'i dikkate alınmıyor
- `QDrag.setPixmap()` doğru boyutta pixmap almıyor

**Çözüm:**

- Sürükleme başladığında widget'ın gerçek boyutunu (col_span × row_span hesabıyla) kullan
- Drag pixmap boyutu widget'ın ekrandaki gerçek boyutuyla eşleşmeli
- HotSpot ayarı da düzeltilmeli

### Problem 2: Grid Satırları Otomatik Kayıyor

**Sorun:**

- Üstten bir uygulama/not taşındığında üst satır boşalınca diğer satırlar yukarı kayıyor
- Grid sabit olmalı - boş bırakılan yerler boş kalmalı

**Teknik Analiz:**

- Mevcut `_reorder_grid_items` ve `_reorder_grid_items_for_apps` metodları sequential flow kullanıyor
- Explicit grid pozisyonları (`grid_row`, `grid_col`) doğru kullanılmıyor
- Layout refresh sırasında tüm itemler yeniden diziliyor (olmamalı!)

**Çözüm:**

- Her item'ın explicit `grid_row`, `grid_col` değerlerini **asla** otomatik değiştirme
- Refresh sırasında itemleri sadece kendi kayıtlı pozisyonlarına yerleştir
- Boş hücreler boş kalsın - doldurmaya çalışma

### Problem 3: Alakasız Yer Değiştirmeler

**Sorun:**

- Bir nesneyi taşırken alakasız nesneler de yer değiştiriyor
- Sadece hedef pozisyondaki nesne etkilenmeli

**Teknik Analiz:**

- `_on_grid_drop` collision detection'ı karmaşık ve buggy
- `_reorder_grid_items` fonksiyonları tüm grid'i yeniden hesaplıyor

**Çözüm:**

- Drop işleminde SADECE:
    1. Taşınan nesnenin pozisyonunu güncelle
    2. Eğer hedef doluysa, SADECE hedef nesneyi taşı (swap veya boş yere)
- Diğer tüm nesneler yerinde kalacak

---

## Hedef Davranış (Android Launcher Mantığı)

### Temel Kurallar

1. **Grid sabit**: Her nesnenin explicit `(grid_row, grid_col)` pozisyonu var ve değiştirilmediği sürece orada kalır

2. **Silme/taşıma sonrası kayma yok**: Bir nesne silindiğinde veya taşındığında diğer nesneler yerinde kalır

3. **Boş hücreler olabilir**: Grid'de boşluklar olması normal - otomatik doldurma yok

4. **Taşıma mantığı**:
    - Nesne (2a, 2b)'den (3a, 3b)'ye taşınmak isteniyor
    - Hedef (3a, 3b) boş mu?
        - **Evet**: Nesneyi taşı, diğer hiçbir şeye dokunma
        - **Hayır**: Hedef pozisyondaki nesneyi kaynak (2a, 2b)'ye swap yap
            - Kaynak boş değilse: Hedef nesneyi ilk boş hücreye taşı

5. **Çoklu hücre nesneler (span)**:
    - col_span=2 olan bir nesne 2 sütun kaplar
    - Taşırken tüm kapladığı alan kontrol edilmeli
    - Sürüklerken bu alanın tamamı görsel olarak gösterilmeli

---

## Gerekli Değişiklikler

### 1. Sürükleme Visual Feedback'i Düzeltme

- [ ] `DraggableMixin.start_drag()` metodunu güncelle:
    - Widget'ın gerçek boyutunu hesapla (col_span × CELL_WIDTH, row_span × CELL_HEIGHT)
    - Bu boyutta pixmap oluştur
    - HotSpot'u doğru hesapla

- [ ] Widget boyut bilgisini drag başlatırken geçir:
    - `init_draggable()`'a `col_span`, `row_span` parametreleri ekle
    - Veya widget'tan dinamik olarak oku

### 2. Grid Refresh Mantığını Baştan Yaz

- [ ] `_populate_category_grid()` güncelle:
    - **Sadece explicit pozisyonları kullan** - sequential flow yok
    - Her item'ı `grid_row`, `grid_col` pozisyonuna yerleştir
    - Pozisyonu olmayan itemlere (yeni eklenen) `_find_first_available_cell()` ile pozisyon ata ve kaydet

- [ ] `_reorder_grid_items` ve `_reorder_grid_items_for_apps` kaldır veya yeniden yaz:
    - Bu fonksiyonlar eski sequential mantığı kullanıyor
    - Kaldırılabilir çünkü artık grid-based positioning var

### 3. Drop Handler'ı Baştan Yaz

- [ ] `_on_grid_drop()` metodunu basitleştir:

```python
def _on_grid_drop(self, item_id: str, target_row: int, target_col: int):
    """Android-like grid drop - SADECE gerekli nesneleri etkile"""

    # 1. Taşınan nesneyi bul
    dragged_item = find_item(item_id)
    if not dragged_item:
        return

    # 2. Taşınan nesnenin span'ini al
    row_span = getattr(dragged_item, 'row_span', 1)
    col_span = getattr(dragged_item, 'col_span', 1)

    # 3. Hedef hücreleri hesapla
    target_cells = set()
    for r in range(target_row, target_row + row_span):
        for c in range(target_col, target_col + col_span):
            target_cells.add((r, c))

    # 4. Grid sınırlarını kontrol et
    if target_col + col_span > 3:
        return  # Sığmıyor

    # 5. Kaynak hücreleri hesapla (taşınan nesnenin mevcut yeri)
    source_cells = get_cells_for_item(dragged_item)

    # 6. Hedef hücrelerde başka nesne var mı kontrol et
    #    (kendi hücrelerini hariç tut)
    occupied = get_occupied_cells(category) - source_cells
    collision_cells = target_cells & occupied

    if not collision_cells:
        # 7a. Hedef boş - sadece taşı, BAŞKA HİÇBİR ŞEYİ DEĞİŞTİRME
        dragged_item.grid_row = target_row
        dragged_item.grid_col = target_col
        save_and_refresh()
    else:
        # 7b. Hedef dolu - SADECE çarpışan nesneyi taşı
        colliding_item = find_item_at_cells(collision_cells)

        if not (source_cells & occupied):
            # Kaynak boş - swap yap
            colliding_item.grid_row = dragged_item.grid_row
            colliding_item.grid_col = dragged_item.grid_col
        else:
            # Kaynak dolu - çarpışan nesneyi ilk boş yere taşı
            empty_cell = find_first_empty(occupied | target_cells)
            colliding_item.grid_row = empty_cell[0]
            colliding_item.grid_col = empty_cell[1]

        # Taşınan nesneyi hedefe koy
        dragged_item.grid_row = target_row
        dragged_item.grid_col = target_col
        save_and_refresh()
```

### 4. GridDropZone Visual Feedback'i Güncelle

- [ ] `GridDropZone.paintEvent()` güncelle:
    - Sürüklenen nesnenin span'ini bilmeli
    - Hover highlight'ı span kadar hücreyi kapsamalı
    - Örn: 2x1 nesne sürükleniyorsa 2 hücre highlight edilmeli

- [ ] Drag MIME data'ya span bilgisi ekle:
    - Format: `"type:id:col_span:row_span"` olabilir
    - Veya ayrı bir MIME type kullan

### 5. Note Model Güncellemesi

- [ ] Note modeline `col_span`, `row_span` ekle (şu an yok):

```python
@dataclass(frozen=True)
class Note:
    # ... mevcut alanlar ...
    col_span: int = field(default=1)  # YENİ
    row_span: int = field(default=1)  # YENİ
```

- [ ] `Note.to_dict()` ve `Note.from_dict()` güncelle

---

## Uygulama Sırası

1. **Note model güncellemesi** - col_span, row_span ekle
2. **Drag visual feedback düzeltmesi** - Doğru boyutta pixmap
3. **Grid refresh mantığı yeniden yazımı** - Sequential flow kaldır
4. **Drop handler basitleştirme** - Android mantığı
5. **GridDropZone span desteği** - Multi-cell highlight
6. **Test** - Her adımda manuel test

---

## Test Senaryoları

### Visual Feedback Testleri

- [ ] 1x1 item sürüklerken 1x1 kare görünmeli
- [ ] 2x1 item sürüklerken 2x1 dikdörtgen görünmeli
- [ ] 3x1 item sürüklerken 3x1 dikdörtgen görünmeli
- [ ] Sürüklenen nesnenin hizası mouse ile eşleşmeli

### Grid Stability Testleri

- [ ] Üstten bir item taşındığında diğerleri yerinde kalmalı
- [ ] Bir item silindiğinde diğerleri yerinde kalmalı
- [ ] Boş hücreler boş kalmalı, otomatik dolmamalı

### Drop Logic Testleri

- [ ] Boş hücreye drop: sadece o item taşınmalı
- [ ] Dolu hücreye drop (kaynak boş): swap olmalı
- [ ] Dolu hücreye drop (kaynak dolu): çarpışan item boş yere gitmeli
- [ ] Hiçbir drop işleminde alakasız itemler etkilenmemeli

---

## Notlar

- Mevcut kod karmaşık hale gelmiş, muhtemelen taşıma mantığını **baştan yazmak** gerekir
- `_reorder_grid_items` fonksiyonları tamamen kaldırılabilir - artık order-based değil, grid-based sistem var
- Grid pozisyonları (`grid_row`, `grid_col`) source of truth olmalı, `order` alanı sadece geriye uyumluluk için

---

## Açık Kaynak Kodlardan Alınacak Algoritmalar

### 1. Collision Detection (react-grid-layout'tan)

```python
def collides(item1, item2) -> bool:
    """İki item çarpışıyor mu kontrol et"""
    if item1.id == item2.id:
        return False

    # Bounding box intersection
    return not (
            item1.grid_col + item1.col_span <= item2.grid_col or  # item1 solda
            item1.grid_col >= item2.grid_col + item2.col_span or  # item1 sağda
            item1.grid_row + item1.row_span <= item2.grid_row or  # item1 üstte
            item1.grid_row >= item2.grid_row + item2.row_span  # item1 altta
    )


def get_first_collision(layout, item) -> Optional[Item]:
    """İlk çarpışan item'ı bul"""
    for other in layout:
        if collides(item, other):
            return other
    return None
```

### 2. Move Item (GridStack.js float mode'dan)

```python
def move_item(item, target_row, target_col, layout):
    """Item'ı taşı - float mode (boşluklar korunur)"""

    # 1. Geçici olarak item'ı yeni pozisyona koy
    old_row, old_col = item.grid_row, item.grid_col
    item.grid_row = target_row
    item.grid_col = target_col

    # 2. Collision kontrol et
    collision = get_first_collision(layout, item)

    if collision is None:
        # Çarpışma yok - taşıma tamam
        return True

    # 3. Swap dene - kaynak boşsa
    collision.grid_row = old_row
    collision.grid_col = old_col

    # 4. Swap sonrası collision kontrol
    if get_first_collision(layout, collision) is None:
        return True  # Swap başarılı

    # 5. Swap yapılamıyorsa, collision'ı ilk boş yere taşı
    collision.grid_row, collision.grid_col = find_first_empty(layout, collision)
    return True
```

### 3. Find First Empty Cell (Android Launcher3'ten)

```python
def find_first_empty(layout, item_to_place) -> tuple[int, int]:
    """Item için ilk boş pozisyonu bul (soldan sağa, yukarıdan aşağı)"""

    occupied = set()
    for item in layout:
        if item.id == item_to_place.id:
            continue
        for r in range(item.grid_row, item.grid_row + item.row_span):
            for c in range(item.grid_col, item.grid_col + item.col_span):
                occupied.add((r, c))

    row = 0
    while True:
        for col in range(3):  # 3 sütun
            # Bu pozisyon item'a uygun mu kontrol et
            fits = True
            if col + item_to_place.col_span > 3:
                continue

            for r in range(row, row + item_to_place.row_span):
                for c in range(col, col + item_to_place.col_span):
                    if (r, c) in occupied:
                        fits = False
                        break
                if not fits:
                    break

            if fits:
                return (row, col)

        row += 1
        if row > 100:  # Güvenlik limiti
            break

    return (0, 0)  # Fallback
```

### 4. Drag Pixmap Boyutu (Qt Best Practice)

```python
def create_drag_pixmap(widget, col_span, row_span):
    """Span boyutunda drag pixmap oluştur"""
    CELL_WIDTH = 94  # 90 + 4 spacing
    CELL_HEIGHT = 94

    # Gerçek boyutu hesapla
    width = col_span * CELL_WIDTH - 4  # Son spacing'i çıkar
    height = row_span * CELL_HEIGHT - 4

    # Widget'ı bu boyutta render et
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setOpacity(0.7)

    # Widget'ı scale ederek çiz veya grab et
    widget.render(painter)

    # Border ekle
    painter.setOpacity(1.0)
    painter.setPen(QPen(QColor(33, 150, 243), 2))
    painter.drawRect(0, 0, width - 1, height - 1)
    painter.end()

    return pixmap
```

---

## Karar: Hangi Yaklaşım?

**Önerilen:** react-grid-layout + GridStack.js hybrid yaklaşımı

1. **Data Model:** react-grid-layout gibi explicit `{row, col, row_span, col_span}`
2. **Render:** Sadece explicit pozisyonlara yerleştir (GridStack float mode)
3. **Move:** Collision → Swap → Displace algoritması
4. **Visual:** Span boyutunda drag pixmap + multi-cell highlight

Bu yaklaşım mevcut kodumuza en uygun ve minimum değişiklikle uygulanabilir.

