# MEW-4 Faz 9 — İlk kullanım geri bildirimi: pencere düzeni, kompakt mod, resim ve emoji

> Önce: `PHASE8.md`

## İçindekiler

- Durum Panosu
- 9.1 İstekler (birebir)
- 9.2 Kararlar
- 9.3 Kabul kriterleri ve testler
- 9.4 Sonuç
- 9.5 Açık işler

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| W1 Resim kırpılmadan sığar | 🟢 Tamamlandı | 9.2 → Resim |
| W2 Tek satırlık üst çubuk | 🟢 Tamamlandı | 9.2 → Üst çubuk |
| W3 Pencere hücre hücre boyutlanır, en az 2x2 | 🟢 Tamamlandı | 9.2 → Pencere boyutu |
| W4 Kompakt mod: 1x1 ikon | 🟢 Tamamlandı | 9.2 → Kompakt mod |
| W5 İkon yerine emoji | 🟢 Tamamlandı | 9.2 → Emoji |

---

## 9.1 İstekler (birebir)

> 1. Resmin kırpılmasında sorun var. Resmin tamamını görmeliyim. Ekran görüntüsünde üstteki resim alttan kırpılı,
>    alttaki resim sağdan kırpılı. Bu olmamalı. Fit olmalı.
> 2. Soldaki Task Timer Widget ile üstteki çubuk aynı olmalı. Uygulamada hem dikeyde çok yer kaplıyor hem de 2 satır
> 3. Pencere boyutu grid sayısına göre küçültülebilmeli en az 2x2 olmalı.
> 4. 3. Resim task timer widget'ın compact modu. Açılıp kapatılabiliyor. Biz de bu widget biraz büyük olduğu için
>    1x1 grid boyutunda bir ikon haline getirip ona basarak geniş moda erişebilmeliyiz.
> 5. İkon olayı çok güzel olmuş, sadece emoji vs ile değiştirebilmeliyim

---

## 9.2 Kararlar

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

## 9.3 Kabul kriterleri ve testler

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

## 9.4 Sonuç

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

## 9.5 Açık işler

- Tema testindeki zamanlama kararsızlığı: piksel okumadan önce diyalog kapanış animasyonunun bitmesini beklemek.
- Performans testinin Sandbox hızına bağlılığı: birden çok ölçümün ortancası ya da ısınma açılışı.
