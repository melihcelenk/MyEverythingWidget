# Faz 9 — İlk kullanım geri bildirimi: tek satır başlık, hücre hücre boyut, kompakt mod, resim, emoji

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Uygulamanın ilk kullanımından gelen beş geri bildirim bu fazda karşılandı. Resim kartları resmi artık kırpmadan,
tamamıyla gösteriyor; başlık çubuğu ve sekmeler tek satıra indi. Pencere kenarından sürüklenince ızgara hücre hücre
büyüyüp küçülüyor (en az 2x2); üst çubuktaki düğmeyle widget tek hücrelik bir ikona dönüşüyor ve kart ikonunun yerine
emoji konabiliyor.

## Problem

- Resimler kartta kırpılıyordu: "Resmin kırpılmasında sorun var. Resmin tamamını görmeliyim. Ekran görüntüsünde üstteki
  resim alttan kırpılı, alttaki resim sağdan kırpılı. Bu olmamalı. Fit olmalı."
- Üst çubuk iki satırdı ve fazla yer kaplıyordu: "Soldaki Task Timer Widget ile üstteki çubuk aynı olmalı. Uygulamada
  hem dikeyde çok yer kaplıyor hem de 2 satır"
- Pencere boyutu ızgaraya bağlı değildi: "Pencere boyutu grid sayısına göre küçültülebilmeli en az 2x2 olmalı."
- Kompakt mod yoktu: "3. Resim task timer widget'ın compact modu. Açılıp kapatılabiliyor. Biz de bu widget biraz büyük
  olduğu için 1x1 grid boyutunda bir ikon haline getirip ona basarak geniş moda erişebilmeliyiz."
- Kart ikonu değiştirilemiyordu: "İkon olayı çok güzel olmuş, sadece emoji vs ile değiştirebilmeliyim"

## Çözüm

- **Resim kartı:** `Stretch="Uniform"`; resim kartın içine sığar, boş kalan kenarlar kart zemini olarak görünür.
- **Üst çubuk:** Başlık çubuğu ve sekmeler tek satır; Ayarlar düğmesi alt çubuğun sağına taşındı.
- **Pencere boyutu (`WM_SIZING`):** Kenar ya da köşe sürüklenince ızgara canlı olarak hücre hücre değişir; 2x2 ile
  10x10 arası, kartların üstüne küçülmez; boyut `settings.json` → `gridSize` içinde saklanır.
- **Kompakt mod:** Pencere çerçevesiz, tek hücrelik (80x80) bir uygulama ikonuna döner; durum `settings.json` →
  `isCompact` içinde saklanır.
- **Emoji:** Kart menüsündeki "Use emoji…" ile ikonun yerine tek bir emoji konur; "Change icon…" ya da "Reset icon"
  emojiyi kaldırır.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 9.1 | Resim kartı resmi kırpmadan, tamamıyla gösterir. | 🟢 Tamamlandı |
| 9.2 | Başlık çubuğu ve sekmeler tek satırdadır. | 🟢 Tamamlandı |
| 9.3 | Pencere hücre hücre boyutlanır ve en az 2x2 olur. | 🟢 Tamamlandı |
| 9.4 | Kompakt mod widget'ı 1x1 bir ikona çevirir. | 🟢 Tamamlandı |
| 9.5 | Kart ikonunun yerine emoji konabilir. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Görsel tasarım kararlarını kim verir? | Asistan verir | 🟢 Verildi ("zevk kararlarını sen ver") | Ayrıntılar → Önceki doküman içeriği → 9.2 Kararlar |

## Nasıl kontrol edilir

- [ ] Geniş (ör. 4:1) bir resmi 3x1 bir karta koy: resmin tamamı görünmeli, kenarlarda kart zemini kalmalı.
- [ ] Pencerenin üstüne bak: kompakt düğmesi, sekmeler, "+", pin ve kapat aynı satırda olmalı; Ayarlar düğmesi alt
  çubuğun sağında olmalı.
- [ ] Pencerenin köşesini sürükle: ızgara hücre hücre büyüyüp küçülmeli, 2x2'den küçülmemeli; uygulamayı kapatıp açınca
  aynı boyut gelmeli.
- [ ] Kartların durduğu yerin üstüne küçültmeyi dene: pencere kartlarda durmalı, hiçbir kart gizlenmemeli.
- [ ] Üst çubuğun solundaki kompakt düğmesine bas: pencere tek hücrelik ikona dönmeli; ikona tıklayınca widget aynı
  köşeden açılmalı. Kompakt halde kapatıp açınca kompakt açılmalı.
- [ ] Bir kartta sağ tık → "Use emoji…", bir emoji yaz: kartta emoji görünmeli; "Reset icon" eski ikonu geri getirmeli.

## Kalan

- Yok. Test altyapısında açık kalan iki iş (tema testi zamanlaması, performans testinin Sandbox hızına
  bağlılığı) Ayrıntılar → Doğrulanmayan / dikkat edilmesi gereken bölümünde.

## Ayrıntılar

### 9.1 — Resim kartı resmi kırpmadan, tamamıyla gösterir.

- **Mevcut durum:** Resim kartı alanı dolduracak şekilde resmi kırpıyordu; üstteki resim alttan, alttaki resim sağdan
  kırpılıyordu.
- **Problem:** Kullanıcı resmin tamamını görmek istiyor ("Fit olmalı.").
- **Çözüm:** Resim `Stretch="Uniform"` ile çiziliyor; kartın içine sığıyor, boş kalan kenarlar kart zemini olarak
  görünüyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/GridCard.xaml`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` → `WideImage_IsShownWhole` (4:1 bir resim 3x1
  kartta 4:1 oranıyla görünür)
- **Durum:** 🟢 Tamamlandı.

### 9.2 — Başlık çubuğu ve sekmeler tek satırdadır.

- **Mevcut durum:** Başlık çubuğu ve sekmeler iki ayrı satırdı ve dikeyde çok yer kaplıyordu.
- **Problem:** Kullanıcı üst çubuğun TaskTimerWidget'taki gibi tek satır ve ince olmasını istiyor.
- **Çözüm:**
  - Solda kompakt düğmesi, sekmeler ve "+", ortada sürükleme alanı, sağda pin ve kapat.
  - Ayarlar düğmesi alt çubuğun sağına taşındı; dar pencerede sekmelere yer kalsın diye.
  - Pencere başlığı ("My Everything Widget") görev çubuğunda ve erişilebilirlikte kalıyor, pencerede gösterilmiyor.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml`, `src/MyEverythingWidget.App/Views/CategoryTabsView.xaml`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` → `TitleBar_IsOneRowWithTabsAndButtons`
  (sekmeler ve kapat düğmesi aynı satırda; ızgara, pencerenin üstünden yarım hücreden az aşağıda başlar)
- **Durum:** 🟢 Tamamlandı.

### 9.3 — Pencere hücre hücre boyutlanır ve en az 2x2 olur.

- **Mevcut durum:** Pencere boyutu ızgaranın hücre sayısına bağlı değildi.
- **Problem:** Kullanıcı pencereyi ızgara hücresi sayısına göre küçültebilmek istiyor; en az 2x2.
- **Çözüm:**
  - Kenar veya köşe sürüklenince ızgara canlı olarak hücre hücre büyür/küçülür (`WM_SIZING` ile yakalanır).
  - Izgara en az 2x2, en çok 10x10 olur.
  - Pencere hiçbir kategorideki kartların üstüne küçülmez; böylece hiçbir kart gizlenmez ya da kaybolmaz. Daha da
    küçültmek için kartlar önce taşınır.
  - Izgara boyutu `settings.json` → `gridSize` içinde saklanır.
- **Dosyalar:** `src/MyEverythingWidget.App/Interop/CellSnappingResizer.cs`,
  `src/MyEverythingWidget.Core/Geometry/GridWindowSizing.cs`, `src/MyEverythingWidget.Core/State/WidgetBoard.cs`,
  `src/MyEverythingWidget.Core/Settings/AppSettings.cs`
- **Testler:**
  - `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` → `DraggingWindowCorner_ResizesGridByWholeCellsDownTo2x2AndIsRemembered`
    (köşe sürüklenince ızgara 3x3, 2x2 (alt sınır), 3x5 olur; yeniden açılınca 3x5 gelir),
    `ShrinkingWindow_StopsAtTheItems` (pencere kartların üstüne küçülmez)
  - `tests/MyEverythingWidget.Core.Tests/Geometry/GridWindowSizingTests.cs`
  - `tests/MyEverythingWidget.Core.Tests/State/WidgetBoardGridSizeTests.cs`
  - `tests/MyEverythingWidget.Core.Tests/State/LayoutPersistenceTests.cs` (5x5'ten büyük ızgaradaki kartlar yeniden
    açılınca okunur)
- **Durum:** 🟢 Tamamlandı.

### 9.4 — Kompakt mod widget'ı 1x1 bir ikona çevirir.

- **Mevcut durum:** Kompakt mod yoktu; widget her zaman tam boyutundaydı.
- **Problem:** Kullanıcı, TaskTimerWidget'ın kompakt modu gibi, widget'ı 1x1 hücrelik bir ikona çevirip ona basarak
  geniş moda dönmek istiyor.
- **Çözüm:**
  - Üst çubuğun solundaki düğme pencereyi tek hücrelik (80x80) uygulama ikonuna çevirir.
  - Kompakt pencere çerçevesizdir; Windows çerçeveli pencereyi 136 pikselden dar yapmıyor. `WM_GETMINMAXINFO` ve
    `PreferredMinimumWidth` bunu aşmadı; çerçeve ve başlık kaldırılınca (`SetBorderAndTitleBar(false, false)`) aşıldı.
  - İkon sürüklenince pencere taşınır; tıklanınca widget aynı köşeden açılır.
  - Durum `settings.json` → `isCompact` içinde saklanır; uygulama kompakt kapatıldıysa kompakt açılır.
  - Kompakt ikonun resmi ilk kullanımda dosyadan yüklenir; `ms-appx:///` açılışta kaynak yöneticisini başlatır.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`, `src/MyEverythingWidget.Presentation/MainViewModel.cs`,
  `src/MyEverythingWidget.Core/Settings/AppSettings.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` →
  `CompactMode_ShrinksToOneCellIconAndClickingItOpensTheWidget`; `tests/MyEverythingWidget.Presentation.Tests/WindowLayoutTests.cs`
  (kompakt düğmesi pencereyi tek hücreye çevirir; ikona tıklanınca aynı boyutta açılır; kompakt kapatılınca kompakt
  açılır)
- **Durum:** 🟢 Tamamlandı.

### 9.5 — Kart ikonunun yerine emoji konabilir.

- **Mevcut durum:** Kart ikonu yalnız bir dosyadan değiştirilebiliyordu.
- **Problem:** Kullanıcı ikonu emoji gibi bir şeyle değiştirebilmek istiyor.
- **Çözüm:**
  - Kart menüsünde "Use emoji…" vardır. Açılan kutuya emoji yazılır ya da Win + . ile seçilir.
  - Yalnız ilk sembol tutulur; ten rengi ve birleşik emojiler tek sembol sayılır.
  - Emoji, ikon dosyasının yerine geçer ve eski ikon dosyası silinir.
  - "Change icon…" ya da "Reset icon" emojiyi kaldırır.
  - (Faz 10'da "Use emoji…" ve "Reset icon" tek bir ikon penceresinde birleştirildi.)
- **Dosyalar:** `src/MyEverythingWidget.Core/Apps/IconEmoji.cs`, `src/MyEverythingWidget.Core/State/WidgetBoard.cs`,
  `src/MyEverythingWidget.Presentation/BoardViewModel.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` → `EmojiFromMenu_ReplacesCardIcon`;
  `tests/MyEverythingWidget.Presentation.Tests/AppIconTests.cs`, `tests/MyEverythingWidget.Core.Tests/Apps/IconEmojiTests.cs`,
  `tests/MyEverythingWidget.Core.Tests/State/WidgetBoardIconTests.cs`
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Testler:** Unit 282/282; yeni UI testleri (`WindowLayoutTests`, 6) hepsi geçti; tam UI suite 52/54 + 1 izole test.
- **Geçmeyen iki test:**
  - `Theme_DarkAndLight_RepaintWithoutRestartAndArePersisted` uzun koşuda düşüyor, tek başına geçiyor. Diyalog
    kapanırken ekran pikseli okunuyor; zamanlamaya bağlı.
  - `StartTimeAndIdleMemory_StayWithinLimits` (sınır 5 s): bu oturumda Sandbox yavaştı. Yeni kod 5,3-5,5 s ölçüldü.
    Önceki commit (`d4b37a8`) aynı koşulda 9,2 s ölçüldü, yani gerileme yok. Eski ölçüm ~2,4 s idi.
- **Açık işler (o günkü hali):**
  - Tema testindeki zamanlama kararsızlığı: piksel okumadan önce diyalog kapanış animasyonunun bitmesini beklemek.
  - Performans testinin Sandbox hızına bağlılığı: birden çok ölçümün ortancası ya da ısınma açılışı.
- **Dosya yolları:** Dosyalar alanındaki yollar bugünkü koddan eşlendi; eski doküman dosya adı vermiyordu.

### Referanslar

- `PHASE8.md` (önceki faz)
- `PHASE10.md` (sonraki faz: kompakt ikon davranışı, tek ikon penceresi)
- `MAIN_TODO.md` → 📊 Genel İlerleme → Faz 9

### Önceki doküman içeriği

Eski başlık: MEW-4 Faz 9 — İlk kullanım geri bildirimi: pencere düzeni, kompakt mod, resim ve emoji

> Önce: `PHASE8.md`

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| W1 Resim kırpılmadan sığar | 🟢 Tamamlandı | 9.2 → Resim |
| W2 Tek satırlık üst çubuk | 🟢 Tamamlandı | 9.2 → Üst çubuk |
| W3 Pencere hücre hücre boyutlanır, en az 2x2 | 🟢 Tamamlandı | 9.2 → Pencere boyutu |
| W4 Kompakt mod: 1x1 ikon | 🟢 Tamamlandı | 9.2 → Kompakt mod |
| W5 İkon yerine emoji | 🟢 Tamamlandı | 9.2 → Emoji |

---

#### 9.1 İstekler (birebir)

> 1. Resmin kırpılmasında sorun var. Resmin tamamını görmeliyim. Ekran görüntüsünde üstteki resim alttan kırpılı,
>    alttaki resim sağdan kırpılı. Bu olmamalı. Fit olmalı.
> 2. Soldaki Task Timer Widget ile üstteki çubuk aynı olmalı. Uygulamada hem dikeyde çok yer kaplıyor hem de 2 satır
> 3. Pencere boyutu grid sayısına göre küçültülebilmeli en az 2x2 olmalı.
> 4. 3. Resim task timer widget'ın compact modu. Açılıp kapatılabiliyor. Biz de bu widget biraz büyük olduğu için
>    1x1 grid boyutunda bir ikon haline getirip ona basarak geniş moda erişebilmeliyiz.
> 5. İkon olayı çok güzel olmuş, sadece emoji vs ile değiştirebilmeliyim

---

#### 9.2 Kararlar

Tasarım kararları kullanıcının "zevk kararlarını sen ver" talimatıyla verildi.

- **Resim:** `Stretch="Uniform"`; resim kartın içine sığar, boş kalan kenarlar kart zemini olarak görünür.
- **Üst çubuk:** Başlık çubuğu ve sekmeler tek satırdır: solda kompakt düğmesi, sekmeler ve "+", ortada sürükleme
  alanı, sağda pin ve kapat.
  - Ayarlar düğmesi alt çubuğun sağına taşındı; dar pencerede sekmelere yer kalsın diye.
  - Pencere başlığı ("My Everything Widget") görev çubuğunda ve erişilebilirlikte kalır, pencerede gösterilmez.
- **Pencere boyutu:**
  - Kenar veya köşe sürüklenince ızgara canlı olarak hücre hücre büyür/küçülür (`WM_SIZING` ile yakalanır).
  - Izgara en az 2x2, en çok 10x10 olur.
  - Pencere hiçbir kategorideki kartların üstüne küçülmez; böylece hiçbir kart gizlenmez ya da kaybolmaz. Daha da
    küçültmek için kartlar önce taşınır.
  - Izgara boyutu `settings.json` → `gridSize` içinde saklanır.
- **Kompakt mod:** (çerçevesiz pencere; Windows çerçeveli pencereyi 136 pikselden dar yapmıyor)
  - Üst çubuğun solundaki düğme pencereyi tek hücrelik (80x80) uygulama ikonuna çevirir.
  - İkon sürüklenince pencere taşınır; tıklanınca widget aynı köşeden açılır.
  - Durum `settings.json` → `isCompact` içinde saklanır; uygulama kompakt kapatıldıysa kompakt açılır.
- **Emoji:**
  - Kart menüsünde "Use emoji…" vardır. Açılan kutuya emoji yazılır ya da Win + . ile seçilir.
  - Yalnız ilk sembol tutulur; ten rengi ve birleşik emojiler tek sembol sayılır.
  - Emoji, ikon dosyasının yerine geçer ve eski ikon dosyası silinir.
  - "Change icon…" ya da "Reset icon" emojiyi kaldırır.

---

#### 9.3 Kabul kriterleri ve testler

| # | Kriter | Test |
|---|--------|------|
| W1 | 4:1 bir resim 3x1 kartta 4:1 oranıyla görünür | `WindowLayoutTests.WideImage_IsShownWhole` |
| W2 | Sekmeler ve kapat düğmesi aynı satırda; ızgara, pencerenin üstünden yarım hücreden az aşağıda başlar | `WindowLayoutTests.TitleBar_IsOneRowWithTabsAndButtons` |
| W3 | Köşe sürüklenince ızgara 3x3, 2x2 (alt sınır), 3x5 olur; yeniden açılınca 3x5 gelir | `WindowLayoutTests.DraggingWindowCorner_ResizesGridByWholeCellsDownTo2x2AndIsRemembered`, `GridWindowSizingTests`, `WidgetBoardGridSizeTests` |
| W3 | Pencere kartların üstüne küçülmez | `WindowLayoutTests.ShrinkingWindow_StopsAtTheItems`, `WidgetBoardGridSizeTests` |
| W3 | 5x5'ten büyük ızgaradaki kartlar yeniden açılınca okunur | `LayoutPersistenceTests` |
| W4 | Kompakt düğmesi pencereyi tek hücreye çevirir; ikona tıklanınca aynı boyutta açılır; kompakt kapatılınca kompakt açılır | `WindowLayoutTests.CompactMode_ShrinksToOneCellIconAndClickingItOpensTheWidget`, `WindowLayoutTests` (Presentation) |
| W5 | "Use emoji…" kartta emojiyi gösterir ve saklar; "Reset icon" geri alır | `WindowLayoutTests.EmojiFromMenu_ReplacesCardIcon`, `AppIconTests`, `IconEmojiTests`, `WidgetBoardIconTests` |

---

#### 9.4 Sonuç

- **Testler:**
  - Unit: 282/282.
  - Yeni UI testleri (`WindowLayoutTests`, 6): hepsi geçti.
  - Tam UI suite: 52/54 + 1 izole test.
- **Geçmeyen iki test:**
  - `Theme_DarkAndLight_RepaintWithoutRestartAndArePersisted` uzun koşuda düşüyor, tek başına geçiyor. Diyalog kapanırken
    ekran pikseli okunuyor; zamanlamaya bağlı.
  - `StartTimeAndIdleMemory_StayWithinLimits` (sınır 5 s): bu oturumda Sandbox yavaştı. Yeni kod 5,3-5,5 s ölçüldü.
    Önceki commit (`d4b37a8`) aynı koşulda 9,2 s ölçüldü, yani gerileme yok. Eski ölçüm ~2,4 s idi.
- **Öğrenilenler:**
  - Windows, çerçeveli pencereyi 136 pikselden dar yapmıyor. `WM_GETMINMAXINFO` ve `PreferredMinimumWidth` bunu
    aşmadı; kompakt modda çerçeve ve başlık kaldırılınca (`SetBorderAndTitleBar(false, false)`) aşıldı.
  - Kompakt ikonun resmi ilk kullanımda dosyadan yüklenir; `ms-appx:///` açılışta kaynak yöneticisini başlatır.

#### 9.5 Açık işler

- Tema testindeki zamanlama kararsızlığı: piksel okumadan önce diyalog kapanış animasyonunun bitmesini beklemek.
- Performans testinin Sandbox hızına bağlılığı: birden çok ölçümün ortancası ya da ısınma açılışı.
