# Faz 15 — Resim kopyalama ve resim alma

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Bir resim kartındaki resim artık panoya kopyalanabiliyor ve Paint, Word ya da bir sohbet uygulamasına
yapıştırılabiliyor. Bunun üç yolu var: kartın üzerindeki kopyalama düğmesi, sağ tık menüsündeki "Copy image" ve büyük
görüntüleme penceresinde Ctrl+C. Widget'a sürüklenen resim dosyaları ve resim verisi de artık uygulama kartı değil,
resim kartı oluyor.

## Problem

- Resim kartlarında kopyalama yoktu: not kartında "Copy" düğmesi vardı, resim kartında ne düğme ne menü öğesi vardı.
- Explorer'dan sürüklenen bir resim dosyası resim kartı yerine uygulama kartı oluyordu; Ctrl+V ile yapıştırılan aynı
  dosya ise resim kartı oluyordu.

## Çözüm

- **Kopyalama (`ClipboardWriter`):** Resim panoya hem resim hem dosya olarak konur ve widget kapansa da panoda kalır.
- **Kart:** Not kartındaki kopyalama düğmesi resim kartlarında da çıkar; menüye "Copy image" eklendi.
- **Görüntüleyici:** Ctrl+C gösterilen resmi kopyalar.
- **Bırakma (`BoardViewModel`):** Resim dosyaları resim kartı, bırakılan resim verisi (bitmap) resim kartı olur;
  diğer dosya, klasör ve adresler eskisi gibi uygulama kartı olur.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 15.1 | Resim kartının üzerindeki düğme resmi panoya kopyalar. | 🟢 Tamamlandı |
| 15.2 | Resim kartının sağ tık menüsünde "Copy image" vardır. | 🟢 Tamamlandı |
| 15.3 | Görüntüleme penceresinde Ctrl+C resmi kopyalar. | 🟢 Tamamlandı |
| 15.4 | Bırakılan resim dosyası resim kartı olur. | 🟢 Tamamlandı |
| 15.5 | Bırakılan resim verisi resim kartı olur. | 🟢 Tamamlandı (yalnız view model testi) |
| 15.6 | Ayarlar kapanınca "Settings" ipucu ızgaranın üstünde kalmaz. | 🟢 Tamamlandı (testlerde bulunan hata) |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| "Resim kopyalama" hangi yön: panoya kopyalama mı, resim alma mı? | A | 🟢 Verildi: C (ikisi birden) | S7 |

## Nasıl kontrol edilir

- [ ] Bir resim kartının üzerine gel, sağ üstteki kopyalama düğmesine bas, Paint'te Ctrl+V yap: resim gelmeli.
- [ ] Resim kartına sağ tıkla → "Copy image", sonra bir sohbet penceresine yapıştır: resim gelmeli.
- [ ] Resim kartına tıkla, açılan pencerede Ctrl+C yap, Explorer'da bir klasöre Ctrl+V yap: resim dosyası gelmeli.
- [ ] Explorer'dan bir `.png` dosyasını widget'a sürükle: uygulama kartı değil, resim kartı olmalı.
- [ ] Bir uygulamadan (ör. Paint ya da bir tarayıcı) resmin kendisini sürükle: resim kartı olmalı.

## Kalan

- **15.5:** Gerçek sürükle-bırak Sandbox'ta otomatik test edilemiyor; elle deneme bekliyor.

## Ayrıntılar

### 15.1 — Resim kartının üzerindeki düğme resmi panoya kopyalar.

- **Mevcut durum:** Kopyalama düğmesi yalnız not kartlarında vardı ve metni kopyalıyordu.
- **Problem:** Resmi başka bir uygulamaya almanın yolu yoktu.
- **Çözüm:**
  - Aynı düğme resim kartlarında da gösteriliyor.
  - Not kartında `CopyNoteButton` ("Copy note") adıyla metni, resim kartında `CopyImageButton` ("Copy image") adıyla
    resmi kopyalıyor.
  - `ClipboardWriter.CopyImageAsync` resmi `SetBitmap` ve `SetStorageItems` ile koyuyor; ardından `Clipboard.Flush`
    çağırıyor.
  - Düğmeye basmak kartın tıklamasını tetiklemez; görüntüleyici açılmaz.
- **Dosyalar:** `src/MyEverythingWidget.App/ClipboardWriter.cs`, `src/MyEverythingWidget.App/Views/GridCard.xaml`,
  `src/MyEverythingWidget.App/Views/GridCard.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/ImageCopyTests.cs` → `CopyButton_OnImageCard_PutsThePictureOnTheClipboard`
- **Durum:** 🟢 Tamamlandı.

### 15.2 — Resim kartının sağ tık menüsünde "Copy image" vardır.

- **Mevcut durum:** Resim kartının menüsünde yalnız "Move to" ve "Delete" vardı.
- **Problem:** Fareyle kartın üzerine gelmeden kopyalamanın yolu yoktu.
- **Çözüm:** Menüye `CopyImageMenuItem` eklendi; aynı `ClipboardWriter.CopyImageAsync` kullanılıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/ImageCopyTests.cs` → `CopyImageMenuItem_PutsThePictureOnTheClipboard`
- **Durum:** 🟢 Tamamlandı.

### 15.3 — Görüntüleme penceresinde Ctrl+C resmi kopyalar.

- **Mevcut durum:** Görüntüleyicide yalnız Esc vardı.
- **Problem:** Büyük hali açıkken resmi kopyalamak beklenen bir kısayol.
- **Çözüm:** Görüntüleyiciye Ctrl+C kısayolu eklendi.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/ImageViewerWindow.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/ImageCopyTests.cs` → `CtrlC_InTheViewer_PutsThePictureOnTheClipboard`
- **Durum:** 🟢 Tamamlandı.

### 15.4 — Bırakılan resim dosyası resim kartı olur.

- **Mevcut durum:** `AddDroppedAsync` her yolu uygulama kartı yapıyordu.
- **Problem:** Ctrl+V ile resim kartı olan bir dosya, sürüklenince uygulama kartı oluyordu.
- **Çözüm:**
  - Tam bir yol, resim uzantısı ve var olan dosya ise `AddImageFileAsync` ile resim kartı ekleniyor.
  - Diğerleri eskisi gibi uygulama kartı oluyor; karışık bırakmada ikisi de ekleniyor.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`
- **Testler:** `tests/MyEverythingWidget.Presentation.Tests/NotesImagesPasteTests.cs` → `Drop_ImageFile_AddsImageNotAppCard`,
  `Drop_ImageFileAndProgram_AddsImageAndAppCard`
- **Durum:** 🟢 Tamamlandı.

### 15.5 — Bırakılan resim verisi resim kartı olur.

- **Mevcut durum:** Bırakma alanı resim verisini (bitmap) kabul etmiyordu.
- **Problem:** Bir uygulamadan sürüklenen resmin kendisi eklenemiyordu.
- **Çözüm:**
  - Bırakılan veride bitmap varsa ve dosya yoksa `AddDroppedPictureAsync` ile resim kartı ekleniyor.
  - `OnGridDragOver` bu biçimi de kabul ediyor.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.Presentation.Tests/NotesImagesPasteTests.cs` → `DropPicture_AddsImage`
- **Durum:** 🟢 Tamamlandı (yalnız view model testi; bırakma işleyicisi elle denenmeli).

### 15.6 — Ayarlar kapanınca "Settings" ipucu ızgaranın üstünde kalmaz.

- **Mevcut durum:** Ayarlar penceresi kapanınca klavye odağı "Settings" düğmesine dönüyordu.
- **Problem:**
  - WinUI, klavye odağındaki düğmenin ipucunu gösteriyor. "Settings" yazısı, kullanıcı bir şey yapana kadar ızgaranın
    sağ alt köşesinin üstünde duruyordu.
  - Tema testleri de bu köşeden renk örneklediği için düşüyordu.
- **Çözüm:** Ayarlar penceresi kapanınca odak programla ızgaraya veriliyor; programla verilen odak ipucu göstermez.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/SettingsAndMigrationTests.cs` (tema testleri; önce 2 test kırmızıydı,
  şimdi 6/6)
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Gerçek sürükle-bırak:** Explorer'dan ya da tarayıcıdan sürükle-bırak Sandbox'ta otomatik test edilemiyor. 15.4 ve
  15.5 view model düzeyinde test edildi.
- **Tarayıcıdan sürükleme:**
  - Tarayıcılar bir resmi sürüklerken çoğunlukla resmin kendisini değil adresini gönderir. O durumda eskisi gibi web
    sitesi kartı oluşur; resmi indirip kart yapmak bu fazın kapsamında değil.
  - Tarayıcıda "Resmi kopyala" + Ctrl+V ise resim kartı verir.
- **Sonar:** Bu turda çalıştırılamadı; çalışan bir IDE yoktu.
- **Testler:** Tam UI suite 77/77 + 1 izole test; unit 296/296.

### Referanslar

- `questions/S07-resim-kopyalama.md` → Cevap
- `PHASE13.md` → Ayrıntılar (resmi ikon olarak yapıştırma; aynı pano okuma yolu)
