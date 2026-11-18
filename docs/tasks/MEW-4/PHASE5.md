# Faz 5 — Uygulama ekleme ve otomatik ikon

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Widget'a artık uygulama, klasör ve web sitesi eklenebiliyor. Alttaki "+ Add" menüsünden "App…" seçilince Başlat
menüsündeki bütün uygulamalar aranabilir bir listede çıkıyor; ya da bir yol veya web adresi yazılıyor. Explorer'dan
dosya, klasör ya da tarayıcıdan bağlantı grid'e bırakılınca da kart oluşuyor. Kartlar kendi ikonlarıyla geliyor; karta
tıklayınca program çalışıyor, adres tarayıcıda, klasör Explorer'da açılıyor.

## Problem

- WinUI sürümünde uygulama, klasör ya da web sitesi eklemenin bir yolu yoktu; grid'de yalnız boş kategoriler vardı.
- Eklenen hedeflerin ikonu olmadan kartlar ayırt edilemezdi; Python sürümündeki emoji/ikon/upload sekmeli ikon seçici
  ise bu sürümde olmayacaktı (`MAIN_TODO.md` → Kararlar → K6).
- Taşınmış ya da kaldırılmış bir hedefe tıklayınca ne olacağı tanımlı değildi.

## Çözüm

- **Core (`LaunchTarget`):** Girilen metni URL, klasör, dosya ya da Apps-folder öğesi olarak sınıflar ve ad önerir.
- **Infrastructure:** `ShellAppsSource` kurulu uygulamaları, `ShellIconStore` 64 px ikonları, `FaviconSource`
  sitenin `/favicon.ico` dosyasını, `ShellLauncher` hedefi açmayı sağlar.
- **Presentation:** `AddAppViewModel` arama, seçim ve ekleme; `BoardViewModel` ekleme, bırakma, açma ve silerken ikon
  temizliği.
- **App:** "Add app" penceresi (`AddAppDialog`), alt çubukta "+ Add" menüsü ve bırakma ipucu, karta tıklayınca açma.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 5.1 | Girilen metin web adresi, klasör ya da program olarak tanınır ve kart için ad önerilir. | 🟢 Tamamlandı |
| 5.2 | Kurulu uygulamalar aranabilir bir listeden kendi ikonlarıyla eklenir. | 🟢 Tamamlandı |
| 5.3 | Web sitesi kartı sitenin kendi ikonunu alır, alınamazsa baş harf rozeti gösterir. | 🟢 Tamamlandı |
| 5.4 | "Add app" penceresinde yol ya da web adresi yazılarak kart eklenir. | 🟢 Tamamlandı |
| 5.5 | Grid'e bırakılan dosya, klasör ve bağlantılar kart olur. | 🟢 Tamamlandı (yalnız ViewModel testi) |
| 5.6 | Karta tıklayınca hedef açılır, eksik hedefte uyarı gösterilir. | 🟢 Tamamlandı |
| 5.7 | Kart silinince ikon dosyası da silinir. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Ekleme nereden yapılır? | Pencerenin altında "+ Add" menüsü ve bırakma ipucu | 🟢 Verildi | Kategori "+"'sından ayrı, tek yerden ekleme |
| Uygulama listesi nereden gelir? | `shell:AppsFolder` | 🟢 Verildi | Başlat menüsüyle birebir; Store uygulamaları için kısıtlı yetenek gerekmez |
| Site ikonu nereden alınır? | Yalnız kartın sitesinden `/favicon.ico` | 🟢 Verildi | Üçüncü taraf ikon servisi yok (gizlilik); alınamazsa baş harf rozeti |
| İkon boyutu ne olur? | 64 px PNG | 🟢 Verildi | 36 DIP ikon %175 ölçekte net görünür |
| Eski sekmeli ikon seçici olacak mı? | Hayır | 🟢 Verildi | `MAIN_TODO.md` → Kararlar → K6 |

## Nasıl kontrol edilir

- [ ] Alttaki "+ Add" → "App…" seç, listede "Notepad" ara ve ekle: kart Notepad'in ikonuyla gelmeli.
- [ ] Aynı pencerede `www.youtube.com` yaz: ad "Youtube" önerilmeli, eklenince kart sitenin ikonunu göstermeli.
- [ ] `notepad` ya da `hello world` yaz: "Enter a full path (C:\...) or a web address (https://...)." uyarısı çıkmalı,
  kart eklenmemeli.
- [ ] Explorer'dan bir klasörü grid'e sürükle: klasörün adıyla bir kart oluşmalı.
- [ ] Bir program kartına tıkla: program açılmalı. Programı taşıyıp karta yeniden tıkla: uyarı görünmeli.
- [ ] Bir kartı sil: `icons\` altındaki ikon dosyası da silinmeli.

## Kalan

- Yok. Sonraki fazlara bırakılanlar: kart menüsünde "Rename" (Faz 6'da yapıldı), "Change icon…" ve "Reset icon"
  (Faz 8'de yapıldı), "Add app" listesinde uygulama ikonları (Faz 8'de açık iş olarak kaldı).

## Ayrıntılar

### 5.1 — Girilen metin web adresi, klasör ya da program olarak tanınır ve kart için ad önerilir.

- **Mevcut durum:** Girilen bir metnin ne tür bir hedef olduğunu anlayan bir kod yoktu.
- **Problem:** Yazılan, yapıştırılan ya da bırakılan metnin uygulama kartı olup olmayacağına ve adına karar verilmeli.
- **Çözüm:**
  - `LaunchTarget` (Core) metni Url, Folder, Executable ya da Apps-folder öğesi olarak sınıflar ve ad önerir.
  - `https://github.com/melihcelenk` → Url, "Github"; `www.youtube.com` → `https://www.youtube.com`, "Youtube".
  - Var olan klasör (`C:\Projects`) → Folder, "Projects"; `C:\Windows\System32\cmd.exe` → Executable, "Cmd".
  - Tırnaklı yol (`"C:\Program Files\...\firefox.exe"`) tırnaksız alınır, "Firefox".
  - `shell:AppsFolder\Microsoft.WindowsNotepad_8wekyb3d8bbwe!App` aynen Executable olur, ad uygulama kimliğidir.
  - `notepad`, `hello world`, `ftp://...` eklenmez: "Enter a full path (C:\...) or a web address (https://...)."
- **Dosyalar:** `src/MyEverythingWidget.Core/Apps/LaunchTarget.cs`
- **Testler:** `Core.Tests` → `LaunchTargetTests` (16)
- **Durum:** 🟢 Tamamlandı.

### 5.2 — Kurulu uygulamalar aranabilir bir listeden kendi ikonlarıyla eklenir.

- **Mevcut durum:** Kurulu uygulamaları listeleyen bir servis yoktu.
- **Problem:** Kullanıcı uygulamanın yolunu bilmeden eklemek ister; Store uygulamalarının da listede olması gerekir.
- **Çözüm:**
  - `ShellAppsSource` (Infrastructure) `shell:AppsFolder` içeriğini `IShellItem` ve `IEnumShellItems` ile okur
    (masaüstü ve Store uygulamaları).
  - `ShellIconStore` `IShellItemImageFactory` ile 64 px ikon alır ve PNG olarak `icons\` altına yazar.
  - Arayüzler Core'da: `IInstalledAppsSource`, `IIconStore`, `IAppLauncher`.
  - COM arayüzleri .NET 10 kaynak üreteçli `GeneratedComInterface` ile tanımlıdır (`ComImport` yok; trimming uyumlu).
  - `AddAppViewModel` arama ve seçimi, `BoardViewModel.AddAppAsync` eklemeyi yapar.
- **Dosyalar:** `src/MyEverythingWidget.Core/Apps/AppServices.cs`,
  `src/MyEverythingWidget.Infrastructure/Shell/ShellAppsSource.cs`,
  `src/MyEverythingWidget.Infrastructure/Shell/ShellIconStore.cs`, `src/MyEverythingWidget.Presentation/AddAppViewModel.cs`,
  `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.App/Views/AddAppDialog.xaml`
- **Testler:** `Infrastructure.Tests` → `ShellServicesTests` (U1, U2; makinede, pencere açmaz);
  `Presentation.Tests` → `AppItemsTests`; `UiTests` → `AppItemTests.InstalledApp_PickedFromList_IsAddedWithItsIcon`;
  `ScreenshotTests` → `add-app-dialog.png`, `cards-with-icons.png`
- **Durum:** 🟢 Tamamlandı.

### 5.3 — Web sitesi kartı sitenin kendi ikonunu alır, alınamazsa baş harf rozeti gösterir.

- **Mevcut durum:** Web adresleri için ikon kaynağı yoktu.
- **Problem:** Site kartları ayırt edilebilmeli; üçüncü taraf ikon servisi gizlilik açısından istenmiyor.
- **Çözüm:**
  - `FaviconSource` yalnız kartın sitesinden `/favicon.ico` dosyasını 5 sn zaman aşımıyla alır.
  - Alınamazsa baş harf rozeti gösterilir.
- **Dosyalar:** `src/MyEverythingWidget.Infrastructure/Shell/SiteIconSource.cs` (`FaviconSource`)
- **Testler:** `Infrastructure.Tests` → `ShellServicesTests` (U4 site ikonu)
- **Durum:** 🟢 Tamamlandı.

### 5.4 — "Add app" penceresinde yol ya da web adresi yazılarak kart eklenir.

- **Mevcut durum:** Ekleme girişi yoktu.
- **Problem:** Listede olmayan program, kısayol, klasör ya da site de eklenebilmeli.
- **Çözüm:**
  - Tam yol ya da web adresi yazılır veya "Browse…" ile seçilir; ad önerilir, değiştirilebilir.
  - Giriş noktası pencerenin altındaki "+ Add" menüsü (App…; Faz 6'da Note, Image…).
- **Dosyalar:** `src/MyEverythingWidget.Presentation/AddAppViewModel.cs`, `src/MyEverythingWidget.App/Views/AddAppDialog.xaml`,
  `src/MyEverythingWidget.App/MainWindow.xaml` (alt çubuk)
- **Testler:** `UiTests` → `TypedPath_IsAddedWithSuggestedName`; `Presentation.Tests` → `AppItemsTests`
- **Durum:** 🟢 Tamamlandı.

### 5.5 — Grid'e bırakılan dosya, klasör ve bağlantılar kart olur.

- **Mevcut durum:** Grid bırakılan veriyi kabul etmiyordu.
- **Problem:** Explorer'dan ya da tarayıcıdan sürükleyerek eklemek en hızlı yol.
- **Çözüm:**
  - `BoardViewModel.AddDroppedAsync` bırakılan metinleri `LaunchTarget` ile sınıflar, tanınanları kart yapar,
    diğerlerini bildirir.
  - Alt çubukta "Drop files, folders or links on the grid" ipucu var.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.App/MainWindow.xaml.cs`
  (bırakma işleyicisi), `src/MyEverythingWidget.App/DroppedTexts.cs`
- **Testler:** `Presentation.Tests` → `AppItemsTests.DroppedTexts_AddRecognisedTargetsAndReportOthers`
- **Durum:** 🟢 Tamamlandı (Explorer'dan sandbox içinde sürükleme kararsız olduğu için uçtan uca test edilmedi).

### 5.6 — Karta tıklayınca hedef açılır, eksik hedefte uyarı gösterilir.

- **Mevcut durum:** Kartlar tıklanınca bir şey yapmıyordu.
- **Problem:** Kart bir kısayol gibi çalışmalı; taşınmış ya da kaldırılmış hedefte kullanıcı bilgilendirilmeli.
- **Çözüm:**
  - `ShellLauncher` hedefin varlığını kontrol eder ve kabuk üzerinden açar: program çalışır, adres tarayıcıda,
    klasör Explorer'da açılır.
  - Hedef yoksa uyarı gösterilir (`BoardViewModel.Launch`).
- **Dosyalar:** `src/MyEverythingWidget.Infrastructure/Shell/ShellLauncher.cs`, `src/MyEverythingWidget.Presentation/BoardViewModel.cs`
- **Testler:** `UiTests` → `ClickingAppCard_StartsTheProgram` (cmd.exe gerçekten başlar),
  `ClickingCardOfRemovedProgram_ShowsWarning`; `Infrastructure.Tests` → `ShellServicesTests` (U6 eksik hedef)
- **Durum:** 🟢 Tamamlandı.

### 5.7 — Kart silinince ikon dosyası da silinir.

- **Mevcut durum:** Oluşturulan ikonlar `icons\` altında birikebilirdi.
- **Problem:** Silinen kartların ikonları veri klasöründe gereksiz yer tutar.
- **Çözüm:** `BoardViewModel` kart silinirken ikon dosyasını da siler.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`
- **Testler:** `Presentation.Tests` → `AppItemsTests`
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Sürükle-bırak (U3):** Uçtan uca test edilmedi; Explorer'dan sandbox içinde sürükleme kararsız olur. Bırakılan
  verinin karta dönüşmesi `AppItemsTests.DroppedTexts_AddRecognisedTargetsAndReportOthers` ile test edildi.
- **Kararsız test:** `ClickingAppCard_StartsTheProgram` bir tam koşuda kırmızıydı, tek başına yeşildi. Uygulama açılır
  açılmaz tıklanıyordu; tıklamadan önce arayüzün oturması bekleniyor ve başarısızlıkta ekran görüntüsü alınıyor.
  Sonraki tam koşu 33/33.
- **Sandbox Notepad'i:** Sandbox'ın `notepad.exe` dosyası ikonsuz bir yönlendiricidir; kartı baş harf rozetiyle gelir
  (beklenen davranış).
- **Testler:** Unit 170/170 (Core, Presentation, Infrastructure), UI 33/33 (Sandbox), Sonar 0 bulgu.

### Referanslar

- `MAIN_TODO.md` → Faz 5 — Uygulama ekleme ve otomatik ikon
- `MAIN_TODO.md` → Kararlar → K6
- `PHASE4.md` (önceki faz) · `PHASE6.md` (Notlar, resimler ve Ctrl+V)
- `PHASE8.md` → Ayrıntılar ("Change icon…", "Reset icon")

### Önceki doküman içeriği

> Önce: `PHASE4.md` · Sonra: `PHASE6.md` (Notlar, resimler ve Ctrl+V)

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `LaunchTarget` sınıflandırıcı (Core) | 🟢 Tamamlandı | U3, U4 |
| `MyEverythingWidget.Infrastructure` (kabuk, ikon, başlatıcı, site ikonu) | 🟢 Tamamlandı | U1, U2, U5, U6 |
| "Add app" penceresi, alt çubuk, karta tıklayınca açma, sürükle-bırak | 🟢 Tamamlandı | |

---

#### 5.1 Kapsam

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

#### 5.2 Yapı

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

#### 5.3 Hedef türleri

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

#### 5.4 Tasarım kararları

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Ekleme girişi | Pencerenin altında "+ Add" menüsü (App…; Faz 6'da Note, Image…) ve "Drop files, folders or links on the grid" ipucu | Kategori "+"'sından ayrı, tek yerden ekleme |
| Uygulama listesi | `shell:AppsFolder` | Başlat menüsüyle birebir; Store uygulamaları için kısıtlı yetenek gerekmez |
| Site ikonu | Yalnız kartın sitesinden `/favicon.ico` | Üçüncü taraf ikon servisi yok (gizlilik); alınamazsa baş harf rozeti |
| İkon boyutu | 64 px PNG | 36 DIP ikon %175 ölçekte net görünür |

---

#### 5.5 Testler

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

#### 5.6 Sonuç

Faz 5 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`: Core, Presentation, Infrastructure) | 170/170 |
| UI (Sandbox) | 33/33 |
| Sonar | 0 bulgu |

##### 5.6.1 Notlar

- `ClickingAppCard_StartsTheProgram` bir tam koşuda kırmızıydı, tek başına yeşildi. Uygulama açılır açılmaz tıklanıyordu;
  tıklamadan önce arayüzün oturması bekleniyor ve başarısızlıkta ekran görüntüsü alınıyor. Sonraki tam koşu 33/33.
- Sandbox'ın `notepad.exe` dosyası ikonsuz bir yönlendiricidir; kartı baş harf rozetiyle gelir (beklenen davranış).

##### 5.6.2 Sonraki fazlara bırakılanlar

| Konu | Faz | Not |
|------|-----|-----|
| Kart menüsünde "Rename" | Faz 6 | Not düzenlemeyle aynı satır içi düzenleyiciyi kullanır |
| Kart menüsünde "Change icon…", "Reset icon" | Faz 8 | |
| "Add app" listesinde uygulama ikonları | Faz 8 | Şu an yalnız adlar; ikonlar gecikmeli yüklenebilir |

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 5 — Uygulama ekleme ve otomatik ikon" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 170/170, UI 33/33 (Sandbox). Sonuç: `PHASE5.md` → 5.6 Sonuç.

**Özet:** Kurulu uygulama seçici, sürükle-bırakla ekleme, otomatik ikon, başlatma.

**Hedefler:**

- [x] `InstalledAppsService` (Win32 + Store, arama) (U1)
- [x] `IconService`: exe, lnk, klasör, Store uygulaması, favicon, baş harf yedeği (U2, U4)
- [x] Widget'a dosya/URL bırakma (U3, U4)
- [x] `LauncherService`: EXE, URL, klasör; eksik hedef uyarısı (U5, U6)
- [x] Kart menüsü: Open, Edit, Rename, Change icon..., Reset icon, Delete — Rename Faz 6, Change/Reset icon Faz 8

**Detay:** `PHASE5.md`
