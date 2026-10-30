# MEW-4 Faz 6 — Notlar, resimler ve Ctrl+V

> Önce: `PHASE5.md` · Sonra: `PHASE7.md` (Ayarlar ve eski veriyi içe aktarma)

## İçindekiler

- Durum Panosu
- 6.1 Kapsam
- 6.2 Ctrl+V kuralları
- 6.3 Tasarım kararları
- 6.4 Testler
- 6.5 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `ImageSpan`, not düzenleme, uygulama adlandırma (Core) | 🟢 Tamamlandı | I2 |
| `PasteAsync`, `AddNote`, `AddImageAsync` (Presentation) | 🟢 Tamamlandı | K7, N1, I1 |
| `ImageStore` (Infrastructure) | 🟢 Tamamlandı | |
| "Add" menüsü (Note, Image…), Ctrl+V, Copy düğmesi, Edit/Rename | 🟢 Tamamlandı | N2 |

---

## 6.1 Kapsam

- "+ Add" menüsü: App…, Note, Image….
- Not: dialogda yazılır (Ctrl+Enter ya da Save). Kartın sağ üstündeki Copy düğmesi metni panoya kopyalar; çift tık
  ya da sağ tık "Edit" ile düzenlenir.
- Uygulama kartı: sağ tık "Rename".
- Resim: dosyadan ya da Ctrl+V ile; kart boyutu en-boy oranından gelir; en uzun kenar 2048 px'e küçültülüp PNG olarak
  `images\` altına kaydedilir; kart silinince dosya da silinir.

---

## 6.2 Ctrl+V kuralları

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

## 6.3 Tasarım kararları

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Not ve ad düzenleyici | Küçük ContentDialog | Menüden açılan flyout, kapanan menü tarafından kapatılıyordu (6.5.1) |
| Copy düğmesi | Not kartında, üzerine gelince görünür | Kart sade kalır |
| Ctrl+V ipucu | Alt çubukta "Drop or paste (Ctrl+V) files, links, text or images" | Özellik keşfedilebilir |

---

## 6.4 Testler

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

## 6.5 Sonuç

Faz 6 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`: Core, Presentation, Infrastructure) | 206/206 |
| UI (Sandbox) | 41/41 (sekme sürükleme testi ayrıca 2 koşuda 8/8) |
| Sonar | 0 bulgu |

### 6.5.1 Bulunan ve düzeltilen sorunlar

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
