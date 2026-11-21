# Faz 8 — UI testleri, performans ve Store paketi

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Bu fazda widget Store'a gönderilmeye hazırlandı. Bütün kabul kriterlerinin otomatik testleri geçiyor; başlama süresi
ve bellek ölçüldü. x64 ve ARM64 için ikon setli MSIX paketleri, Store listeleme metni, gizlilik politikası ve gönderim
adımları hazır. Kart menüsüne "Change icon…" ve "Reset icon" eklendi. Kalan tek adım, Partner Center gönderimini
kullanıcının kendi hesabıyla yapması.

## Problem

- Kabul kriterlerinin hepsinin bir otomatik testle doğrulandığı tek bir yerde görülmüyordu.
- WinUI sürümünün başlama süresi ve belleği ölçülmemişti; Python sürümüyle karşılaştırma yoktu.
- Store'a gönderilecek paket, ikon seti, listeleme metni ve gizlilik politikası yoktu.
- Kart menüsünde "Change icon…" ve "Reset icon" Faz 5'ten kalmıştı.

## Çözüm

- **Testler:** Her kabul kriteri bir teste bağlandı (Ayrıntılar → 8.1); `PerformanceTests` gerilemeye karşı sınır koyar.
- **Paket (`scripts/publish-msix.ps1`):** `-Platform x64|ARM64` ile imzasız tek `.msix`, bütün ikon ölçekleri içinde.
- **Dokümanlar:** `docs/general/STORE_LISTING.md`, `docs/general/PRIVACY_POLICY.md`, `docs/general/STORE_SUBMISSION.md`.
- **Kart menüsü:** "Change icon…" seçilen resmi ikon yapar; "Reset icon" hedefin kendi ikonunu yeniden oluşturur.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 8.1 | Bütün kabul kriterleri otomatik testlerle doğrulanır. | 🟢 Tamamlandı (U3 yalnız ViewModel testi) |
| 8.2 | Başlama süresi ve bellek ölçülür ve gerilemeye karşı korunur. | 🟢 Tamamlandı |
| 8.3 | x64 ve ARM64 için ikon setli, Store'a hazır MSIX paketi üretilir. | 🟢 Tamamlandı |
| 8.4 | Store listeleme metni, gizlilik politikası ve gönderim adımları yazılır. | 🟢 Tamamlandı |
| 8.5 | Kart menüsünde "Change icon…" ve "Reset icon" vardır. | 🟢 Tamamlandı (Faz 5'ten kalan) |
| 8.6 | Uygulama Partner Center üzerinden Store'a gönderilir. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- [ ] `dotnet test` çalıştır: unit testlerin hepsi (236) geçmeli.
- [ ] `pwsh scripts/test-ui.ps1` çalıştır: Windows Sandbox'ta UI testlerinin hepsi (49) geçmeli.
- [ ] `pwsh scripts/publish-msix.ps1 -Platform x64` ve `-Platform ARM64` çalıştır: iki `.msix` dosyası oluşmalı
  (yaklaşık 97 MB ve 95 MB).
- [ ] Paketi kur ve Başlat menüsüne bak: uygulama ikonu açık ve koyu görev çubuğunda net görünmeli.
- [ ] Bir uygulama kartına sağ tıkla → "Change icon…", bir resim seç: kart yeni ikonu göstermeli; "Reset icon" ile
  programın kendi ikonu geri gelmeli.
- [ ] `docs/general/STORE_SUBMISSION.md` adımlarını izle: Partner Center gönderimi tamamlanmalı.

## Kalan

- **8.6:** Partner Center gönderimi kullanıcıda; adımlar `docs/general/STORE_SUBMISSION.md`'de.
- **Store ekran görüntüleri:** Gerçek içerikle, son build'den alınmalı.
- **Sekme sürükleme testinin kök nedeni:** Diğer testlerden sonra aynı süreçte sistem sürükle-bırakı başlamıyor; test
  ayrı süreçte koşuyor (`PHASE7.md` → 7.5).
- **Başlama süresi:** Birden çok örnekle (sıcak/soğuk) ölçüm, sonra ReadyToRun ya da trimming yeniden denenebilir.
- **"Add app" listesinde ikonlar:** Liste şu an yalnız ad gösteriyor.
- **Klavye ile kart taşıma:** Erişilebilirlik; şu an yalnız fare.
- **Explorer'dan gerçek sürükleme testi:** U3 yalnız ViewModel düzeyinde test edildi.
- **MSIX boyutu (97 MB):** Store, Windows App SDK'yı çerçeve paketi olarak verebilir; framework-dependent paket boyutu
  yarıdan fazla düşürür ama sandbox testinde çerçeve paketinin de kurulmasını gerektirir.

## Ayrıntılar

### 8.1 — Bütün kabul kriterleri otomatik testlerle doğrulanır.

- **Mevcut durum:** Testler fazlara dağılmıştı; hangi kriterin hangi testle doğrulandığı tek yerde yoktu.
- **Problem:** Store'a göndermeden önce her kabul kriterinin (`MAIN_TODO.md` → 1.4 Kabul Kriterleri) geçtiği
  görülmeli.
- **Çözüm:** Kriterler testlere bağlandı:
  - G1-G6, G9, G10, K5: `GridDslTests` (27 senaryo) + gerçek fareyle 6 senaryo (`GridInteractionTests`).
  - G7, G8: `GridInteractionTests.DraggedNote_KeepsItsSizeFollowsPointerAndHighlightsTwoCells`.
  - U1, U2: `ShellServicesTests`, `AppItemTests.InstalledApp_PickedFromList_IsAddedWithItsIcon`.
  - U3: `AppItemsTests.DroppedTexts_AddRecognisedTargetsAndReportOthers` (yalnız ViewModel testi; Explorer'dan gerçek
    sürükleme test edilmedi).
  - U4: `LaunchTargetTests`, `ShellServicesTests.Icon_ForWebsite_UsesItsFavicon`.
  - U5, U6: `AppItemTests.ClickingAppCard_StartsTheProgram`, `ClickingCardOfRemovedProgram_ShowsWarning`.
  - N1, N2: `NoteImagePasteTests.AddNoteFromMenu_AddsNote`, `CopyButton_PutsNoteTextOnClipboard`.
  - I1, I2, K7: `NoteImagePasteTests` (yapıştırma), `ImageSpanTests`.
  - W1: `SettingsAndMigrationTests` (piksel ölçümü, iki tema, kalıcılık).
  - W2, W3: `MainWindowTests`.
  - D1: `LegacyImportTests`, `LegacyMigratorTests`, `PreviousVersionData_IsImportedOnFirstStartOnly`.
- **Dosyalar:** `tests/MyEverythingWidget.Core.Tests/Grid/GridDslTests.cs`, `tests/Grid/*.dsl`,
  `tests/MyEverythingWidget.UiTests/GridInteractionTests.cs`, `tests/MyEverythingWidget.UiTests/MainWindowTests.cs`
- **Testler:** Unit 236/236 (Core, Presentation, Infrastructure); UI 49/49 (48 ana süreç + 1 ayrı süreç)
- **Durum:** 🟢 Tamamlandı (U3 yalnız ViewModel düzeyinde).

### 8.2 — Başlama süresi ve bellek ölçülür ve gerilemeye karşı korunur.

- **Mevcut durum:** WinUI sürümünün başlama süresi ve belleği bilinmiyordu.
- **Problem:** Widget sürekli açık durduğu için hızlı başlamalı ve az bellek kullanmalı; Python sürümüyle
  karşılaştırılmalı.
- **Çözüm:**
  - Ölçüm: `PerformanceTests` (Windows Sandbox, soğuk başlama, 12 öğeli grid, 5 sn bekleme sonrası).
  - Başlama (süreç başlangıcı → ana pencere): 2,4-2,5 sn (iki koşu); sınır < 5 sn.
  - Private bellek: 89-91 MB; sınır < 250 MB. Working set: 156-167 MB.
  - Karşılaştırma: Python/PySide6 sürümünün working set'i kullanıcının makinesinde boşta yaklaşık 100 MB'tı
    (2026-10-30, `tasklist`). WinUI sürümü working set'te daha yüksek, private bellekte benzer.
  - ReadyToRun (önceden derleme) denendi: tek ölçümde başlama 3,7 sn çıktı, iyileşme gösterilemedi ve geri alındı.
- **Dosyalar:** `tests/MyEverythingWidget.UiTests/PerformanceTests.cs`
- **Testler:** `UiTests` → `PerformanceTests`
- **Durum:** 🟢 Tamamlandı.

### 8.3 — x64 ve ARM64 için ikon setli, Store'a hazır MSIX paketi üretilir.

- **Mevcut durum:** Faz 1'den yalnız yerel çalıştırma için MSIX vardı; Store'a uygun ikon seti ve iki mimari yoktu.
- **Problem:** Store, desteklenen her mimari için paket ve bütün ölçeklerde ikon ister.
- **Çözüm:**
  - `scripts/publish-msix.ps1 -Platform x64|ARM64`: imzasız tek `.msix`, bütün ikon ölçekleri içinde. Boyut: x64
    97 MB, ARM64 95 MB (self-contained .NET ve Windows App SDK).
  - Betik önce `dotnet clean` çalıştırır; artımlı build bazen paketi yeni klasöre yazmıyordu.
  - İkon seti: `Square44x44Logo` için 16-256 px hedef boyutlar (plated, unplated, light-unplated), diğer logolar için
    %100-%400 ölçekler; `app.ico` exe'ye ve pencereye bağlı.
  - Store kimliği (Partner Center), sürüm ve gönderim: `docs/general/STORE_SUBMISSION.md`.
- **Dosyalar:** `scripts/publish-msix.ps1`, `src/MyEverythingWidget.App/Package.appxmanifest`,
  `src/MyEverythingWidget.App/Assets/`, `src/MyEverythingWidget.App/app.ico`
- **Testler:** — (paketler `scripts/publish-msix.ps1` ile iki mimari için üretildi; Store ekran görüntüleri son build'den alınacak)
- **Durum:** 🟢 Tamamlandı.

### 8.4 — Store listeleme metni, gizlilik politikası ve gönderim adımları yazılır.

- **Mevcut durum:** Store için doküman yoktu.
- **Problem:** Partner Center gönderimi listeleme metni, gizlilik politikası ve `runFullTrust` gerekçesi ister.
- **Çözüm:** TaskTimerWidget dokümanları örnek alınarak:
  - `docs/general/STORE_LISTING.md`: ad, açıklamalar, anahtar kelimeler, ekran görüntüsü listesi.
  - `docs/general/PRIVACY_POLICY.md`: veri toplanmaz; tek ağ isteği eklenen sitenin `/favicon.ico` dosyası.
  - `docs/general/STORE_SUBMISSION.md`: kimlik, sürüm, build, `runFullTrust` gerekçesi.
- **Dosyalar:** `docs/general/STORE_LISTING.md`, `docs/general/PRIVACY_POLICY.md`, `docs/general/STORE_SUBMISSION.md`
- **Testler:** —
- **Durum:** 🟢 Tamamlandı.

### 8.5 — Kart menüsünde "Change icon…" ve "Reset icon" vardır.

- **Mevcut durum:** Kartın ikonu yalnız otomatik oluşturuluyordu; menü öğeleri Faz 5'ten bu faza bırakılmıştı.
- **Problem:** Otomatik ikon beğenilmezse ya da alınamazsa kullanıcı değiştirebilmeli ve geri alabilmeli.
- **Çözüm:**
  - "Change icon…": seçilen resim 64 px PNG olarak `icons\` altına alınır; eski ikon silinir.
  - "Reset icon": programın, klasörün ya da sitenin kendi ikonu yeniden oluşturulur.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`
- **Testler:** `Presentation.Tests` → `AppIconTests` (`ChangeIcon_UsesPickedImageAndDeletesOldIcon`,
  `ChangeIcon_UnreadableImage_KeepsIconAndWarns`, `ResetIcon_RecreatesIconFromTarget`)
- **Durum:** 🟢 Tamamlandı.

### 8.6 — Uygulama Partner Center üzerinden Store'a gönderilir.

- **Mevcut durum:** Paketler ve dokümanlar hazır; gönderim yapılmadı.
- **Problem:** Gönderim kullanıcının Partner Center hesabıyla yapılır; ajan bunu yapamaz.
- **Çözüm:** Kullanıcı `docs/general/STORE_SUBMISSION.md` adımlarını izler; Store ekran görüntüleri gerçek içerikle son
  build'den alınır.
- **Dosyalar:** `docs/general/STORE_SUBMISSION.md`
- **Testler:** —
- **Durum:** 🟢 Tamamlandı (2026-11-20). 1.0.0 Store'da yayında (`PHASE17.md` → 17.4); ardından 1.0.1 ve 1.1.0 gönderildi.

### Doğrulanmayan / dikkat edilmesi gereken

- **Explorer'dan gerçek sürükleme (U3):** Yalnız ViewModel düzeyinde test edildi.
- **Sekme sürükleme testi:** Kök neden bulunamadı; test ayrı süreçte koşuyor (`PHASE7.md` → 7.5).
- **Başlama süresi:** İki koşuluk ölçüm; ReadyToRun tek ölçümle değerlendirildi.
- **Testler:** Unit 236/236, UI 49/49 (48 ana süreç + 1 ayrı süreç), Sonar 0 bulgu.

### Referanslar

- `MAIN_TODO.md` → Faz 8 — UI testleri, performans ve Store paketi
- `MAIN_TODO.md` → 1.4 Kabul Kriterleri
- `docs/general/STORE_SUBMISSION.md`, `docs/general/STORE_LISTING.md`, `docs/general/PRIVACY_POLICY.md`
- `PHASE7.md` (önceki faz)

### Önceki doküman içeriği

> Önce: `PHASE7.md` · Sonra: Partner Center gönderimi (kullanıcı, `docs/general/STORE_SUBMISSION.md`)

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| Bütün kabul kriterlerinin testleri | 🟢 Tamamlandı | 8.1 |
| Başlama süresi ve bellek ölçümü | 🟢 Tamamlandı | 8.2 |
| x64 ve ARM64 MSIX, ikon seti | 🟢 Tamamlandı | 8.3 |
| Store listeleme, gizlilik politikası, gönderim adımları | 🟢 Tamamlandı | `docs/general/STORE_*.md`, `PRIVACY_POLICY.md` |
| Kart menüsü: "Change icon…", "Reset icon" | 🟢 Tamamlandı | Faz 5'ten kalan |
| Partner Center gönderimi | ⏳ Bekliyor | Kullanıcının hesabıyla yapılır |

---

#### 8.1 Kabul kriterlerinin kapsamı

`MAIN_TODO.md` → 1.4 Kabul Kriterleri.

| Kriter | Test | Durum |
|--------|------|-------|
| G1-G6, G9, G10, K5 | `GridDslTests` (27 senaryo) + gerçek fareyle 6 senaryo (`GridInteractionTests`) | ✅ |
| G7, G8 | `GridInteractionTests.DraggedNote_KeepsItsSizeFollowsPointerAndHighlightsTwoCells` | ✅ |
| U1, U2 | `ShellServicesTests`, `AppItemTests.InstalledApp_PickedFromList_IsAddedWithItsIcon` | ✅ |
| U3 | `AppItemsTests.DroppedTexts_AddRecognisedTargetsAndReportOthers` | ✅ yalnız ViewModel testi; Explorer'dan gerçek sürükleme test edilmedi |
| U4 | `LaunchTargetTests`, `ShellServicesTests.Icon_ForWebsite_UsesItsFavicon` | ✅ |
| U5, U6 | `AppItemTests.ClickingAppCard_StartsTheProgram`, `ClickingCardOfRemovedProgram_ShowsWarning` | ✅ |
| N1, N2 | `NoteImagePasteTests.AddNoteFromMenu_AddsNote`, `CopyButton_PutsNoteTextOnClipboard` | ✅ |
| I1, I2, K7 | `NoteImagePasteTests` (yapıştırma), `ImageSpanTests` | ✅ |
| W1 | `SettingsAndMigrationTests` (piksel ölçümü, iki tema, kalıcılık) | ✅ |
| W2, W3 | `MainWindowTests` | ✅ |
| D1 | `LegacyImportTests`, `LegacyMigratorTests`, `PreviousVersionData_IsImportedOnFirstStartOnly` | ✅ |

---

#### 8.2 Performans

Ölçüm: `PerformanceTests` (Windows Sandbox, soğuk başlama, 12 öğeli grid, 5 sn bekleme sonrası).

| Ölçüm | Değer | Sınır (gerileme koruması) |
|-------|-------|---------------------------|
| Başlama (süreç başlangıcı → ana pencere) | 2,4-2,5 sn (iki koşu) | < 5 sn |
| Private bellek | 89-91 MB | < 250 MB |
| Working set | 156-167 MB | — |

Karşılaştırma: Python/PySide6 sürümünün working set'i kullanıcının makinesinde boşta yaklaşık 100 MB'tı (2026-10-30,
`tasklist`). WinUI sürümü working set'te daha yüksek, private bellekte benzer.

ReadyToRun (önceden derleme) denendi: tek ölçümde başlama 3,7 sn çıktı, iyileşme gösterilemedi ve geri alındı
(8.6).

---

#### 8.3 Store paketi

- `scripts/publish-msix.ps1 -Platform x64|ARM64`: imzasız tek `.msix`, bütün ikon ölçekleri içinde. Boyut: x64 97 MB,
  ARM64 95 MB (self-contained .NET ve Windows App SDK).
- Betik önce `dotnet clean` çalıştırır; artımlı build bazen paketi yeni klasöre yazmıyordu.
- İkon seti: `Square44x44Logo` için 16-256 px hedef boyutlar (plated, unplated, light-unplated), diğer logolar için
  %100-%400 ölçekler; `app.ico` exe'ye ve pencereye bağlı.
- Store kimliği (Partner Center), sürüm ve gönderim: `docs/general/STORE_SUBMISSION.md`.

---

#### 8.4 Eklenenler

| Konu | Not |
|------|-----|
| "Change icon…" | Seçilen resim 64 px PNG olarak `icons\` altına alınır; eski ikon silinir |
| "Reset icon" | Programın, klasörün ya da sitenin kendi ikonu yeniden oluşturulur |
| `docs/general/STORE_LISTING.md` | Ad, açıklamalar, anahtar kelimeler, ekran görüntüsü listesi |
| `docs/general/PRIVACY_POLICY.md` | Veri toplanmaz; tek ağ isteği eklenen sitenin `/favicon.ico` dosyası |
| `docs/general/STORE_SUBMISSION.md` | Kimlik, sürüm, build, `runFullTrust` gerekçesi |

---

#### 8.5 Sonuç

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`: Core, Presentation, Infrastructure) | 236/236 |
| UI (Windows Sandbox) | 49/49 (48 ana süreç + 1 ayrı süreç) |
| Sonar | 0 bulgu |

---

#### 8.6 Açık işler

| Konu | Not |
|------|-----|
| Partner Center gönderimi | Kullanıcı; adımlar `STORE_SUBMISSION.md`'de |
| Store ekran görüntüleri | Gerçek içerikle, son build'den alınmalı |
| Sekme sürükleme testinin kök nedeni | Diğer testlerden sonra aynı süreçte sistem sürükle-bırakı başlamıyor; test ayrı süreçte koşuyor (`PHASE7.md` → 7.6.2) |
| Başlama süresi | Birden çok örnekle (sıcak/soğuk) ölçüm, sonra ReadyToRun ya da trimming yeniden denenebilir |
| "Add app" listesinde ikonlar | Liste şu an yalnız ad gösteriyor |
| Klavye ile kart taşıma | Erişilebilirlik; şu an yalnız fare |
| Explorer'dan gerçek sürükleme testi | U3 yalnız ViewModel düzeyinde test edildi |
| MSIX boyutu (97 MB) | Store, Windows App SDK'yı çerçeve paketi olarak verebilir; framework-dependent paket boyutu yarıdan fazla düşürür ama sandbox testinde çerçeve paketinin de kurulmasını gerektirir |

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 8 — UI testleri, performans ve Store paketi" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı. Kod, testler (unit 236/236, UI 49/49), paketler ve dokümanlar 2026-10-30'da hazırdı; Store gönderimi 2026-11-19'da yapıldı. Sonuç: `PHASE8.md` → 8.5 Sonuç.

**Özet:** Uçtan uca test turu, bellek/başlama süresi ölçümü, Store'a hazır paket ve listeleme dokümanları.

**Hedefler:**

- [x] Tüm kabul kriterlerinin testleri geçiyor (1.5'teki tablo)
- [x] Ölçüm: soğuk başlama süresi, boşta bellek (Python sürümüyle karşılaştırmalı)
- [x] Store paketi (x64 + arm64), uygulama ikonları, ekran görüntüleri
- [x] Store listeleme ve gizlilik politikası taslağı (TaskTimerWidget dokümanları örnek alınarak)
- [ ] Partner Center gönderimi kullanıcı tarafından yapılır

**Detay:** `PHASE8.md`
