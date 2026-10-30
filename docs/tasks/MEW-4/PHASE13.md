# MEW-4 Faz 13 — İkon penceresi: "Select icon" / "Select image" sekmeleri

> Önce: `PHASE12.md` · Karar: `questions/S05-ikon-penceresi-sekmeler.md` (A)

## İçindekiler

- Durum Panosu
- 13.1 İstek (birebir)
- 13.2 Sorun
- 13.3 Kararlar
- 13.4 Kabul kriterleri ve testler
- 13.5 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| T1 "Select icon" ve "Select image" sekmeleri, aralarında geçiş | 🟢 Tamamlandı | 13.3 |
| T2 "Reset to original" Cancel'ın solunda, her boyutta görünür | 🟢 Tamamlandı | 13.3 |
| T3 Resim: Browse, sürükle-bırak, Ctrl+V | 🟢 Tamamlandı | 13.3 |

---

## 13.1 İstek (birebir)

> Küçültünce bir şey görünmüyor. Yani şöyle olabilir: Change icon'un yerine Select icon yaz, bu bir sekme olsun,
> Select Image yaz bu da başka bir sekme olsun. O sekmeler arasında geçiş yapılabilsin. Reset to Original Cancel'ın
> soluna gelsin. Image seçme tarafında gözat olduğu gibi resim sürükleme veya ctrl v ile direkt yapıştırma da olsun.

---

## 13.2 Sorun

- **Ne oluyordu:** Faz 10'daki pencerede "Image…" ve "Reset to original" emoji ızgarasının altındaydı. Pencere
  widget'tan büyük olamadığı için küçük widget'ta ızgaranın alt satırları ve bu iki düğme kesiliyordu.
- **Testler neden yakalamadı:** Düğmelere UI Automation ile basıyorlardı, ekranda görünüp görünmediklerine
  bakmıyorlardı.

---

## 13.3 Kararlar

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

## 13.4 Kabul kriterleri ve testler

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

## 13.5 Sonuç

- **Testler:** `WindowLayoutTests` 10/10; tam UI suite 71/71 + 1 izole test.
- **Sonar:** Bu turda çalıştırılamadı; IDE bu dosyaları tanımıyordu. Derleme uyarı vermeden geçti
  (`TreatWarningsAsErrors`).
