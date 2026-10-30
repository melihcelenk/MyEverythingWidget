# MEW-4 Faz 12 — Resme tıklayınca büyük hali

> Önce: `PHASE11.md`

## İçindekiler

- Durum Panosu
- 12.1 İstek (birebir)
- 12.2 Kararlar
- 12.3 Kabul kriterleri ve testler
- 12.4 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| V1 Resim kartına tıklayınca resim büyük açılır | 🟢 Tamamlandı | 12.2 |
| V2 Görüntüleyici ekrana sığar | 🟢 Tamamlandı | `ImageViewerPlacement` |
| V3 Esc, resme tıklama ya da kapat düğmesi kapatır | 🟢 Tamamlandı | 12.2 |

---

## 12.1 İstek (birebir)

> Bu resimlere tıklanınca büyük hali görülmeli.

---

## 12.2 Kararlar

- **Açılma:** Resim kartına (sürüklemeden) tıklanınca ayrı bir görüntüleme penceresi açılır (`ImageViewerWindow`).
  Uygulama kartlarına tıklamak eskisi gibi uygulamayı açar.
- **Boyut ve konum:** Widget'ın bulunduğu ekranın ortasında açılır, resmin oranını korur.
  - Pencere çalışma alanının en çok %90'ını kaplar (`ImageViewerPlacement.Fit`).
  - Bundan küçük resimler kendi boyutunda gösterilir.
  - Boyutu bilinmeyen resimler çalışma alanının yarısı kadar bir pencerede açılır.
- **Kapanma:** Esc, resme tıklama ya da sağ üstteki kapat düğmesi. Aynı anda tek görüntüleyici açık olur; widget
  kapanınca o da kapanır.
- **Görünüm:** Başlık çubuğu yok; zemin temanın temel rengi (`SolidBackgroundFillColorBase`).

---

## 12.3 Kabul kriterleri ve testler

| # | Kriter | Test |
|---|--------|------|
| V1 | 1200x600 resmin büyük hali kartın iki katından geniş, oranı 2:1 | `ImageViewerTests.ClickingImageCard_ShowsTheImageLarge`, `ImageItemViewModelTests` |
| V2 | Görüntüleyici çalışma alanının içinde; %90 sınırı, ortalama, küçük ve boyutu bilinmeyen resim | `ImageViewerTests.Viewer_FitsOnTheScreen`, `ImageViewerPlacementTests` |
| V3 | Esc görüntüleyiciyi kapatır, widget açık kalır | `ImageViewerTests.Escape_ClosesTheViewer` |

---

## 12.4 Sonuç

- **Testler:**
  - Unit: 293/293.
  - Görüntüleyici UI testleri 3/3; tam UI suite 67/67 + 1 izole test.
  - Sonar: bulgu yok.
- **Test altyapısı:**
  - Sandbox'ta masaüstünün alt pencereleri, başlatılan sürecin kimliğiyle eşleşmiyor. Bu yüzden ikinci bir pencere
    süreç kimliğiyle değil, başlığıyla bulunuyor (`AppSession.FindWindow`).
  - Uygulama çökerse `crash.log` sonuç klasörüne kopyalanıyor (`AppDataFolder.Dispose`).
