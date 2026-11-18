# Faz 4 — Kategoriler

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Bu fazda kartlar kategorilere ayrıldı ve pencerenin üstünde kategori sekmeleri göründü. Sekmeye tıklayınca o
kategorinin kartları açılıyor; "+" ile yeni kategori ekleniyor ve adı hemen düzenleniyor; sağ tık ya da çift tıkla
yeniden adlandırılıyor, sağ tıkla siliniyor ve sekmeler sürüklenerek sıralanıyor. Kartın sağ tık menüsündeki
"Move to" ile kart başka kategoriye taşınıyor; açık sekme hatırlanıyor ve uygulama aynı sekmeyle açılıyor.

## Problem

- Faz 3'te yalnız seçili (tek) kategorinin kartları görünüyordu; kategori ekleme, yeniden adlandırma, silme ve
  sıralama yoktu (durum modelinde yerleri Faz 2'den hazırdı).
- Kartı bir kategoriden diğerine taşımanın yolu yoktu.
- Uygulama yeniden açılınca hangi sekmenin açık olduğu bilinmiyordu.

## Çözüm

- **Core (`WidgetBoard`):** Kategori ekle, adlandır, sil, sırala, seç ve öğeyi başka kategoriye taşı; kurallar
  (boş ad, 30 karakter, son kategori, yer yok) burada.
- **ViewModel (`BoardViewModel`, `CategoryViewModel`):** Sekmelerin listesi ve seçili sekme Core ile senkron; uyarılar
  durum çubuğunda.
- **View (`CategoryTabsView`):** WinUI `TabView`, kapat düğmesi yok; "+" şeridin sonunda; sağ tık "Rename" ve
  "Delete", çift tıkla adlandırma, sürükleyerek sıralama.
- **Kart menüsü:** "Move to" → diğer kategoriler.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 4.1 | `WidgetBoard` kategori ekler, adlandırır, siler, sıralar ve seçer. | 🟢 Tamamlandı |
| 4.2 | `BoardViewModel` sekmeleri `CategoryViewModel` ile Core'a senkron tutar. | 🟢 Tamamlandı |
| 4.3 | `CategoryTabsView` sekmeleri gösterir, ekler, adlandırır, siler ve sıralar. | 🟢 Tamamlandı |
| 4.4 | Kartın sağ tık menüsündeki "Move to" kartı başka kategoriye taşır. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Sekme kontrolü ne olur? | WinUI `TabView`, kapat düğmesi yok | 🟢 Verildi | Sürükleyerek sıralama hazır; kapatma = silme olmamalı |
| Sekme şeridi nasıl görünür? | Şerit Mica üzerinde; açık sekme ve grid ortak katman renginde (`LayerFillColorDefaultBrush`) | 🟢 Verildi | Windows 11 sekmeli uygulamalarıyla aynı dil |
| Kategori nasıl eklenir? | "+" şeridin sonunda; yeni sekme açılır, ad kutusu seçili metinle gelir | 🟢 Verildi | Tek tıkla ekle, hemen adlandır |
| Silerken onay sorulur mu? | Yalnız öğe varsa; varsayılan düğme "Cancel" | 🟢 Verildi | Boş kategoride gereksiz soru yok, dolu kategoride kazara silme yok |

## Nasıl kontrol edilir

- [ ] "+" düğmesine bas: yeni bir sekme açılmalı ve ad kutusu seçili metinle gelmeli; ad yazıp Enter'a bas.
- [ ] Bir sekmeye sağ tıkla → "Rename" (ya da sekmeye çift tıkla) ve adı değiştir: sekmenin adı değişmeli.
- [ ] Ada 30 karakterden uzun bir metin yaz: ad 30 karaktere kısaltılmalı. Adı boş bırak: ad değişmemeli.
- [ ] İçinde kart olan bir sekmeye sağ tıkla → "Delete": onay sorulmalı, "Cancel" ile hiçbir şey değişmemeli.
- [ ] Tek sekme kalınca sağ tık menüsüne bak: "Delete" pasif olmalı.
- [ ] Bir sekmeyi sürükleyip başka yere bırak: sekmelerin sırası değişmeli.
- [ ] Bir karta sağ tıkla → "Move to" → başka kategori: kart o kategoriye geçmeli.
- [ ] Başka bir sekmeyi açıp uygulamayı kapat ve yeniden aç: aynı sekmeyle açılmalı.

## Kalan

- Yok.

## Ayrıntılar

### 4.1 — `WidgetBoard` kategori ekler, adlandırır, siler, sıralar ve seçer.

- **Mevcut durum:** Durum modelinde kategoriler vardı ama işlemleri yoktu (Faz 2).
- **Problem:** Kategori kuralları UI'dan bağımsız olarak Core'da tutulmalıydı.
- **Çözüm:**
  - İşlemler: ekle, adlandır, sil, sırala, seç, öğeyi başka kategoriye taşı.
  - Kategori adı boş ya da yalnız boşluksa ad değişmez (yeni kategoride "New category" kalır); 30 karakterden uzunsa
    30 karaktere kısaltılır.
  - Son kategori silinemez (Core reddeder).
  - Açık sekme silinirse solundaki sekme açılır (ilk sekmeyse yeni ilk sekme).
  - Kayıtlı açık sekme artık yoksa (örnek: elle düzenlenmiş dosya) ilk sekme açılır.
- **Dosyalar:** `src/MyEverythingWidget.Core/State/WidgetBoard.cs`
- **Testler:** `Core.Tests` → `WidgetBoardCategoryTests` (17)
- **Durum:** 🟢 Tamamlandı.

### 4.2 — `BoardViewModel` sekmeleri `CategoryViewModel` ile Core'a senkron tutar.

- **Mevcut durum:** `BoardViewModel` yalnız tek kategorinin kartlarını tutuyordu (Faz 3).
- **Problem:** Sekme listesi, seçili sekme ve uyarılar View'a bağlanabilmeliydi.
- **Çözüm:**
  - `CategoryViewModel` her kategoriyi temsil eder; `BoardViewModel` sekme listesini ve seçili sekmeyi Core ile senkron
    tutar.
  - "Move to" hedef kategoride yer yoksa "There is no room in {ad}." uyarısı durum çubuğunda gösterilir.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.Presentation/CategoryViewModel.cs`
- **Testler:** `Presentation.Tests` → `BoardViewModelCategoryTests` (12)
- **Durum:** 🟢 Tamamlandı.

### 4.3 — `CategoryTabsView` sekmeleri gösterir, ekler, adlandırır, siler ve sıralar.

- **Mevcut durum:** Pencerede sekme şeridi yoktu.
- **Problem:** Kullanıcı kategorileri görüp yönetebilmeliydi.
- **Çözüm:**
  - WinUI `TabView`, kapat düğmesi yok; şerit Mica üzerinde, açık sekme ve grid `LayerFillColorDefaultBrush`
    renginde.
  - "+" şeridin sonunda; yeni sekme açılır ve ad kutusu seçili metinle gelir. Ad kutusu, yeni sekme görsel ağaca
    girmeden açılmaya çalışıldığı için açılmıyordu; artık sekmenin `Loaded` olayı bekleniyor.
  - Sağ tık "Rename" ya da çift tık ile adlandırma; sağ tık "Delete" (son kategoride pasif). Kategoride öğe varsa onay
    sorulur, varsayılan düğme "Cancel".
  - Sekmeler sürüklenerek sıralanır; açık sekme kaydedilir.
  - Silme onayının "Cancel" düğmesinin otomasyon kimliği (`CloseButton`) pencerenin kapat düğmesiyle aynı; testler
    dialog düğmelerini `DeleteCategoryDialog` içinde arar.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/CategoryTabsView.xaml`, `src/MyEverythingWidget.App/Views/CategoryTabsView.xaml.cs`
- **Testler:** `UiTests` → `CategoryTests.PlusButton_CreatesNamedCategoryAndOpensIt`, `SelectingTab_ShowsOnlyItsCards`,
  `OpenTab_IsRestoredAfterRestart`, `RenameFromContextMenu_ChangesTabName`,
  `DeleteCategoryWithItems_AsksAndThenDeletesItAndItsItems`, `DeleteCategory_Cancelled_KeepsEverything`,
  `DraggingTab_ReordersCategories` (gerçek fare)
- **Durum:** 🟢 Tamamlandı.

### 4.4 — Kartın sağ tık menüsündeki "Move to" kartı başka kategoriye taşır.

- **Mevcut durum:** Kartın sağ tık menüsünde yalnız "Delete" vardı (Faz 3).
- **Problem:** Kartı başka kategoriye almanın yolu yoktu.
- **Çözüm:**
  - Menüde "Move to" → diğer kategoriler; kart hedefte ilk boş uygun hücreye yerleşir.
  - Hedefte yer yoksa kart yerinde kalır; "There is no room in {ad}." uyarısı gösterilir.
  - Testin beklentisi yanlıştı: hedef kategoride iki not ilk iki satırın sol yarısını doldurduğu için ilk boş hücre
    R1C3'tür; uygulama doğruydu, testteki elle hesap düzeltildi.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`, `src/MyEverythingWidget.Presentation/BoardViewModel.cs`
- **Testler:** `UiTests` → `MoveToFromCardMenu_MovesCardToOtherCategory`
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Kırmızı aşama:** Core ve Presentation kodu testlerden hemen sonra yazıldı; kırmızı aşama ayrıca koşturulmadı. UI
  testlerinin ilk koşusunda iki test kırmızıydı (4.3 ad kutusu, 4.4 "Move to" beklentisi), yani testler davranışı
  gerçekten ölçüyor.
- **Sonuç:** Faz 4 tamamlandı (2026-10-30). Unit 128/128, UI (Sandbox) 28/28, Sonar 0 bulgu.

### Referanslar

- `MAIN_TODO.md` → Faz 4 — Kategoriler
- `PHASE3.md` → Faz 3 — Grid UI (önceki faz) · `PHASE5.md` → Faz 5 — Uygulama ekleme ve otomatik ikon (sonraki faz)
- Önceki doküman içeriği aşağıdadır; oradaki bölüm numaraları (4.1 Kapsam … 4.5 Sonuç) eski numaralardır, yukarıdaki
  alt faz numaralarıyla aynı değildir.

### Önceki doküman içeriği

> Önce: `PHASE3.md` · Sonra: `PHASE5.md` (Uygulama ekleme ve otomatik ikon)

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `WidgetBoard` kategori işlemleri | 🟢 Tamamlandı | Ekle, adlandır, sil, sırala, seç, öğe taşı |
| `BoardViewModel` sekmeleri, `CategoryViewModel` | 🟢 Tamamlandı | |
| `CategoryTabsView` (TabView) ve kart menüsünde "Move to" | 🟢 Tamamlandı | |

---

#### 4.1 Kapsam

- Sekmeler: seçme, "+" ile ekleme (ad hemen düzenlenir), sağ tık "Rename" ya da çift tık ile yeniden adlandırma.
- Silme: sağ tık "Delete". Kategoride öğe varsa onay sorar; son kategori silinemez.
- Sekmeleri sürükleyerek sıralama.
- Kartın sağ tık menüsünde "Move to" → diğer kategoriler.
- Açık sekme kaydedilir; uygulama yeniden açılınca aynı sekmeyle açılır.

---

#### 4.2 Kurallar

| Durum | Davranış |
|-------|----------|
| Kategori adı boş ya da yalnız boşluk | Ad değişmez (yeni kategoride "New category" kalır) |
| Ad 30 karakterden uzun | 30 karaktere kısaltılır |
| Son kategori silinmek istenir | Menüde "Delete" pasiftir; Core da reddeder |
| Açık sekme silinir | Solundaki sekme açılır (ilk sekmeyse yeni ilk sekme) |
| "Move to" hedef kategoride yer yok | Kart yerinde kalır; "There is no room in {ad}." uyarısı |
| Kayıtlı açık sekme artık yok (örnek: elle düzenlenmiş dosya) | İlk sekme açılır |

---

#### 4.3 Tasarım kararları

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Sekme kontrolü | WinUI `TabView`, kapat düğmesi yok | Sürükleyerek sıralama hazır; kapatma = silme olmamalı |
| Görünüm | Şerit Mica üzerinde; açık sekme ve grid ortak katman renginde (`LayerFillColorDefaultBrush`) | Windows 11 sekmeli uygulamalarıyla aynı dil |
| Ekleme | "+" sekme şeridinin sonunda; yeni sekme açılır ve ad kutusu seçili metinle gelir | Tek tıkla ekle, hemen adlandır |
| Silme onayı | Yalnız öğe varsa; varsayılan düğme "Cancel" | Boş kategoride gereksiz soru yok, dolu kategoride kazara silme yok |

---

#### 4.4 Testler

| Kabul kriteri | Test |
|---------------|------|
| Kategori kuralları (Core) | `Core.Tests` → `WidgetBoardCategoryTests` (17) |
| Sekme senkronizasyonu, uyarılar | `Presentation.Tests` → `BoardViewModelCategoryTests` (12) |
| "+" ile ekleme ve adlandırma | `UiTests` → `CategoryTests.PlusButton_CreatesNamedCategoryAndOpensIt` |
| Sekme seçimi | `UiTests` → `SelectingTab_ShowsOnlyItsCards` |
| Açık sekmenin hatırlanması | `UiTests` → `OpenTab_IsRestoredAfterRestart` |
| Yeniden adlandırma | `UiTests` → `RenameFromContextMenu_ChangesTabName` |
| Onaylı silme / vazgeçme | `UiTests` → `DeleteCategoryWithItems_AsksAndThenDeletesItAndItsItems`, `DeleteCategory_Cancelled_KeepsEverything` |
| "Move to" | `UiTests` → `MoveToFromCardMenu_MovesCardToOtherCategory` |
| Sürükleyerek sıralama (gerçek fare) | `UiTests` → `DraggingTab_ReordersCategories` |

---

#### 4.5 Sonuç

Faz 4 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`) | 128/128 |
| UI (Sandbox) | 28/28 |
| Sonar | 0 bulgu |

##### 4.5.1 Notlar

- Core ve Presentation kodu testlerden hemen sonra yazıldı; kırmızı aşama ayrıca koşturulmadı. UI testlerinin ilk
  koşusunda iki test kırmızıydı (aşağıda), yani testler davranışı gerçekten ölçüyor.
- **"+" sonrası ad kutusu açılmıyordu:** kutu, yeni sekme görsel ağaca girmeden açılmaya çalışılıyordu. Artık sekmenin
  `Loaded` olayı bekleniyor.
- **"Move to" testinin beklentisi yanlıştı:** hedef kategoride iki not ilk iki satırın sol yarısını doldurduğu için ilk
  boş hücre R1C3'tür; uygulama doğruydu, testteki elle hesap düzeltildi.
- Silme onayının "Cancel" düğmesinin otomasyon kimliği (`CloseButton`) pencerenin kapat düğmesiyle aynıdır; testler
  dialog düğmelerini `DeleteCategoryDialog` içinde arar.

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 4 — Kategoriler" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 128/128, UI 28/28 (Sandbox). Sonuç: `PHASE4.md` → 4.5 Sonuç.

**Özet:** Sekmeler: ekle, yeniden adlandır, sil, sürükleyerek sırala; öğeyi başka kategoriye taşı.

**Hedefler:**

- [x] `TabView` ile kategori sekmeleri ve "+" sekmesi
- [x] Rename (satır içi), Delete (onaylı; içindeki öğe sayısı gösterilir)
- [x] Sekmeleri sürükleyerek sıralama, tekerlekle kaydırma
- [x] Kart menüsünde "Move to" → kategori; hedef kategoride ilk boş hücreye yerleşir

**Detay:** `PHASE4.md`
