# MEW-4 Faz 11 — Boyutlandırma tutamacının oku ve kart renkleri

> Önce: `PHASE10.md`

## İçindekiler

- Durum Panosu
- 11.1 İstekler (birebir)
- 11.2 Kararlar
- 11.3 Kabul kriterleri ve testler
- 11.4 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| R1 Okun yönü ↖↘ | 🟢 Tamamlandı | 11.2 → Tutamaç |
| R2 Ok dairenin ortasında, daire küçük | 🟢 Tamamlandı | 11.2 → Tutamaç |
| R3 Tutamaç kartın tam sağ alt köşesinde | 🟢 Tamamlandı | 11.2 → Tutamaç |
| R4 Kartlar zeminden belirgin, notlar sarı | 🟢 Tamamlandı | 11.2 → Renkler |

---

## 11.1 İstekler (birebir)

> 1- O ikonun yönü yanlış
> 2- O ikon bulunduğu dairenin tam ortasında olmalı, o daire de daha küçük olmalı, dışına taşmamalı ama.
> 3- O ikonun konumu çerçevenin tam sağ alt köşesi olmalı. Şu an biraz yukarıda ve içeride kalıyor.
> 4- Her bir kart belirgin bir renkle arkaplandan ayrılmalı. Not kartları sarı olmalı.

---

## 11.2 Kararlar

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

## 11.3 Kabul kriterleri ve testler

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

## 11.4 Sonuç

- **Testler:** `CardStyleTests` 4/4; tam UI suite 64/64 + 1 izole test; Sonar bulgu yok.
