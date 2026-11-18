# Faz 12 — Resme tıklayınca büyük hali

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Bir resim kartına tıklayınca resim ayrı bir pencerede büyük olarak açılıyor. Pencere widget'ın bulunduğu ekranın
ortasında, resmin oranını koruyarak ve ekrana sığacak boyutta açılıyor. Esc, resme tıklama ya da sağ üstteki kapat
düğmesi pencereyi kapatıyor; uygulama kartlarına tıklamak eskisi gibi uygulamayı açıyor.

## Problem

- Resim kartlarındaki resimler yalnız kart boyutunda görülebiliyordu; büyük halini açmanın yolu yoktu.
- Gereksinim: Resim kartlarındaki resimlere tıklanınca resmin büyük hali görüntülenmeli.

## Çözüm

- **Görüntüleyici (`ImageViewerWindow`):** Resim kartına (sürüklemeden) tıklanınca ayrı bir görüntüleme penceresi
  açılır; başlık çubuğu yoktur, zemin temanın temel rengidir (`SolidBackgroundFillColorBase`).
- **Yerleşim (`ImageViewerPlacement`):** Pencere çalışma alanının en çok %90'ını kaplar, ekranın ortasında durur ve
  resmin oranını korur.
- **Kapanma:** Esc, resme tıklama ya da kapat düğmesi; aynı anda tek görüntüleyici açık olur, widget kapanınca o da
  kapanır.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 12.1 | Resim kartına tıklayınca resim büyük açılır. | 🟢 Tamamlandı |
| 12.2 | Görüntüleyici ekrana sığar. | 🟢 Tamamlandı |
| 12.3 | Esc, resme tıklama ya da kapat düğmesi görüntüleyiciyi kapatır. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- [ ] Bir resim kartına tıkla: resim ayrı bir pencerede, karttan çok daha büyük ve aynı oranda açılmalı.
- [ ] Ekrandan büyük bir resim aç: pencere ekranın içinde ve ortasında kalmalı.
- [ ] Küçük bir resim aç: kendi boyutunda gösterilmeli, büyütülmemeli.
- [ ] Görüntüleyicide Esc'ye bas: görüntüleyici kapanmalı, widget açık kalmalı.
- [ ] Görüntüleyiciyi açıp resme tıkla, sonra tekrar açıp sağ üstteki kapat düğmesine bas: iki durumda da kapanmalı.
- [ ] Bir uygulama kartına tıkla: eskisi gibi uygulama açılmalı.

## Kalan

- Yok.

## Ayrıntılar

### 12.1 — Resim kartına tıklayınca resim büyük açılır.

- **Mevcut durum:** Resim yalnız kart boyutunda görülüyordu; büyük halini açmanın yolu yoktu.
- **Problem:** Resim kartlarındaki resimlere tıklanınca resmin büyük hali görüntülenmeli.
- **Çözüm:**
  - Resim kartına (sürüklemeden) tıklanınca ayrı bir görüntüleme penceresi açılıyor (`ImageViewerWindow`).
  - Uygulama kartlarına tıklamak eskisi gibi uygulamayı açıyor.
  - Başlık çubuğu yok; zemin temanın temel rengi (`SolidBackgroundFillColorBase`).
- **Dosyalar:** `src/MyEverythingWidget.App/Views/ImageViewerWindow.cs`
- **Testler:** `ImageViewerTests.ClickingImageCard_ShowsTheImageLarge` (1200x600 resmin büyük hali kartın iki katından
  geniş, oranı 2:1), `ImageItemViewModelTests`
- **Durum:** 🟢 Tamamlandı.

### 12.2 — Görüntüleyici ekrana sığar.

- **Mevcut durum:** Görüntüleyici yoktu.
- **Problem:** Büyük bir resim ekrandan taşmamalı, küçük bir resim gereksiz büyütülmemeli.
- **Çözüm:**
  - Pencere widget'ın bulunduğu ekranın ortasında açılıyor, resmin oranını koruyor.
  - Pencere çalışma alanının en çok %90'ını kaplıyor (`ImageViewerPlacement.Fit`).
  - Bundan küçük resimler kendi boyutunda gösteriliyor.
  - Boyutu bilinmeyen resimler çalışma alanının yarısı kadar bir pencerede açılıyor.
- **Dosyalar:** `src/MyEverythingWidget.Core/Geometry/ImageViewerPlacement.cs`,
  `src/MyEverythingWidget.App/Views/ImageViewerWindow.cs`
- **Testler:** `ImageViewerTests.Viewer_FitsOnTheScreen`, `ImageViewerPlacementTests` (görüntüleyici çalışma alanının
  içinde; %90 sınırı, ortalama, küçük ve boyutu bilinmeyen resim)
- **Durum:** 🟢 Tamamlandı.

### 12.3 — Esc, resme tıklama ya da kapat düğmesi görüntüleyiciyi kapatır.

- **Mevcut durum:** Görüntüleyici yoktu.
- **Problem:** Başlık çubuğu olmayan pencerenin kolay ve bilinen yollarla kapanabilmesi gerekiyor.
- **Çözüm:**
  - Esc, resme tıklama ya da sağ üstteki kapat düğmesi görüntüleyiciyi kapatıyor.
  - Aynı anda tek görüntüleyici açık oluyor; widget kapanınca o da kapanıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/ImageViewerWindow.cs`
- **Testler:** `ImageViewerTests.Escape_ClosesTheViewer` (Esc görüntüleyiciyi kapatır, widget açık kalır)
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Kapatma yolları:** Otomatik testte yalnız Esc doğrulandı; resme tıklama ve kapat düğmesiyle kapanma için ayrı bir
  UI testi yok.
- **Test altyapısı:**
  - Sandbox'ta masaüstünün alt pencereleri, başlatılan sürecin kimliğiyle eşleşmiyor. Bu yüzden ikinci bir pencere
    süreç kimliğiyle değil, başlığıyla bulunuyor (`AppSession.FindWindow`).
  - Uygulama çökerse `crash.log` sonuç klasörüne kopyalanıyor (`AppDataFolder.Dispose`).
- **Testler:** Unit 293/293; görüntüleyici UI testleri 3/3; tam UI suite 67/67 + 1 izole test. Sonar: bulgu yok.

### Referanslar

- `MAIN_TODO.md` → 📊 Genel İlerleme → Faz 12
- `PHASE11.md` (önceki faz)
- `PHASE15.md` → 15.3 (görüntüleyicide Ctrl+C)

### Önceki doküman içeriği

> Önce: `PHASE11.md`

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| V1 Resim kartına tıklayınca resim büyük açılır | 🟢 Tamamlandı | 12.2 |
| V2 Görüntüleyici ekrana sığar | 🟢 Tamamlandı | `ImageViewerPlacement` |
| V3 Esc, resme tıklama ya da kapat düğmesi kapatır | 🟢 Tamamlandı | 12.2 |

---

#### 12.1 Gereksinim

- Gereksinim: Resim kartlarındaki resimlere tıklanınca resmin büyük hali görüntülenmeli.

---

#### 12.2 Kararlar

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

#### 12.3 Kabul kriterleri ve testler

| # | Kriter | Test |
|---|--------|------|
| V1 | 1200x600 resmin büyük hali kartın iki katından geniş, oranı 2:1 | `ImageViewerTests.ClickingImageCard_ShowsTheImageLarge`, `ImageItemViewModelTests` |
| V2 | Görüntüleyici çalışma alanının içinde; %90 sınırı, ortalama, küçük ve boyutu bilinmeyen resim | `ImageViewerTests.Viewer_FitsOnTheScreen`, `ImageViewerPlacementTests` |
| V3 | Esc görüntüleyiciyi kapatır, widget açık kalır | `ImageViewerTests.Escape_ClosesTheViewer` |

---

#### 12.4 Sonuç

- **Testler:**
  - Unit: 293/293.
  - Görüntüleyici UI testleri 3/3; tam UI suite 67/67 + 1 izole test.
  - Sonar: bulgu yok.
- **Test altyapısı:**
  - Sandbox'ta masaüstünün alt pencereleri, başlatılan sürecin kimliğiyle eşleşmiyor. Bu yüzden ikinci bir pencere
    süreç kimliğiyle değil, başlığıyla bulunuyor (`AppSession.FindWindow`).
  - Uygulama çökerse `crash.log` sonuç klasörüne kopyalanıyor (`AppDataFolder.Dispose`).
