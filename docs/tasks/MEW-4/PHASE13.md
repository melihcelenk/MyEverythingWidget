# Faz 13 — İkon penceresi: Select icon / Select image sekmeleri

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

İkon penceresinin üstünde artık iki sekme var: "Select icon" emoji ızgarasını, "Select image" ise resim seçme alanını
gösteriyor. Resim "Browse…" ile seçilebiliyor, alana sürüklenebiliyor ya da Ctrl+V ile yapıştırılabiliyor.
"Reset to original" ve "Cancel" pencerenin alt çubuğunda, Reset Cancel'ın solunda duruyor ve widget ne kadar küçük
olursa olsun görünür kalıyor.

## Problem

- Kullanıcının isteği (birebir): "Küçültünce bir şey görünmüyor. Yani şöyle olabilir: Change icon'un yerine Select
  icon yaz, bu bir sekme olsun, Select Image yaz bu da başka bir sekme olsun. O sekmeler arasında geçiş yapılabilsin.
  Reset to Original Cancel'ın soluna gelsin. Image seçme tarafında gözat olduğu gibi resim sürükleme veya ctrl v ile
  direkt yapıştırma da olsun."
- Faz 10'daki pencerede "Image…" ve "Reset to original" emoji ızgarasının altındaydı. Pencere widget'tan büyük
  olamadığı için küçük widget'ta ızgaranın alt satırları ve bu iki düğme kesiliyordu.
- Testler bunu yakalamadı: düğmelere UI Automation ile basıyorlardı, ekranda görünüp görünmediklerine bakmıyorlardı.

## Çözüm

- **Sekmeler (`SelectorBar`):** Pencere başlığı yerine "Select icon" ve "Select image" sekmeleri; pencere
  "Select icon" ile açılır.
- **Select icon:** 56 emojilik ızgara; sığmazsa kaydırılır, tıklanan emoji uygulanır ve pencere kapanır.
- **Select image:** Kesik kenarlı bırakma alanı, "Browse…" düğmesi, sürükle-bırak ve Ctrl+V; resim olmayan veride
  "That is not an image." yazar.
- **Alt çubuk:** `Reset to original` · `Cancel` diyaloğun kendi düğmeleri olduğu için her boyutta görünür.
- **Ana pencere:** İkon penceresi açıkken ana pencerenin Ctrl+V'si çalışmaz.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 13.1 | İkon penceresinde "Select icon" ve "Select image" sekmeleri vardır ve aralarında geçilebilir. | 🟢 Tamamlandı |
| 13.2 | "Reset to original" Cancel'ın solundadır ve her boyutta görünür. | 🟢 Tamamlandı |
| 13.3 | Resim Browse, sürükle-bırak ya da Ctrl+V ile ikon yapılabilir. | 🟢 Tamamlandı (gerçek sürükle-bırak elle denenmeli) |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| İkon penceresi: iki sekmeli düzen doğru anlaşıldı mı? | A | 🟢 Verildi: A | S5 (`questions/S05-ikon-penceresi-sekmeler.md`) |

## Nasıl kontrol edilir

- [ ] Widget'ı en küçük boyuta (2x2) getir, bir karta sağ tıkla → "Change icon…": iki sekme, "Reset to original" ve
  "Cancel" ekranda görünmeli; Reset, Cancel'ın solunda olmalı.
- [ ] "Select image" sekmesine geç: "Browse…" düğmesi ve bırakma alanı görünmeli; "Select icon"a dönünce emoji
  ızgarası geri gelmeli.
- [ ] Bir ekran görüntüsü al, "Select image" sekmesinde Ctrl+V yap: resim kartın ikonu olmalı, pencere kapanmalı,
  ızgaraya ayrı bir kart eklenmemeli.
- [ ] Explorer'dan bir `.png` dosyasını bırakma alanına sürükle: resim ikon olmalı.
- [ ] Resim olmayan bir dosyayı bırak: alanda "That is not an image." yazmalı.
- [ ] "Select icon" sekmesinde bir emojiye tıkla: kartın ikonu o emoji olmalı ve pencere kapanmalı.

## Kalan

- Yok.

## Ayrıntılar

### 13.1 — İkon penceresinde "Select icon" ve "Select image" sekmeleri vardır ve aralarında geçilebilir.

- **Mevcut durum:** Faz 10'daki pencerede başlık "Change icon" idi; "Image…" ve "Reset to original" emoji ızgarasının
  altındaydı.
- **Problem:** Küçük widget'ta ızgaranın alt satırları ve bu iki düğme kesiliyordu: "Küçültünce bir şey görünmüyor."
- **Çözüm:**
  - Pencere başlığı yerine `SelectorBar` ile iki sekme var: "Select icon" ve "Select image". Pencere "Select icon" ile
    açılır.
  - Select icon: 56 emojilik ızgara. Pencereye sığmazsa kaydırılır; tıklanan emoji uygulanır ve pencere kapanır.
  - Kart menüsünde öğenin adı "Change icon…" olarak kaldı.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/IconPickerDialog.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` →
  `IconDialog_InSmallestWindow_KeepsTabsResetAndCancelVisible`, `SelectImageTab_OffersBrowseAndDropArea` ("Select
  image" sekmesi Browse düğmesini ve bırakma alanını gösterir, emoji ızgarasını gizler; geri dönünce ızgara görünür),
  `EmojiPickedInIconDialog_ReplacesCardIcon` (emoji seçimi ve iki sekmenin varlığı)
- **Durum:** 🟢 Tamamlandı.

### 13.2 — "Reset to original" Cancel'ın solundadır ve her boyutta görünür.

- **Mevcut durum:** "Reset to original" emoji ızgarasının altındaydı ve küçük widget'ta kesiliyordu.
- **Problem:** Kullanıcı Reset'in Cancel'ın soluna gelmesini istedi; düğme her boyutta görünür olmalı.
- **Çözüm:** Alt çubukta `Reset to original` · `Cancel` var. Bunlar diyaloğun kendi düğmeleri olduğu için pencere ne
  kadar küçülürse küçülsün görünür kalır.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/IconPickerDialog.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` →
  `IconDialog_InSmallestWindow_KeepsTabsResetAndCancelVisible` (en küçük (2x2) widget'ta iki sekme, Reset ve Cancel
  ekranda ve pencerenin içinde; Reset, Cancel'ın solunda; gerçek tıklamayla Reset çalışır)
- **Durum:** 🟢 Tamamlandı.

### 13.3 — Resim Browse, sürükle-bırak ya da Ctrl+V ile ikon yapılabilir.

- **Mevcut durum:** Resim yalnız "Image…" düğmesiyle (gözat) seçilebiliyordu.
- **Problem:** Kullanıcı gözatın yanında resim sürükleme ve Ctrl+V ile doğrudan yapıştırma da istedi.
- **Çözüm:**
  - Kesik kenarlı bir alanda "Drop an image here or paste it with Ctrl+V" yazısı ve "Browse…" düğmesi var.
  - Kabul edilenler: sürüklenen ya da panodaki resim (ekran görüntüsü gibi) ve resim dosyası (`.png`, `.jpg`, `.gif`,
    `.bmp`, `.ico`, `.webp`, `.tif`).
  - Gelen veri resim olarak çözülebiliyorsa ikon yapılır ve pencere kapanır; çözülemiyorsa alanda "That is not an
    image." yazar.
  - Bırakılan dosya, Ctrl+V ile yapıştırılan dosyayla aynı kod yolundan geçiyor (`ReadImageAsync`).
  - Ctrl+V çakışması: İkon penceresi açıkken ana pencerenin Ctrl+V'si çalışmaz. Böylece yapıştırılan resim ızgaraya
    ayrı bir kart olarak eklenmez.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/IconPickerDialog.cs`, `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` → `PastedPicture_InSelectImageTab_BecomesTheIcon`
  (panodaki resim Ctrl+V ile ikon olur, pencere kapanır, ızgaraya kart eklenmez),
  `PastedImageFile_InSelectImageTab_BecomesTheIcon` (panodaki resim dosyası Ctrl+V ile ikon olur)
- **Durum:** 🟢 Tamamlandı (gerçek sürükle-bırak elle denenmeli).

### Doğrulanmayan / dikkat edilmesi gereken

- **Gerçek sürükle-bırak:** Explorer'dan sürükle-bırak Sandbox'ta otomatik test edilemiyor. Bırakılan dosya, Ctrl+V
  ile yapıştırılan dosyayla aynı kod yolundan geçiyor (`ReadImageAsync`); o yol test edildi.
- **Sonar:** Bu turda çalıştırılamadı; IDE bu dosyaları tanımıyordu. Derleme uyarı vermeden geçti
  (`TreatWarningsAsErrors`).
- **Testler:** `WindowLayoutTests` 10/10 (Sandbox'ta gerçek fare ve klavyeyle); tam UI suite 71/71 + 1 izole test.
- **Dosya yolları:** Eski doküman dosya adı vermiyordu; Dosyalar satırları koddaki sınıf adlarından eklendi.

### Referanslar

- `questions/S05-ikon-penceresi-sekmeler.md` → Cevap (A)
- `PHASE12.md` (önceki faz)
- `PHASE14.md` (ikon penceresinin geç açılması)
- `PHASE15.md` → Ayrıntılar (aynı pano okuma yolu)
- `MAIN_TODO.md` → 📊 Genel İlerleme → Faz 13

### Önceki doküman içeriği

> Önce: `PHASE12.md` · Karar: `questions/S05-ikon-penceresi-sekmeler.md` (A)

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| T1 "Select icon" ve "Select image" sekmeleri, aralarında geçiş | 🟢 Tamamlandı | 13.3 |
| T2 "Reset to original" Cancel'ın solunda, her boyutta görünür | 🟢 Tamamlandı | 13.3 |
| T3 Resim: Browse, sürükle-bırak, Ctrl+V | 🟢 Tamamlandı | 13.3 |

---

#### 13.1 İstek (birebir)

> Küçültünce bir şey görünmüyor. Yani şöyle olabilir: Change icon'un yerine Select icon yaz, bu bir sekme olsun,
> Select Image yaz bu da başka bir sekme olsun. O sekmeler arasında geçiş yapılabilsin. Reset to Original Cancel'ın
> soluna gelsin. Image seçme tarafında gözat olduğu gibi resim sürükleme veya ctrl v ile direkt yapıştırma da olsun.

---

#### 13.2 Sorun

- **Ne oluyordu:** Faz 10'daki pencerede "Image…" ve "Reset to original" emoji ızgarasının altındaydı. Pencere
  widget'tan büyük olamadığı için küçük widget'ta ızgaranın alt satırları ve bu iki düğme kesiliyordu.
- **Testler neden yakalamadı:** Düğmelere UI Automation ile basıyorlardı, ekranda görünüp görünmediklerine
  bakmıyorlardı.

---

#### 13.3 Kararlar

- **Sekmeler:** Pencere başlığı yerine `SelectorBar` ile iki sekme var: "Select icon" ve "Select image". Pencere
  "Select icon" ile açılır.
- **Select icon:** 56 emojilik ızgara. Pencereye sığmazsa kaydırılır; tıklanan emoji uygulanır ve pencere kapanır.
- **Select image:**
  - Kesik kenarlı bir alanda "Drop an image here or paste it with Ctrl+V" yazısı ve "Browse…" düğmesi var.
  - Kabul edilenler: sürüklenen ya da panodaki resim (ekran görüntüsü gibi) ve resim dosyası (`.png`, `.jpg`, `.gif`,
    `.bmp`, `.ico`, `.webp`, `.tif`).
  - Gelen veri resim olarak çözülebiliyorsa ikon yapılır ve pencere kapanır; çözülemiyorsa alanda "That is not an
    image." yazar.
- **Alt çubuk:** `Reset to original` · `Cancel`. Bunlar diyaloğun kendi düğmeleri olduğu için pencere ne kadar
  küçülürse küçülsün görünür kalır.
- **Kart menüsü:** öğenin adı "Change icon…" olarak kaldı.
- **Ctrl+V çakışması:** İkon penceresi açıkken ana pencerenin Ctrl+V'si çalışmaz. Böylece yapıştırılan resim ızgaraya
  ayrı bir kart olarak eklenmez.

---

#### 13.4 Kabul kriterleri ve testler

Hepsi `WindowLayoutTests` içinde, Sandbox'ta gerçek fare ve klavyeyle.

| # | Kriter | Test |
|---|--------|------|
| T1, T2 | En küçük (2x2) widget'ta iki sekme, Reset ve Cancel ekranda ve pencerenin içinde; Reset, Cancel'ın solunda; gerçek tıklamayla Reset çalışır | `IconDialog_InSmallestWindow_KeepsTabsResetAndCancelVisible` |
| T1 | "Select image" sekmesi Browse düğmesini ve bırakma alanını gösterir, emoji ızgarasını gizler; geri dönünce ızgara görünür | `SelectImageTab_OffersBrowseAndDropArea` |
| T3 | Panodaki resim Ctrl+V ile ikon olur, pencere kapanır, ızgaraya kart eklenmez | `PastedPicture_InSelectImageTab_BecomesTheIcon` |
| T3 | Panodaki resim dosyası (sürükle-bırakla aynı yol) Ctrl+V ile ikon olur | `PastedImageFile_InSelectImageTab_BecomesTheIcon` |
| — | Emoji seçimi ve iki sekmenin varlığı | `EmojiPickedInIconDialog_ReplacesCardIcon` |

Explorer'dan gerçek sürükle-bırak Sandbox'ta otomatik test edilemiyor. Bırakılan dosya, Ctrl+V ile yapıştırılan
dosyayla aynı kod yolundan geçiyor (`ReadImageAsync`).

---

#### 13.5 Sonuç

- **Testler:** `WindowLayoutTests` 10/10; tam UI suite 71/71 + 1 izole test.
- **Sonar:** Bu turda çalıştırılamadı; IDE bu dosyaları tanımıyordu. Derleme uyarı vermeden geçti
  (`TreatWarningsAsErrors`).
