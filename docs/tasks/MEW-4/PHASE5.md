# MEW-4 Faz 5 — Uygulama ekleme ve otomatik ikon

> Önce: `PHASE4.md` · Sonra: `PHASE6.md` (Notlar, resimler ve Ctrl+V)

## İçindekiler

- Durum Panosu
- 5.1 Kapsam
- 5.2 Yapı
- 5.3 Hedef türleri
- 5.4 Tasarım kararları
- 5.5 Testler
- 5.6 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `LaunchTarget` sınıflandırıcı (Core) | 🟢 Tamamlandı | U3, U4 |
| `MyEverythingWidget.Infrastructure` (kabuk, ikon, başlatıcı, site ikonu) | 🟢 Tamamlandı | U1, U2, U5, U6 |
| "Add app" penceresi, alt çubuk, karta tıklayınca açma, sürükle-bırak | 🟢 Tamamlandı | |

---

## 5.1 Kapsam

- **Kurulu uygulamalar:** Başlat menüsündeki tüm uygulamalar (masaüstü ve Store) aranabilir listede; seçilen uygulama
  kendi ikonuyla eklenir.
- **Yol ya da adres:** Tam yol (program, kısayol, klasör) ya da web adresi yazılır veya "Browse…" ile seçilir; ad
  önerilir, değiştirilebilir.
- **Sürükle-bırak:** Explorer'dan dosya, klasör ya da tarayıcıdan bağlantı grid'e bırakılınca kart oluşur.
- **Açma:** Karta tıklayınca program çalışır, adres tarayıcıda, klasör Explorer'da açılır.
- **Eksik hedef:** Taşınmış ya da kaldırılmış hedefte uyarı gösterilir.
- **İkon temizliği:** Kart silinince ikon dosyası da silinir.

Emoji/ikon/upload sekmeli eski ikon seçici yoktur (`MAIN_TODO.md` → Kararlar → K6).

---

## 5.2 Yapı

| Tür | Katman | Görev |
|-----|--------|-------|
| `LaunchTarget` | Core | Metni URL, klasör, dosya ya da Apps-folder öğesi olarak sınıflar, ad önerir |
| `IInstalledAppsSource`, `IIconStore`, `IAppLauncher` | Core | Windows servislerinin arayüzleri |
| `AddAppViewModel` | Presentation | Arama, seçim, elle hedef, ad önerisi, ekleme |
| `BoardViewModel` | Presentation | `AddAppAsync`, `AddDroppedAsync`, `Launch`, silerken ikon temizliği |
| `ShellAppsSource` | Infrastructure | `shell:AppsFolder` içeriği (`IShellItem`, `IEnumShellItems`) |
| `ShellIconStore` | Infrastructure | `IShellItemImageFactory` ile 64 px ikon, PNG olarak `icons\` altına |
| `FaviconSource` | Infrastructure | Sitenin `/favicon.ico` dosyası, 5 sn zaman aşımı |
| `ShellLauncher` | Infrastructure | Hedefin varlığını kontrol eder, kabuk üzerinden açar |
| `AddAppDialog`, alt çubuk | App | Arayüz |

COM arayüzleri .NET 10 kaynak üreteçli `GeneratedComInterface` ile tanımlıdır (`ComImport` yok; trimming uyumlu).

---

## 5.3 Hedef türleri

| Girilen | Tür | Hedef | Önerilen ad |
|---------|-----|-------|-------------|
| `https://github.com/melihcelenk` | Url | aynen | `Github` |
| `www.youtube.com` | Url | `https://www.youtube.com` | `Youtube` |
| `C:\Projects` (var olan klasör) | Folder | aynen | `Projects` |
| `C:\Windows\System32\cmd.exe` | Executable | aynen | `Cmd` |
| `"C:\Program Files\...\firefox.exe"` | Executable | tırnaksız | `Firefox` |
| `shell:AppsFolder\Microsoft.WindowsNotepad_8wekyb3d8bbwe!App` | Executable | aynen | uygulama kimliği |
| `notepad`, `hello world`, `ftp://...` | — | eklenmez, "Enter a full path (C:\...) or a web address (https://...)." | — |

---

## 5.4 Tasarım kararları

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Ekleme girişi | Pencerenin altında "+ Add" menüsü (App…; Faz 6'da Note, Image…) ve "Drop files, folders or links on the grid" ipucu | Kategori "+"'sından ayrı, tek yerden ekleme |
| Uygulama listesi | `shell:AppsFolder` | Başlat menüsüyle birebir; Store uygulamaları için kısıtlı yetenek gerekmez |
| Site ikonu | Yalnız kartın sitesinden `/favicon.ico` | Üçüncü taraf ikon servisi yok (gizlilik); alınamazsa baş harf rozeti |
| İkon boyutu | 64 px PNG | 36 DIP ikon %175 ölçekte net görünür |

---

## 5.5 Testler

| Kabul kriteri | Test |
|---------------|------|
| U3, U4 sınıflandırma | `Core.Tests` → `LaunchTargetTests` (16) |
| U1-U6 mantık | `Presentation.Tests` → `AppItemsTests` (14) |
| U1 kurulu uygulamalar, U2 ikon, U4 site ikonu, U6 eksik hedef (gerçek Windows) | `Infrastructure.Tests` → `ShellServicesTests` (12, makinede, pencere açmaz) |
| U1, U2 uçtan uca | `UiTests` → `AppItemTests.InstalledApp_PickedFromList_IsAddedWithItsIcon` |
| Yol yazarak ekleme | `UiTests` → `TypedPath_IsAddedWithSuggestedName` |
| U5 | `UiTests` → `ClickingAppCard_StartsTheProgram` (cmd.exe gerçekten başlar) |
| U6 | `UiTests` → `ClickingCardOfRemovedProgram_ShowsWarning` |
| Görsel | `ScreenshotTests` → `add-app-dialog.png`, `cards-with-icons.png` |

Sürükle-bırak (U3) uçtan uca test edilmedi; Explorer'dan sandbox içinde sürükleme kararsız olur. Bırakılan verinin
karta dönüşmesi `AppItemsTests.DroppedTexts_AddRecognisedTargetsAndReportOthers` ile test edilir.

---

## 5.6 Sonuç

Faz 5 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`: Core, Presentation, Infrastructure) | 170/170 |
| UI (Sandbox) | 33/33 |
| Sonar | 0 bulgu |

### 5.6.1 Notlar

- `ClickingAppCard_StartsTheProgram` bir tam koşuda kırmızıydı, tek başına yeşildi. Uygulama açılır açılmaz tıklanıyordu;
  tıklamadan önce arayüzün oturması bekleniyor ve başarısızlıkta ekran görüntüsü alınıyor. Sonraki tam koşu 33/33.
- Sandbox'ın `notepad.exe` dosyası ikonsuz bir yönlendiricidir; kartı baş harf rozetiyle gelir (beklenen davranış).

### 5.6.2 Sonraki fazlara bırakılanlar

| Konu | Faz | Not |
|------|-----|-----|
| Kart menüsünde "Rename" | Faz 6 | Not düzenlemeyle aynı satır içi düzenleyiciyi kullanır |
| Kart menüsünde "Change icon…", "Reset icon" | Faz 8 | |
| "Add app" listesinde uygulama ikonları | Faz 8 | Şu an yalnız adlar; ikonlar gecikmeli yüklenebilir |
