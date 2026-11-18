# Faz 6 — Notlar, resimler ve Ctrl+V

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Widget'a artık not ve resim kartları eklenebiliyor. Alttaki "+ Add" menüsünde App…, Note ve Image… var; not kartındaki
Copy düğmesi metni panoya kopyalıyor, kartlar sağ tıkla düzenlenip yeniden adlandırılabiliyor. Pencerede Ctrl+V'ye
basınca panodaki içeriğe göre kart ekleniyor: resim resim kartı, program ya da adres uygulama kartı, diğer metin not
kartı oluyor.

## Problem

- WinUI sürümünde not ve resim kartı yoktu; yalnız uygulama kartları eklenebiliyordu.
- Panodaki metin, resim ya da dosyayı widget'a almanın hızlı bir yolu yoktu.
- Uygulama kartlarının adı değiştirilemiyordu (Faz 5'ten kalan "Rename").

## Çözüm

- **Core:** `ImageSpan` resmin en-boy oranından kart boyutunu hesaplar; not düzenleme ve uygulama adlandırma.
- **Presentation (`BoardViewModel`):** `PasteAsync`, `AddNote`, `AddImageAsync`.
- **Infrastructure (`ImageStore`):** Resmi en uzun kenarı 2048 px'e küçültüp PNG olarak `images\` altına kaydeder.
- **App:** "+ Add" menüsüne Note ve Image…, pencere düzeyinde Ctrl+V, not kartında Copy düğmesi, sağ tık Edit/Rename
  (`TextEditorDialog`).

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 6.1 | "+ Add" menüsünde App…, Note ve Image… seçenekleri vardır. | 🟢 Tamamlandı |
| 6.2 | Not bir pencerede yazılır ve not kartı olarak eklenir. | 🟢 Tamamlandı |
| 6.3 | Not kartındaki Copy düğmesi metni panoya kopyalar. | 🟢 Tamamlandı |
| 6.4 | Not ve uygulama kartları sağ tık menüsünden düzenlenir ve yeniden adlandırılır. | 🟢 Tamamlandı |
| 6.5 | Resim dosyadan eklenir ve kart boyutu resmin en-boy oranından gelir. | 🟢 Tamamlandı |
| 6.6 | Pencerede Ctrl+V panodaki içeriğe göre resim, uygulama ya da not kartı ekler. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Not ve ad düzenleyici ne olur? | Küçük ContentDialog | 🟢 Verildi | Menüden açılan flyout, kapanan menü tarafından kapatılıyordu (Ayrıntılar → 6.4) |
| Copy düğmesi nerede durur? | Not kartında, üzerine gelince görünür | 🟢 Verildi | Kart sade kalır |
| Ctrl+V nasıl keşfedilir? | Alt çubukta "Drop or paste (Ctrl+V) files, links, text or images" ipucu | 🟢 Verildi | Özellik keşfedilebilir |
| Ctrl+V hangi içerikten ne yapar? | İçerik türü tablosu | 🟢 Verildi | `MAIN_TODO.md` → Kararlar → K7; Ayrıntılar → 6.6 |

## Nasıl kontrol edilir

- [ ] "+ Add" → "Note" seç, bir metin yaz ve Ctrl+Enter'a bas: not kartı eklenmeli.
- [ ] Not kartının üzerine gel, sağ üstteki Copy düğmesine bas, bir metin kutusuna yapıştır: notun metni gelmeli.
- [ ] Not kartına çift tıkla ya da sağ tıkla → "Edit": metni değiştir, kart yeni metni göstermeli.
- [ ] Bir uygulama kartına sağ tıkla → "Rename": yeni ad kartta görünmeli.
- [ ] Bir ekran görüntüsü al (1600x900), widget'ta Ctrl+V yap: 3x2 boyutunda resim kartı eklenmeli.
- [ ] `Meeting at 10` metnini kopyala ve Ctrl+V yap: not kartı eklenmeli; `https://github.com` kopyalayınca "Github"
  adlı uygulama kartı eklenmeli.
- [ ] Bir metin kutusu odaktayken Ctrl+V yap: metin kutuya yapışmalı, kart oluşmamalı.

## Kalan

- Yok.

## Ayrıntılar

### 6.1 — "+ Add" menüsünde App…, Note ve Image… seçenekleri vardır.

- **Mevcut durum:** "+ Add" menüsünde yalnız App… vardı (Faz 5).
- **Problem:** Not ve resim eklemek için bir giriş noktası gerekiyordu.
- **Çözüm:** Alt çubuktaki "+ Add" menüsüne Note ve Image… eklendi.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml` (alt çubuk)
- **Testler:** `UiTests` → `NoteImagePasteTests.AddNoteFromMenu_AddsNote`
- **Durum:** 🟢 Tamamlandı.

### 6.2 — Not bir pencerede yazılır ve not kartı olarak eklenir.

- **Mevcut durum:** Not kartı yoktu.
- **Problem:** Kısa notları widget'ta tutmak isteniyor (N1).
- **Çözüm:** Not bir pencerede yazılır ve Ctrl+Enter ya da Save ile kaydedilir; `BoardViewModel.AddNote` kartı ekler.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.App/Views/TextEditorDialog.cs`
- **Testler:** `Presentation.Tests` → `NotesImagesPasteTests`; `UiTests` → `AddNoteFromMenu_AddsNote`
- **Durum:** 🟢 Tamamlandı.

### 6.3 — Not kartındaki Copy düğmesi metni panoya kopyalar.

- **Mevcut durum:** Notun metnini başka bir yere almanın yolu yoktu.
- **Problem:** Not içeriği çoğunlukla başka bir yere yapıştırılmak için tutuluyor (N2).
- **Çözüm:** Kartın sağ üstündeki Copy düğmesi metni panoya kopyalar; düğme yalnız üzerine gelince görünür, kart
  sade kalır.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/GridCard.xaml`, `src/MyEverythingWidget.App/Views/GridCard.xaml.cs`
- **Testler:** `UiTests` → `CopyButton_PutsNoteTextOnClipboard`
- **Durum:** 🟢 Tamamlandı.

### 6.4 — Not ve uygulama kartları sağ tık menüsünden düzenlenir ve yeniden adlandırılır.

- **Mevcut durum:** Kartlar oluşturulduktan sonra değiştirilemiyordu; "Rename" Faz 5'ten bu faza bırakılmıştı.
- **Problem:** Notun metni ve uygulama kartının adı değiştirilebilmeli.
- **Çözüm:**
  - Not kartı çift tık ya da sağ tık "Edit" ile, uygulama kartı sağ tık "Rename" ile düzenlenir.
  - Not düzenleme ve adlandırma Core'da.
  - Düzenleyici küçük bir ContentDialog (`TextEditorDialog`). Menüden açılan flyout, kapanan menü tarafından
    kapatılıyordu: sandbox ekran görüntüsünde flyout yoktu, bazı koşularda bulunuyor ama yazılamıyordu
    (`E_UNEXPECTED`). Açılışı menü kapandıktan sonraya ertelemek kararsız kaldı; ContentDialog 8/8 kararlı.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/TextEditorDialog.cs`, `src/MyEverythingWidget.Core/State/WidgetBoard.cs`
- **Testler:** `Core.Tests` → `WidgetBoardEditTests`; `UiTests` → `EditNoteFromMenu_ChangesText`,
  `RenameAppFromMenu_ChangesName`
- **Durum:** 🟢 Tamamlandı.

### 6.5 — Resim dosyadan eklenir ve kart boyutu resmin en-boy oranından gelir.

- **Mevcut durum:** Resim kartı yoktu.
- **Problem:** Resimler widget'ta görünür olmalı ve kart boyutu resme uymalı (I2).
- **Çözüm:**
  - Resim "Image…" ile dosyadan ya da Ctrl+V ile eklenir (`BoardViewModel.AddImageAsync`).
  - `ImageStore` en uzun kenarı 2048 px'e küçültüp PNG olarak `images\` altına kaydeder; kart silinince dosya da
    silinir. Dosya yoksa "Image not found" yer tutucusu gösterilir.
  - `ImageSpan` (Python sürümüyle aynı kurallar): oran ≥ 2,5 → 3x1; ≥ 1,5 → 3x2; ≥ 1,1 → 2x1; ≥ 0,9 → 2x2;
    ≥ 0,5 → 1x2; daha dar → 1x3.
- **Dosyalar:** `src/MyEverythingWidget.Core/Grid/ImageSpan.cs`, `src/MyEverythingWidget.Presentation/BoardViewModel.cs`,
  `src/MyEverythingWidget.Infrastructure/Shell/ImageStore.cs`
- **Testler:** `Core.Tests` → `ImageSpanTests`; `Infrastructure.Tests` → `ImageStoreTests` (4)
- **Durum:** 🟢 Tamamlandı.

### 6.6 — Pencerede Ctrl+V panodaki içeriğe göre resim, uygulama ya da not kartı ekler.

- **Mevcut durum:** Ctrl+V'nin widget'ta bir karşılığı yoktu.
- **Problem:** Panodaki içeriği tek tuşla kart yapmak isteniyor (K7, I1).
- **Çözüm:**
  - Pano okuma (`ClipboardService`, bugün `ClipboardReader`) ve pencere düzeyinde Ctrl+V; `BoardViewModel.PasteAsync` içerik türüne göre karar verir
    (`MAIN_TODO.md` → Kararlar → K7).
  - Resim (bitmap) → resim kartı, span en-boy oranından (1600x900 ekran görüntüsü → 3x2).
  - Resim dosyası (Explorer'da kopyalanan `.png`) → resim kartı.
  - Program, kısayol, klasör → uygulama kartı (Explorer'da kopyalanan `cmd.exe` → "Cmd").
  - Tek satırlık web adresi ya da tam yol → uygulama kartı (`https://github.com` → "Github").
  - Diğer metin (`Meeting at 10`) ve içinde adres geçen cümle (`see https://github.com later`) → not kartı.
  - Pano boşsa hiçbir şey olmaz; bir metin kutusu odaktayken Ctrl+V o kutuya yapıştırır, kart oluşturmaz.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.Presentation/PastedContent.cs`,
  `src/MyEverythingWidget.App/ClipboardReader.cs` (pano okuma), `src/MyEverythingWidget.App/MainWindow.xaml.cs` (Ctrl+V)
- **Testler:** `Presentation.Tests` → `NotesImagesPasteTests` (15); `UiTests` → `NoteImagePasteTests.PastingText_AddsNote`,
  `PastingScreenshot_AddsImageSizedByAspectRatio`, `PastingCopiedProgram_AddsAppCard`,
  `PastingIntoTextBox_DoesNotAddCard`
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **UI testlerinde pano:** UI testleri panoyu sandbox içinde PowerShell (WinForms) ile doldurur ve gerçek Ctrl+V
  tuşuna basar.
- **Yapıştırma testlerinin beklemesi:** Ctrl+V çalışıyordu; testler grid altında bir gizli öğe daha sayıldığını
  varsayıyordu. Uygulama doğruydu, test düzeltildi.
- **Sekme sürükleme testi:** Bir tam koşuda kırmızıydı. `TabView` sistem sürükle-bırakını kullanır; eşiği aşan ilk
  harekette duraklama ister. Test sürücüsü bunu yapıyor, iki ayrı koşuda kararlı (kök neden için `PHASE7.md` → 7.5).
- **Testler:** Unit 206/206, UI 41/41 (sekme sürükleme testi ayrıca 2 koşuda 8/8), Sonar 0 bulgu.

### Referanslar

- `MAIN_TODO.md` → Faz 6 — Notlar, resimler ve Ctrl+V
- `MAIN_TODO.md` → Kararlar → K7
- `PHASE5.md` (önceki faz) · `PHASE7.md` (Ayarlar ve eski veriyi içe aktarma)

### Önceki doküman içeriği

> Önce: `PHASE5.md` · Sonra: `PHASE7.md` (Ayarlar ve eski veriyi içe aktarma)

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `ImageSpan`, not düzenleme, uygulama adlandırma (Core) | 🟢 Tamamlandı | I2 |
| `PasteAsync`, `AddNote`, `AddImageAsync` (Presentation) | 🟢 Tamamlandı | K7, N1, I1 |
| `ImageStore` (Infrastructure) | 🟢 Tamamlandı | |
| "Add" menüsü (Note, Image…), Ctrl+V, Copy düğmesi, Edit/Rename | 🟢 Tamamlandı | N2 |

---

#### 6.1 Kapsam

- "+ Add" menüsü: App…, Note, Image….
- Not: dialogda yazılır (Ctrl+Enter ya da Save). Kartın sağ üstündeki Copy düğmesi metni panoya kopyalar; çift tık
  ya da sağ tık "Edit" ile düzenlenir.
- Uygulama kartı: sağ tık "Rename".
- Resim: dosyadan ya da Ctrl+V ile; kart boyutu en-boy oranından gelir; en uzun kenar 2048 px'e küçültülüp PNG olarak
  `images\` altına kaydedilir; kart silinince dosya da silinir.

---

#### 6.2 Ctrl+V kuralları

`MAIN_TODO.md` → Kararlar → K7.

| Panoda | Sonuç | Örnek |
|--------|-------|-------|
| Resim (bitmap) | Resim kartı, span en-boy oranından | 1600x900 ekran görüntüsü → 3x2 |
| Resim dosyası | Resim kartı | Explorer'da kopyalanan `.png` |
| Program, kısayol, klasör | Uygulama kartı | Explorer'da kopyalanan `cmd.exe` → "Cmd" |
| Tek satırlık web adresi ya da tam yol | Uygulama kartı | `https://github.com` → "Github" |
| Diğer metin | Not kartı | `Meeting at 10` |
| İçinde adres geçen cümle | Not kartı | `see https://github.com later` |
| Boş | Hiçbir şey | |

Bir metin kutusu odaktayken Ctrl+V o kutuya yapıştırır, kart oluşturmaz.

Resim span kuralları (Python sürümüyle aynı): oran ≥ 2,5 → 3x1; ≥ 1,5 → 3x2; ≥ 1,1 → 2x1; ≥ 0,9 → 2x2; ≥ 0,5 → 1x2;
daha dar → 1x3.

---

#### 6.3 Tasarım kararları

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Not ve ad düzenleyici | Küçük ContentDialog | Menüden açılan flyout, kapanan menü tarafından kapatılıyordu (6.5.1) |
| Copy düğmesi | Not kartında, üzerine gelince görünür | Kart sade kalır |
| Ctrl+V ipucu | Alt çubukta "Drop or paste (Ctrl+V) files, links, text or images" | Özellik keşfedilebilir |

---

#### 6.4 Testler

| Kabul kriteri | Test |
|---------------|------|
| I2 | `Core.Tests` → `ImageSpanTests` |
| Not düzenleme, adlandırma (Core) | `Core.Tests` → `WidgetBoardEditTests` |
| K7, N1, I1 (mantık) | `Presentation.Tests` → `NotesImagesPasteTests` (15) |
| Resim içe aktarma | `Infrastructure.Tests` → `ImageStoreTests` (4) |
| K7 metin → not | `UiTests` → `NoteImagePasteTests.PastingText_AddsNote` |
| K7 bitmap → resim, I2 | `UiTests` → `PastingScreenshot_AddsImageSizedByAspectRatio` |
| K7 dosya → uygulama | `UiTests` → `PastingCopiedProgram_AddsAppCard` |
| K7 metin kutusu | `UiTests` → `PastingIntoTextBox_DoesNotAddCard` |
| N1 | `UiTests` → `AddNoteFromMenu_AddsNote` |
| N2 | `UiTests` → `CopyButton_PutsNoteTextOnClipboard` |
| Düzenleme, adlandırma | `UiTests` → `EditNoteFromMenu_ChangesText`, `RenameAppFromMenu_ChangesName` |

UI testleri panoyu sandbox içinde PowerShell (WinForms) ile doldurur ve gerçek Ctrl+V tuşuna basar.

---

#### 6.5 Sonuç

Faz 6 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`: Core, Presentation, Infrastructure) | 206/206 |
| UI (Sandbox) | 41/41 (sekme sürükleme testi ayrıca 2 koşuda 8/8) |
| Sonar | 0 bulgu |

##### 6.5.1 Bulunan ve düzeltilen sorunlar

- **Menüden açılan düzenleyici flyout'u kapanıyordu:**
  - Teşhis: sandbox ekran görüntüsünde flyout yoktu; bazı koşularda bulunuyor ama yazılamıyordu (`E_UNEXPECTED`).
  - Önce açılışı menü kapandıktan sonraya ertelemek denendi; kararsız kaldı.
  - Çözüm: düzenleyici ContentDialog oldu (`TextEditorDialog`); 8/8 kararlı.
- **Yapıştırma testlerinin beklemesi yanlıştı:**
  - Teşhis: Ctrl+V çalışıyordu (not kartı ekranda).
  - Testler grid altında bir gizli öğe daha sayıldığını varsayıyordu.
  - Uygulama doğruydu, test düzeltildi.
- **Sekme sürükleme testi bir tam koşuda kırmızıydı:**
  - Sebep: `TabView` sistem sürükle-bırakını kullanır; eşiği aşan ilk harekette duraklama ister.
  - Test sürücüsü bunu yapıyor, iki ayrı koşuda kararlı.

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 6 — Notlar, resimler ve Ctrl+V" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 206/206, UI 41/41 (Sandbox). Sonuç: `PHASE6.md` → 6.5 Sonuç.

**Özet:** Not ve resim kartları, hızlı not, pencere düzeyinde Ctrl+V.

**Hedefler:**

- [x] Hızlı not kutusu (N1), not kartı: Copy, Edit, Resize, Move to, Delete (N2)
- [x] Resim kartı: dosyadan ekleme, en-boy oranından span (I2), "Image not found" yer tutucusu
- [x] `ClipboardService` + pencere düzeyinde Ctrl+V; içerik türü tablosu (K7, I1)
- [x] "Add" menüsü (alt çubukta "+ Add" menüsü): App, Note, Image

**Detay:** `PHASE6.md`
