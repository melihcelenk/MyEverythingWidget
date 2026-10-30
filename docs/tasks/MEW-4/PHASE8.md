# MEW-4 Faz 8 — UI testleri, performans ve Store paketi

> Önce: `PHASE7.md` · Sonra: Partner Center gönderimi (kullanıcı, `docs/general/STORE_SUBMISSION.md`)

## İçindekiler

- Durum Panosu
- 8.1 Kabul kriterlerinin kapsamı
- 8.2 Performans
- 8.3 Store paketi
- 8.4 Eklenenler
- 8.5 Sonuç
- 8.6 Açık işler

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| Bütün kabul kriterlerinin testleri | 🟢 Tamamlandı | 8.1 |
| Başlama süresi ve bellek ölçümü | 🟢 Tamamlandı | 8.2 |
| x64 ve ARM64 MSIX, ikon seti | 🟢 Tamamlandı | 8.3 |
| Store listeleme, gizlilik politikası, gönderim adımları | 🟢 Tamamlandı | `docs/general/STORE_*.md`, `PRIVACY_POLICY.md` |
| Kart menüsü: "Change icon…", "Reset icon" | 🟢 Tamamlandı | Faz 5'ten kalan |
| Partner Center gönderimi | ⏳ Bekliyor | Kullanıcının hesabıyla yapılır |

---

## 8.1 Kabul kriterlerinin kapsamı

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

## 8.2 Performans

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

## 8.3 Store paketi

- `scripts/publish-msix.ps1 -Platform x64|ARM64`: imzasız tek `.msix`, bütün ikon ölçekleri içinde. Boyut: x64 97 MB,
  ARM64 95 MB (self-contained .NET ve Windows App SDK).
- Betik önce `dotnet clean` çalıştırır; artımlı build bazen paketi yeni klasöre yazmıyordu.
- İkon seti: `Square44x44Logo` için 16-256 px hedef boyutlar (plated, unplated, light-unplated), diğer logolar için
  %100-%400 ölçekler; `app.ico` exe'ye ve pencereye bağlı.
- Store kimliği (Partner Center), sürüm ve gönderim: `docs/general/STORE_SUBMISSION.md`.

---

## 8.4 Eklenenler

| Konu | Not |
|------|-----|
| "Change icon…" | Seçilen resim 64 px PNG olarak `icons\` altına alınır; eski ikon silinir |
| "Reset icon" | Programın, klasörün ya da sitenin kendi ikonu yeniden oluşturulur |
| `docs/general/STORE_LISTING.md` | Ad, açıklamalar, anahtar kelimeler, ekran görüntüsü listesi |
| `docs/general/PRIVACY_POLICY.md` | Veri toplanmaz; tek ağ isteği eklenen sitenin `/favicon.ico` dosyası |
| `docs/general/STORE_SUBMISSION.md` | Kimlik, sürüm, build, `runFullTrust` gerekçesi |

---

## 8.5 Sonuç

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`: Core, Presentation, Infrastructure) | 236/236 |
| UI (Windows Sandbox) | 49/49 (48 ana süreç + 1 ayrı süreç) |
| Sonar | 0 bulgu |

---

## 8.6 Açık işler

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
