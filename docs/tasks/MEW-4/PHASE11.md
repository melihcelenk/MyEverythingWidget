# Faz 11 — Boyutlandırma tutamacının oku ve kart renkleri

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Kartın sağ altındaki boyutlandırma tutamacı düzeltildi: ok artık doğru yönü (↖↘) gösteriyor, küçük dairenin tam
ortasında duruyor ve daire kartın tam sağ alt köşesine oturuyor. Kartlar da zeminden belirgin biçimde ayrılıyor; not
kartları sarı. Bütün renkler tema kaynaklarından geliyor, koyu ve açık temada ayrı tonlar var.

## Problem

- Okun yönü yanlıştı: "O ikonun yönü yanlış"
- Ok ortada değildi, daire büyüktü: "O ikon bulunduğu dairenin tam ortasında olmalı, o daire de daha küçük olmalı,
  dışına taşmamalı ama."
- Tutamaç köşede değildi: "O ikonun konumu çerçevenin tam sağ alt köşesi olmalı. Şu an biraz yukarıda ve içeride
  kalıyor."
- Kartlar zeminden ayrılmıyordu: "Her bir kart belirgin bir renkle arkaplandan ayrılmalı. Not kartları sarı olmalı."

## Çözüm

- **Tutamaç oku:** ↖↘ çift ok; 12x12'lik iç alanda merkeze (6,6) göre simetrik, `Stretch="None"`.
- **Tutamaç dairesi:** 14 piksel, köşeden 1 piksel içeride; kartın yuvarlak köşesinin içine oturuyor.
- **Renkler:** Zemin `SolidBackgroundFillColorSecondary`, uygulama ve resim kartları `SolidBackgroundFillColorQuarternary`,
  not kartları `SystemFillColorCautionBackground`; sabit renk yok.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 11.1 | Tutamacın oku ↖↘ yönünü gösterir. | 🟢 Tamamlandı |
| 11.2 | Ok küçük dairenin tam ortasındadır. | 🟢 Tamamlandı |
| 11.3 | Tutamaç kartın tam sağ alt köşesinde durur. | 🟢 Tamamlandı |
| 11.4 | Kartlar zeminden belirgin ayrılır ve not kartları sarıdır. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- [ ] Bir kartın üzerine gel: sağ alttaki tutamacın oku sol üstten sağ alta (↖↘) uzanmalı.
- [ ] Tutamaca yakından bak: ok dairenin ortasında olmalı, dairenin dışına taşmamalı; daire küçük olmalı.
- [ ] Tutamaç kartın çerçevesinin tam sağ alt köşesinde, yuvarlak köşenin içinde durmalı.
- [ ] Koyu ve açık temada bak: uygulama ve resim kartları zeminden belirgin ayrılmalı, not kartları sarı olmalı.

## Kalan

- Yok.

## Ayrıntılar

### 11.1 — Tutamacın oku ↖↘ yönünü gösterir.

- **Mevcut durum:** Ok ↗↙ yönündeydi.
- **Problem:** "O ikonun yönü yanlış" — kartın sağ alt köşesinden boyutlandırma ↖↘ yönündedir.
- **Çözüm:** Ok ↖↘ çift ok olarak çiziliyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/ResizeGrip.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CardStyleTests.cs` → `ResizeGrip_ArrowPointsTopLeftToBottomRight` (ok
  piksellerinin x/y kovaryansı pozitif (↖↘); eski ok −2,75 veriyordu). İlk yazılan yön testi, farkın mutlak değerine
  baktığı için yanlış oku da kabul ediyordu; yeşil faza geçmeden önce kovaryans ölçümüyle değiştirildi.
- **Durum:** 🟢 Tamamlandı.

### 11.2 — Ok küçük dairenin tam ortasındadır.

- **Mevcut durum:** Daire 20 pikseldi ve ok ortada değildi.
- **Problem:** Ok dairenin tam ortasında olmalı, daire daha küçük olmalı ama ok dışına taşmamalı.
- **Çözüm:**
  - Daire 14 piksel.
  - Ok dairenin 12x12'lik iç alanında, merkeze (6,6) göre simetrik çiziliyor. `Stretch="None"`, yani ölçeklenmiyor ve
    kaymıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/ResizeGrip.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CardStyleTests.cs` → `ResizeGrip_SitsInTheCardsBottomRightCorner_AndIsSmall`
  (genişliği hücrenin %20'sinden küçük)
- **Durum:** 🟢 Tamamlandı.

### 11.3 — Tutamaç kartın tam sağ alt köşesinde durur.

- **Mevcut durum:** 20 piksellik daire köşeden 3 piksel içeride duruyordu; biraz yukarıda ve içeride kalıyordu.
- **Problem:** Tutamaç çerçevenin tam sağ alt köşesinde olmalı.
- **Çözüm:** Daire köşeden 1 piksel içeride; kartın yuvarlak köşesinin içine oturuyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/GridCard.xaml`, `src/MyEverythingWidget.App/Views/ResizeGrip.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CardStyleTests.cs` → `ResizeGrip_SitsInTheCardsBottomRightCorner_AndIsSmall`
  (tutamacın sağ ve alt kenarı kartın kenarına en çok 2 piksel)
- **Durum:** 🟢 Tamamlandı.

### 11.4 — Kartlar zeminden belirgin ayrılır ve not kartları sarıdır.

- **Mevcut durum:** Kartlar zeminden belirgin bir renkle ayrılmıyordu; not kartları diğerleriyle aynı renkteydi.
- **Problem:** "Her bir kart belirgin bir renkle arkaplandan ayrılmalı. Not kartları sarı olmalı."
- **Çözüm:** Tümü tema kaynaklarından; sabit renk yok.
  - Zemin ve seçili sekme: `SolidBackgroundFillColorSecondary` (koyu #1C1C1C, açık #EEEEEE).
  - Uygulama ve resim kartları: `SolidBackgroundFillColorQuarternary` (koyu #2C2C2C, açık #FFFFFF).
  - Not kartları: `SystemFillColorCautionBackground` (koyu #433519, açık #FFF4CE).
- **Dosyalar:** `src/MyEverythingWidget.App/Views/GridCard.xaml`, `src/MyEverythingWidget.App/MainWindow.xaml`,
  `src/MyEverythingWidget.App/Views/CategoryTabsView.xaml`
- **Testler:** `tests/MyEverythingWidget.UiTests/CardStyleTests.cs` → `NoteCard_IsYellow` (not kartında R−B > 25 ve
  G−B > 15), `AppCard_StandsOutFromTheSurface` (uygulama kartı ile zeminin parlaklık farkı > 12)
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Ölçüm:** Bütün kabul testleri `CardStyleTests` içinde; değerler ekran pikselinden okunuyor.
- **Testler:** `CardStyleTests` 4/4; tam UI suite 64/64 + 1 izole test; Sonar bulgu yok.
- **Dosya yolları:** Dosyalar alanındaki yollar bugünkü koddan eşlendi; eski doküman dosya adı vermiyordu.

### Referanslar

- `PHASE10.md` (önceki faz; tutamaç rozeti ve çift oklu imleç)
- `MAIN_TODO.md` → 📊 Genel İlerleme → Faz 11

### Önceki doküman içeriği

Eski başlık: MEW-4 Faz 11 — Boyutlandırma tutamacının oku ve kart renkleri

> Önce: `PHASE10.md`

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| R1 Okun yönü ↖↘ | 🟢 Tamamlandı | 11.2 → Tutamaç |
| R2 Ok dairenin ortasında, daire küçük | 🟢 Tamamlandı | 11.2 → Tutamaç |
| R3 Tutamaç kartın tam sağ alt köşesinde | 🟢 Tamamlandı | 11.2 → Tutamaç |
| R4 Kartlar zeminden belirgin, notlar sarı | 🟢 Tamamlandı | 11.2 → Renkler |

---

#### 11.1 İstekler (birebir)

> 1- O ikonun yönü yanlış
> 2- O ikon bulunduğu dairenin tam ortasında olmalı, o daire de daha küçük olmalı, dışına taşmamalı ama.
> 3- O ikonun konumu çerçevenin tam sağ alt köşesi olmalı. Şu an biraz yukarıda ve içeride kalıyor.
> 4- Her bir kart belirgin bir renkle arkaplandan ayrılmalı. Not kartları sarı olmalı.

---

#### 11.2 Kararlar

- **Tutamaç:**
  - **Önceki hali:** ok ↗↙ yönündeydi; 20 piksellik daire köşeden 3 piksel içeride duruyordu.
  - **Daire:** 14 piksel, köşeden 1 piksel içeride; kartın yuvarlak köşesinin içine oturuyor.
  - **Ok:** ↖↘ çift ok. Dairenin 12x12'lik iç alanında, merkeze (6,6) göre simetrik çiziliyor. `Stretch="None"`, yani
    ölçeklenmiyor ve kaymıyor.
- **Renkler:** Tümü tema kaynaklarından; sabit renk yok.

| Öğe | Kaynak | Koyu | Açık |
|-----|--------|------|------|
| Zemin ve seçili sekme | `SolidBackgroundFillColorSecondary` | #1C1C1C | #EEEEEE |
| Uygulama ve resim kartları | `SolidBackgroundFillColorQuarternary` | #2C2C2C | #FFFFFF |
| Not kartları | `SystemFillColorCautionBackground` | #433519 | #FFF4CE |

---

#### 11.3 Kabul kriterleri ve testler

Hepsi `CardStyleTests` içinde; değerler ekran pikselinden okunuyor.

| # | Kriter | Test |
|---|--------|------|
| R1 | Ok piksellerinin x/y kovaryansı pozitif (↖↘); eski ok −2,75 veriyordu | `ResizeGrip_ArrowPointsTopLeftToBottomRight` |
| R2, R3 | Tutamacın sağ ve alt kenarı kartın kenarına en çok 2 piksel; genişliği hücrenin %20'sinden küçük | `ResizeGrip_SitsInTheCardsBottomRightCorner_AndIsSmall` |
| R4 | Not kartında R−B > 25 ve G−B > 15 (sarı) | `NoteCard_IsYellow` |
| R4 | Uygulama kartı ile zeminin parlaklık farkı > 12 | `AppCard_StandsOutFromTheSurface` |

İlk yazılan yön testi, farkın mutlak değerine baktığı için yanlış oku da kabul ediyordu. Yeşil faza geçmeden önce
kovaryans ölçümüyle değiştirildi.

---

#### 11.4 Sonuç

- **Testler:** `CardStyleTests` 4/4; tam UI suite 64/64 + 1 izole test; Sonar bulgu yok.
