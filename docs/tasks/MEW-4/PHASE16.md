# Faz 16 — Kopyalama geri bildirimi, görüntüleyici menüsü ve Paint'te düzenleme

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Kopyalama düğmesine basınca düğme bir an onay işaretine dönüp "Copied" diyor; sağ tık menüsünden kopyalayınca da kart
aynı şekilde gösteriyor. Büyük görüntüleme penceresinde sağ tık menüsü var: "Copy" ve "Edit in Paint". Resim
kartlarının menüsüne de "Edit in Paint" eklendi. Paint'te kaydedilen resim, widget'a geri dönülünce kartta yenileniyor.
Düzenleme Paint'te yapıldığı için widget'ın belleği büyümüyor.

## Problem

- Kopyalama düğmesine basınca hiçbir şey değişmiyordu; resimde de notta da kopyalanmamış gibi görünüyordu (T3).
- Büyük görüntüleme penceresinde sağ tık menüsü yoktu (T3).
- Resmi düzenlemenin yolu yoktu. Uygulama içine çizim aracı koymak hem iş hem bellek açısından pahalı; sorulan,
  Paint'te düzenleme gibi ucuz bir yoldu (T3).

## Çözüm

- **Kart (`GridCard`):** Kopyalayınca düğme 1,5 s onay işareti ve "Copied" gösterir. Fare kartın üzerinde değilse de
  görünür.
- **Kart menüsü:** "Copy image" aynı geri bildirimi verir; "Edit in Paint" eklendi.
- **Görüntüleyici:**
  - Sağ tık menüsünde "Copy" ve "Edit in Paint" var.
  - Kopyalayınca (menü ya da Ctrl+C) altta kısa bir "Copied" bildirimi çıkar.
- **Yenileme:** Widget yeniden etkinleşince, dosyası değişmiş resim kartları yeniden yüklenir; görüntü önbelleği atlanır.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 16.1 | Kopyalama düğmesi kopyaladığını bir an gösterir. | 🟢 Tamamlandı |
| 16.2 | Görüntüleme penceresinde "Copy" ve "Edit in Paint" içeren sağ tık menüsü vardır. | 🟢 Tamamlandı |
| 16.3 | Resim Paint'te düzenlenebilir; kaydedilen değişiklik kartta görünür. | 🟢 Tamamlandı (Paint'in açılması elle denenmeli) |
| 16.4 | Faz tablosu ve faz özetleri şablona getirilir. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- [ ] Bir not ya da resim kartında kopyalama düğmesine bas: düğme bir an onay işaretine dönüp "Copied" demeli.
- [ ] Resim kartına sağ tıkla → "Copy image": kartın köşesinde aynı onay görünmeli.
- [ ] Resmi büyüt, sağ tıkla → "Copy": altta "Copied" yazmalı; Paint'e yapıştırınca resim gelmeli.
- [ ] Sağ tık → "Edit in Paint": Paint resimle açılmalı. Bir çizgi çizip kaydet, widget'a tıkla: kart yeni hali göstermeli.

## Kalan

- **16.3:** Paint'in gerçekten açılması Sandbox'ta otomatik test edilmedi; elle denenmeli.

## Ayrıntılar

### 16.1 — Kopyalama düğmesi kopyaladığını bir an gösterir.

- **Mevcut durum:** Düğmeye basınca görünürde bir değişiklik olmuyordu.
- **Problem:** Kullanıcı kopyalamanın olup olmadığını anlayamıyordu.
- **Çözüm:**
  - `GridCard.CopyAsync` kopyalayıp `ShowCopied` çağırıyor.
  - Simge 1,5 s onay işaretine dönüyor, ad ve ipucu "Copied" oluyor, sonra eski haline geliyor.
  - Menüdeki "Copy image" de aynı yöntemi kullanıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/GridCard.xaml`, `src/MyEverythingWidget.App/Views/GridCard.xaml.cs`,
  `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/ImageCopyTests.cs` → `CopyButton_ShowsThatTheImageWasCopied`,
  `CopyImageMenuItem_ShowsThatTheImageWasCopied`
- **Durum:** 🟢 Tamamlandı.

### 16.2 — Görüntüleme penceresinde "Copy" ve "Edit in Paint" içeren sağ tık menüsü vardır.

- **Mevcut durum:** Görüntüleyicide yalnız Esc ve Ctrl+C vardı.
- **Problem:** Fareyle kopyalamanın ya da düzenlemenin yolu yoktu.
- **Çözüm:**
  - Kök öğeye `ContextFlyout` eklendi: `ViewerCopyMenuItem`, `ViewerEditMenuItem`.
  - Kopyalama sonrası `ViewerCopiedNotice` 1,5 s görünüyor; Paint açılamazsa aynı yerde "Paint could not be opened."
    yazıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/ImageViewerWindow.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/ImageCopyTests.cs` → `ViewerContextMenu_CopiesAndSaysSo`
- **Durum:** 🟢 Tamamlandı.

### 16.3 — Resim Paint'te düzenlenebilir; kaydedilen değişiklik kartta görünür.

- **Mevcut durum:** Resmi düzenlemenin yolu yoktu.
- **Problem:** Uygulama içi bir çizim aracı bellek ve iş açısından pahalı.
- **Çözüm:**
  - `ImageEditor.TryOpenInPaint` resmi `mspaint.exe` ile açıyor. Paint ayrı bir süreç olduğu için widget'ın belleği
    değişmiyor.
  - Paint açılamazsa durum çubuğunda uyarı çıkıyor (`BoardViewModel.ReportProblem`).
  - Widget yeniden etkinleşince (`MainWindow.Activated`), dosyasının değişme zamanı farklı olan resim kartları yeniden
    yükleniyor (`GridCard.RefreshImageIfChanged`). Yükleme `BitmapCreateOptions.IgnoreImageCache` ile yapılıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/ImageEditor.cs`, `src/MyEverythingWidget.App/MainWindow.xaml.cs`,
  `src/MyEverythingWidget.App/Views/GridCard.xaml.cs`, `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`,
  `src/MyEverythingWidget.Presentation/BoardViewModel.cs`
- **Testler:**
  - `ImageCopyTests.EditInPaint_IsOfferedForImageCards`.
  - `ImageCopyTests.ImageChangedOutside_IsShownWhenTheWidgetIsActivatedAgain`: dosya dışarıdan değiştirilince kart
    yeni resmi gösteriyor.
  - `NotesImagesPasteTests.ReportProblem_ShowsAWarning`.
- **Durum:** 🟢 Tamamlandı (Paint'in açılması elle denenmeli).

### 16.4 — Faz tablosu ve faz özetleri şablona getirilir.

- **Mevcut durum:** `MAIN_TODO.md` → Faz 1–8 özetleri 5 satırdan uzun.
- **Problem:** Denetim aracı, şablonda olan bazı bölümlerin eksik olduğunu bildiriyor.
- **Çözüm:**
  - `/h-progress-fix` ile yapıldı (T5).
  - `PHASE1.md`–`PHASE14.md` faz sayfası biçimine çevrildi. Eski içerikleri her dokümanın sonunda "Önceki doküman
    içeriği" altında olduğu gibi duruyor.
  - `MAIN_TODO.md`'deki uzun Faz 1–8 bölümleri ilgili faz dokümanının sonuna ("MAIN_TODO'dan taşınan notlar")
    taşındı. Yerlerine "🎯 Faz Özetleri" altında 16 fazın kısa özeti yazıldı.
  - Branch Bilgisi tabloya çevrildi; "✅ Hazırlık Durumu" bölümü eklendi.
- **Dosyalar:** `docs/tasks/MEW-4/MAIN_TODO.md`, `docs/tasks/MEW-4/PHASE1.md` … `PHASE14.md`
- **Testler:** `python ~/.claude/hooks/progress_table_check.py --check` → `MAIN_TODO.md` ve 16 faz dokümanının hepsi
  temiz.
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Paint'in açılması:** Paint, Sandbox'ta bulunmayabileceği için otomatik test edilmedi. Menü öğesinin varlığı ve
  dışarıdan değişen resmin yenilenmesi test edildi.
- **Resim boyutu:** Paint'te resmin boyutu değişirse kartın kapladığı hücre sayısı değişmez; resim kartın içine
  sığdırılarak gösterilir.

### Referanslar

- `PHASE15.md` → 15.1 (kopyalama düğmesi), 15.3 (görüntüleyicide Ctrl+C)
- `TALIMATLAR.md` → T3, T4 (aynı talimat; pano ve terminal kaydı), T5
