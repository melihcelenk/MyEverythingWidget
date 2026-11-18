# Faz 1 — İskelet, pencere ve MSIX

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Bu fazda WinUI ile boş ama gerçek bir widget penceresi kuruldu: özel başlık çubuğu, pin ve kapat düğmeleri, Mica
arka plan. Pencerenin konumu, boyutu ve always-on-top durumu kapatıp açınca hatırlanıyor; uygulama ikinci kez
başlatılırsa yeni pencere açılmıyor, mevcut pencere öne geliyor. Testler üç katmanda (Core, Presentation, Sandbox'ta
UI) koşuyor ve uygulama MSIX paketi olarak üretilebiliyor. Grid, kart ve kategori bu fazda yok (Faz 2-4).

## Problem

- WinUI sürümü için henüz proje, pencere ve test altyapısı yoktu; sonraki fazların üzerine kurulacağı bir iskelet
  gerekiyordu.
- `MAIN_TODO.md` ViewModel'leri App projesinde gösteriyordu; bu haliyle ViewModel testleri WinUI çalışma zamanı
  olmadan koşamazdı.
- UI testleri kullanıcının masaüstünde koşmamalıydı; bunun için Windows Sandbox'ta çalışan bir koşucu gerekiyordu.
- Store için MSIX paketi, geliştirme ve test için ise sertifika ve runtime kurulumu gerektirmeyen bir yol gerekiyordu.

## Çözüm

- **Proje yapısı:** `Core`, `Presentation` ve `App` projeleri ile üç test projesi açıldı; solution uyarısız derleniyor.
- **Pencere (`MainWindow`):** Özel başlık çubuğu, pin, kapat ve Mica; konum, boyut ve pin kalıcı; uygulama tek kopya
  çalışıyor.
- **Ayarlar (`JsonSettingsStore`):** Atomik yazma; dosya yoksa ya da bozuksa varsayılanlarla açılış, bozuk dosyanın
  yedeği.
- **ViewModel'ler (`Presentation`):** WinUI'a bağımlı değil; pencere işlemleri `IWindowService` ile soyutlandı.
- **Sandbox koşucusu (`scripts/test-ui.ps1`):** UI testlerini Windows Sandbox'ta koşturup sonucu dışarı yazıyor.
- **MSIX:** Store için aynı proje MSIX olarak publish ediliyor; testler paketsiz, self-contained build ile koşuyor.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 1.1 | Proje yapısı kurulur ve solution uyarısız derlenir. | 🟢 Tamamlandı |
| 1.2 | Pencere pin, konum hatırlama ve tek kopya ile çalışır. | 🟢 Tamamlandı (F1.1-F1.9) |
| 1.3 | Ayarlar, pencere konumu ve ViewModel için unit testler yazılır. | 🟢 Tamamlandı (19/19) |
| 1.4 | Pencere davranışı Sandbox'ta FlaUI UI testleriyle doğrulanır. | 🟢 Tamamlandı (8/8, Sandbox'ta) |
| 1.5 | Sandbox koşucusu UI testlerini kullanıcı masaüstüne dokunmadan çalıştırır. | 🟢 Tamamlandı |
| 1.6 | Uygulama imzasız bir MSIX paketi olarak üretilir. | 🟢 Tamamlandı (Sandbox'ta kurulup açıldı) |
| 1.7 | Kök `CLAUDE.md`, `README.md` ve `legacy` yolları güncellenir. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| ViewModel'ler ayrı bir projede mi durur? | `Presentation` projesi | 🟢 Verildi | Ayrıntılar → Önceki doküman içeriği → Karar 1 |
| Geliştirme, test ve Store için paket biçimi ne olur? | Test için paketsiz, Store için MSIX | 🟢 Verildi | Ayrıntılar → Önceki doküman içeriği → Karar 2 |

## Nasıl kontrol edilir

- [ ] Uygulamayı aç: "My Everything Widget" başlıklı tek bir pencere görünmeli; başlık çubuğunda pin ve kapat
  düğmeleri olmalı.
- [ ] Pin düğmesine bas ve başka bir pencereye tıkla: widget üstte kalmalı. Tekrar bas: normal pencereye dönmeli.
- [ ] Pin açıkken uygulamayı kapatıp yeniden aç: pencere yine always-on-top açılmalı.
- [ ] Pencereyi ekranda başka bir yere taşı, kapat ve yeniden aç: aynı konumda açılmalı.
- [ ] Uygulama açıkken ikinci kez başlat: yeni pencere açılmamalı, mevcut pencere öne gelmeli.
- [ ] Ayar dosyasını sil ve uygulamayı aç: 404x480 boyutunda, birincil ekranın sağ üst köşesinde, pin kapalı açılmalı.
- [ ] Ayar dosyasının içini boz ve uygulamayı aç: varsayılanlarla açılmalı; klasörde `settings.corrupt-<zaman>.json`
  yedeği olmalı.

## Kalan

- Yok.

## Ayrıntılar

### 1.1 — Proje yapısı kurulur ve solution uyarısız derlenir.

- **Mevcut durum:** WinUI sürümü için proje yoktu; Python sürümü `legacy/` altındaydı.
- **Problem:** Sonraki fazlar için katmanları ayrılmış bir solution gerekiyordu.
- **Çözüm:**
  - `src/MyEverythingWidget.Core` (`net10.0`, bağımlılık yok): modeller, ayarlar, JSON depolama.
  - `src/MyEverythingWidget.Presentation` (`net10.0`, Core ve CommunityToolkit.Mvvm): ViewModel'ler; WinUI'a bağımlı
    değil.
  - `src/MyEverythingWidget.App` (`net10.0-windows10.0.26100.0`, Core, Presentation, Windows App SDK): WinUI View'lar,
    pencere servisleri, MSIX.
  - Test projeleri: `tests/MyEverythingWidget.Core.Tests`, `tests/MyEverythingWidget.Presentation.Tests` (`net10.0`,
    xunit.v3) ve `tests/MyEverythingWidget.UiTests` (`net10.0-windows`, xunit.v3, FlaUI).
  - `MAIN_TODO.md` → "Planlanan Yapı"dan iki fark: ViewModel'ler ayrı `Presentation` projesinde (Karar 1);
    `Infrastructure` projesi ilk ihtiyaç duyulan fazda (Faz 5) açılır.
- **Dosyalar:** `src/MyEverythingWidget.Core`, `src/MyEverythingWidget.Presentation`, `src/MyEverythingWidget.App`,
  `tests/MyEverythingWidget.Core.Tests`, `tests/MyEverythingWidget.Presentation.Tests`, `tests/MyEverythingWidget.UiTests`
- **Testler:** Solution uyarısız derleniyor (`TreatWarningsAsErrors`).
- **Durum:** 🟢 Tamamlandı.

### 1.2 — Pencere pin, konum hatırlama ve tek kopya ile çalışır.

- **Mevcut durum:** Pencere yoktu.
- **Problem:** Widget'ın temel pencere davranışları (F1.1-F1.9) gerekiyordu.
- **Çözüm:**
  - F1.1: "My Everything Widget" başlıklı tek pencere; başlık çubuğunda pin ve kapat.
  - F1.2, F1.3: Pin always-on-top'u açıp kapatır ve kalıcıdır.
  - F1.4, F1.5: Konum hatırlanır; kayıtlı konum hiçbir ekranda görünmüyorsa pencere birincil ekranda görünür bir
    konumda açılır (`WindowPlacement`).
  - F1.6: İkinci başlatmada ikinci işlem kapanır, mevcut pencere öne gelir.
  - F1.7: Kapat düğmesi uygulamayı kapatır ve ayarları kaydeder.
  - F1.8, F1.9: Ayar dosyası yoksa varsayılanlar (pin kapalı, 404x480, birincil ekranın sağ üst köşesi); bozuksa
    varsayılanlar ve `settings.corrupt-<zaman>.json` yedeği.
  - `DisplayArea.FindAll()` sonucu LINQ ile gezilemediği için (açılışta `InvalidCastException`) liste indeksle
    dolaşılıyor (`MainWindow.GetWorkAreas`).
  - Yakalanmayan hatalar `logs\crash.log`'a yazılıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml`, `src/MyEverythingWidget.App/MainWindow.xaml.cs`,
  `src/MyEverythingWidget.App/App.xaml.cs`, `src/MyEverythingWidget.App/CrashLog.cs`,
  `src/MyEverythingWidget.Core/Geometry/WindowPlacement.cs`, `src/MyEverythingWidget.Core/Settings/JsonSettingsStore.cs`,
  `src/MyEverythingWidget.Presentation/MainViewModel.cs`
- **Testler:** `UiTests` → `MainWindowTests` (F1.1, F1.2, F1.3, F1.4, F1.6, F1.7, F1.9 uçtan uca); mantık testleri 1.3'te.
- **Durum:** 🟢 Tamamlandı.

### 1.3 — Ayarlar, pencere konumu ve ViewModel için unit testler yazılır.

- **Mevcut durum:** Test yoktu.
- **Problem:** Pencere mantığı WinUI çalışma zamanı olmadan, normal `dotnet test` ile doğrulanmalıydı.
- **Çözüm:**
  - `Core.Tests` → `JsonSettingsStoreTests`: F1.8, F1.9 ve atomik yazma.
  - `Core.Tests` → `WindowPlacementTests`: F1.5.
  - `Presentation.Tests` → `MainViewModelTests`: F1.2, F1.3, F1.4, F1.7 (mantık).
- **Dosyalar:** `tests/MyEverythingWidget.Core.Tests/Settings/JsonSettingsStoreTests.cs`,
  `tests/MyEverythingWidget.Core.Tests/Geometry/WindowPlacementTests.cs`,
  `tests/MyEverythingWidget.Presentation.Tests/MainViewModelTests.cs`
- **Testler:** `Core.Tests` 13/13, `Presentation.Tests` 6/6 (makinede `dotnet test`).
- **Durum:** 🟢 Tamamlandı.

### 1.4 — Pencere davranışı Sandbox'ta FlaUI UI testleriyle doğrulanır.

- **Mevcut durum:** Gerçek pencereyi test eden bir altyapı yoktu.
- **Problem:** Pin, konum, tek kopya ve kapatma gerçek pencerede uçtan uca doğrulanmalıydı.
- **Çözüm:**
  - `UiTests` → `MainWindowTests` (F1.1, F1.2, F1.3, F1.4, F1.6, F1.7, F1.9) ve `PackagedAppTests` (MSIX kurulumu ve
    paket veri klasörü).
  - Testler fare kullanmıyor (UI Automation pattern'leri ve Win32).
  - UI testleri kod yazıldıktan sonra yazıldığı için bozma (mutation) denemesi yapıldı: pin, konum kaydı ve tek kopya
    kontrolü geçici olarak bozuldu; beklenen 5 test kırmızı oldu, bozulmayan davranışların 2 testi yeşil kaldı; kod geri
    alındı.
  - Solution düzeyindeki `dotnet test` UI testlerini bir kez geliştirici masaüstünde koşturdu (fare ve klavyeye
    dokunulmadı). `SandboxGuard` eklendi: UI testleri yalnız `MEW_UI_TEST_SANDBOX=1` iken uygulamayı açıyor, aksi halde
    atlanıyor.
- **Dosyalar:** `tests/MyEverythingWidget.UiTests/MainWindowTests.cs`, `tests/MyEverythingWidget.UiTests/PackagedAppTests.cs`,
  `tests/MyEverythingWidget.UiTests/Infrastructure/SandboxGuard.cs`
- **Testler:** `UiTests` 8/8 (Windows Sandbox, `scripts/test-ui.ps1`).
- **Durum:** 🟢 Tamamlandı.

### 1.5 — Sandbox koşucusu UI testlerini kullanıcı masaüstüne dokunmadan çalıştırır.

- **Mevcut durum:** UI testlerini izole ortamda koşturan bir betik yoktu.
- **Problem:** UI testleri kullanıcının masaüstünde koşmamalı, faresine ve klavyesine dokunmamalı.
- **Çözüm:**
  - Betik App ve UiTests'i self-contained publish eder (Sandbox'ta .NET kurmaya gerek kalmaz).
  - `tmp/sandbox/` altına `.wsb` yazar: publish klasörleri salt okunur, sonuç klasörü yazılabilir.
  - `WindowsSandbox.exe` ile Sandbox'ı başlatır; içeride `LogonCommand` testleri koşturur, sonucu ve ekran
    görüntülerini sonuç klasörüne yazar.
  - Sonuç dosyası gelene kadar bekler, Sandbox'ı dışarıdan kapatır, özeti yazdırır. İçeriden `shutdown` Sandbox
    penceresini bir kapanış ekranında bırakıp kullanıcıdan "Kapat" beklediği için kaldırıldı.
- **Dosyalar:** `scripts/test-ui.ps1`
- **Testler:** Kullanıcı müdahalesi olmadan koşu bitti, geride Sandbox süreci kalmadı. Sandbox penceresi küçültülmüşken
  FlaUI testleri sorunsuz çalıştı (S2 riski).
- **Durum:** 🟢 Tamamlandı.

### 1.6 — Uygulama imzasız bir MSIX paketi olarak üretilir.

- **Mevcut durum:** Paket yoktu.
- **Problem:** Uygulama Microsoft Store'a MSIX olarak gidecek; geliştirme ve test ise sertifika ve runtime kurulumu
  istememeli.
- **Çözüm:**
  - Testler self-contained ve paketsiz (`WindowsPackageType=None`) build ile koşuyor; Sandbox'a yalnız klasör
    kopyalanıyor.
  - Store için aynı proje MSIX olarak publish ediliyor.
  - Veri klasörü: MSIX'te paketin yerel klasörü (`ApplicationData.Current.LocalFolder`), paketsizde
    `%LOCALAPPDATA%\MyEverythingWidget.WinUI`, testte `MEW_DATA_DIR`. Eski Python verisi
    (`%LOCALAPPDATA%\MyEverythingWidget\app_state.json`) ile karışmaz.
- **Dosyalar:** `src/MyEverythingWidget.App/Package.appxmanifest`, `scripts/publish-msix.ps1`
- **Testler:** `UiTests` → `PackagedAppTests` (MSIX kurulumu ve paket veri klasörü); paket Sandbox'ta kurulup açıldı.
- **Durum:** 🟢 Tamamlandı (imzasız).

### 1.7 — Kök `CLAUDE.md`, `README.md` ve `legacy` yolları güncellenir.

- **Mevcut durum:** Kök dokümanlar Python sürümünü anlatıyordu.
- **Problem:** Python sürümü `legacy/` altına taşındığı için yollar ve anlatım WinUI sürümüne göre güncellenmeliydi.
- **Çözüm:** Kök `CLAUDE.md` ve `README.md` WinUI sürümünü anlatıyor; `legacy` yolları düzeltildi.
- **Dosyalar:** `CLAUDE.md`, `README.md`
- **Testler:** —
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **F1.5 uçtan uca:** Sandbox'ta tek monitör olduğu için uçtan uca test yok; yalnız Core unit testi
  (`WindowPlacementTests`) var.
- **Gerçek fare sürüklemesi:** Bu fazdaki testler fare kullanmıyor; ilk kez Faz 3'te denenecekti.
- **Sonraki fazlara bırakılanlar:**
  - Açılışta pin düğmesinde klavye odak çerçevesi görünüyor → Faz 3 (UI cilası).
  - MSIX self-contained (97 MB); Store için framework bağımlı paket değerlendirilecek → Faz 8.
  - Geçici logolar (`Assets/*.png`) → Faz 8.
  - Store publisher kimliği (şu an imzasız paket OID'i) → Faz 8.

### Referanslar

- `MAIN_TODO.md` → Faz 1 — İskelet, pencere ve MSIX
- `PHASE2.md` → Faz 2 — Grid motoru, durum ve kalıcılık (sonraki faz)
- Önceki doküman içeriği aşağıdadır; oradaki bölüm numaraları (1.1 Kapsam … 1.7 Sonuç) eski numaralardır, yukarıdaki
  alt faz numaralarıyla aynı değildir.

### Önceki doküman içeriği

> Önce: `MAIN_TODO.md` → Faz 1 · Sonra: `PHASE2.md` (Grid motoru, durum ve kalıcılık)

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| 1.2 Proje yapısı ve build | 🟢 Tamamlandı | Solution uyarısız derleniyor |
| 1.3 Pencere, pin, konum hatırlama, tek kopya | 🟢 Tamamlandı | F1.1-F1.9 |
| 1.4 Unit testler | 🟢 Tamamlandı | 19/19 |
| 1.4 UI testleri (FlaUI) | 🟢 Tamamlandı | 8/8, Sandbox'ta |
| 1.5 Sandbox koşucusu | 🟢 Tamamlandı | `scripts/test-ui.ps1` |
| MSIX paketi | 🟢 Tamamlandı | İmzasız; Sandbox'ta kurulup açıldı |
| Kök `CLAUDE.md`, `README.md`, `legacy` yolları | 🟢 Tamamlandı | |

Durum etiketleri `MAIN_TODO.md` → Genel İlerleme ile aynıdır.

---

#### 1.1 Kapsam

- Boş ama gerçek bir widget penceresi açılır: özel başlık çubuğu, pin, kapat, Mica.
- Pencere ayarları (konum, boyut, always-on-top) kalıcıdır.
- Uygulama tek kopya çalışır.
- Testler üç katmanda koşar: Core, Presentation, UI (Sandbox).
- MSIX paketi üretilir.

Grid, kart ve kategori bu fazın kapsamında değildir (Faz 2-4).

---

#### 1.2 Proje yapısı

| Proje | Hedef | Bağımlılık | İçerik |
|-------|-------|------------|--------|
| `src/MyEverythingWidget.Core` | `net10.0` | yok | Modeller, ayarlar, JSON depolama |
| `src/MyEverythingWidget.Presentation` | `net10.0` | Core, CommunityToolkit.Mvvm | ViewModel'ler; WinUI'a bağımlı değil |
| `src/MyEverythingWidget.App` | `net10.0-windows10.0.26100.0` | Core, Presentation, Windows App SDK | WinUI View'lar, pencere servisleri, MSIX |
| `tests/MyEverythingWidget.Core.Tests` | `net10.0` | xunit.v3 | Core testleri |
| `tests/MyEverythingWidget.Presentation.Tests` | `net10.0` | xunit.v3 | ViewModel testleri |
| `tests/MyEverythingWidget.UiTests` | `net10.0-windows` | xunit.v3, FlaUI | Gerçek pencere testleri |

`MAIN_TODO.md` → "Planlanan Yapı"dan iki fark var (bkz. 1.6 Kararlar):

- ViewModel'ler ayrı bir `Presentation` projesinde.
- `Infrastructure` projesi ilk ihtiyaç duyulan fazda (Faz 5) açılır.

---

#### 1.3 Kabul kriterleri

| # | Kriter |
|---|--------|
| F1.1 | Uygulama açıldığında "My Everything Widget" başlıklı tek bir pencere görünür; başlık çubuğunda pin ve kapat düğmeleri vardır. |
| F1.2 | Pin kapalıyken düğmeye basılınca pencere always-on-top olur; tekrar basılınca normal pencereye döner. |
| F1.3 | Pin açıkken uygulama kapatılıp yeniden açılırsa pencere yine always-on-top açılır. |
| F1.4 | Pencere taşınıp (örnek: ekranda 300, 200 konumuna) kapatılırsa yeniden açılışta aynı konumda açılır. |
| F1.5 | Kayıtlı konum artık hiçbir ekranda görünmüyorsa (örnek: kaldırılmış ikinci monitör) pencere birincil ekranda görünür bir konumda açılır. |
| F1.6 | Uygulama açıkken ikinci kez başlatılırsa yeni pencere açılmaz, ikinci işlem kapanır ve mevcut pencere öne gelir. |
| F1.7 | Kapat düğmesi uygulamayı kapatır ve ayarları kaydeder. |
| F1.8 | Ayar dosyası yoksa varsayılanlarla açılır (pin kapalı, 404x480, birincil ekranın sağ üst köşesi). |
| F1.9 | Ayar dosyası bozuksa uygulama varsayılanlarla açılır; bozuk dosya `settings.corrupt-<zaman>.json` olarak saklanır. |

---

#### 1.4 Testler

| Kabul kriteri | Test |
|---------------|------|
| F1.8, F1.9 | `Core.Tests` → `JsonSettingsStoreTests` |
| Atomik yazma | `Core.Tests` → `JsonSettingsStoreTests` |
| F1.5 | `Core.Tests` → `WindowPlacementTests` |
| F1.2, F1.3, F1.4, F1.7 (mantık) | `Presentation.Tests` → `MainViewModelTests` |
| F1.1, F1.2, F1.3, F1.4, F1.6, F1.7, F1.9 (uçtan uca) | `UiTests` → `MainWindowTests` |
| MSIX kurulumu ve paket veri klasörü | `UiTests` → `PackagedAppTests` |
| F1.5 (uçtan uca) | Test yok; Sandbox'ta tek monitör var. Yalnız Core unit testi. |

---

#### 1.5 Sandbox koşucusu

Planlanan akış (sonuç 1.7'ye yazılır):

```
scripts/test-ui.ps1
  1. App ve UiTests'i self-contained publish eder (sandbox'ta .NET kurmaya gerek kalmaz)
  2. tmp/sandbox/ altına .wsb yazar: publish klasörleri salt okunur, sonuç klasörü yazılabilir
  3. WindowsSandbox.exe ile sandbox'ı başlatır
  4. Sandbox içinde LogonCommand testleri koşturur, sonucu ve ekran görüntülerini sonuç klasörüne yazar
  5. Sonuç dosyası gelene kadar bekler, sandbox'ı dışarıdan kapatır, özeti yazdırır
```

---

#### 1.6 Kararlar

##### Karar 1 — ViewModel'ler ayrı projede

**Mevcut durum:** `MAIN_TODO.md` ViewModel'leri App projesinde gösteriyordu.

**Karar:**

- ViewModel'ler WinUI'a bağımlı olmayan `Presentation` projesine konur.
- Böylece ViewModel testleri WinUI çalışma zamanı olmadan, normal `dotnet test` ile koşar.
- Pencere işlemleri (`IWindowService`) arayüzle soyutlanır, App projesinde uygulanır.

**Durum:** 🟢 VERİLDİ.

##### Karar 2 — Geliştirme ve test için paketsiz, Store için MSIX

**Karar:**

- Testler, self-contained ve paketsiz (`WindowsPackageType=None`) build ile koşar.
  - Sandbox'a yalnız klasör kopyalanır.
  - Sertifika ve runtime kurulumu gerekmez.
- Store için aynı proje MSIX olarak publish edilir.
- Veri klasörü:

| Çalışma biçimi | Veri klasörü |
|----------------|--------------|
| MSIX (Store) | Paketin yerel klasörü (`ApplicationData.Current.LocalFolder`) |
| Paketsiz | `%LOCALAPPDATA%\MyEverythingWidget.WinUI` |
| Test | `MEW_DATA_DIR` ortam değişkeni |

Eski Python verisi `%LOCALAPPDATA%\MyEverythingWidget\app_state.json` ile karışmaz.

**Durum:** 🟢 VERİLDİ.

---

#### 1.7 Sonuç

Faz 1 tamamlandı (2026-10-30). Bütün testler geçiyor.

| Test grubu | Sonuç | Nerede koştu |
|------------|-------|--------------|
| `Core.Tests` | 13/13 | Makine (`dotnet test`) |
| `Presentation.Tests` | 6/6 | Makine (`dotnet test`) |
| `UiTests` | 8/8 | Windows Sandbox (`scripts/test-ui.ps1`) |

##### 1.7.1 Testlerin hata yakaladığının kanıtı

UI testleri kod yazıldıktan sonra yazıldığı için ayrıca bozma (mutation) denemesi yapıldı:

- Uygulamada üç davranış geçici olarak bozuldu: pin, konum kaydı, tek kopya kontrolü.
- Sandbox koşusunda beklenen 5 test kırmızı oldu; bozulmayan davranışların 2 testi yeşil kaldı.
- Kod geri alındı.

##### 1.7.2 S2 riskinin sonucu

- Sandbox penceresi küçültülmüşken FlaUI testleri sorunsuz çalıştı.
- Bu fazdaki testler fare kullanmıyor (UI Automation pattern'leri ve Win32).
- Gerçek fare sürüklemesi ilk kez Faz 3'te denenecek.

##### 1.7.3 Bulunan ve düzeltilen sorunlar

- **`DisplayArea.FindAll()` sonucu LINQ ile gezilemiyor:**
  - Belirti: `InvalidCastException`, uygulama açılışta çöküyordu.
  - Çözüm: liste indeksle dolaşılıyor (`MainWindow.GetWorkAreas`).
- **Crash log:** Yakalanmayan hatalar artık `logs\crash.log`'a yazılıyor; ilk hata bununla bulundu.
- **UI testleri bir kez geliştirici masaüstünde koştu:**
  - Sebep: solution düzeyindeki `dotnet test` UI test projesini de çalıştırdı.
  - Fare ve klavyeye dokunulmadı; pencereler birkaç saniyeliğine açılıp kapandı.
  - Çözüm: `SandboxGuard` eklendi. UI testleri yalnız `MEW_UI_TEST_SANDBOX=1` iken uygulamayı açıyor, aksi halde atlanıyor.

- **Sandbox kapanışı kullanıcıdan "Kapat" bekliyordu:**
  - Sebep: sandbox içinden `shutdown` yapılınca Sandbox penceresi bir kapanış ekranında kalıyordu.
  - Çözüm: içeriden kapatma kaldırıldı. Sonuç dosyası gelince betik Sandbox istemcisini dışarıdan kapatıyor.
  - Doğrulama: kullanıcı müdahalesi olmadan koşu bitti, geride Sandbox süreci kalmadı.

##### 1.7.4 Sonraki fazlara bırakılanlar

| Konu | Faz |
|------|-----|
| Açılışta pin düğmesinde klavye odak çerçevesi görünüyor | Faz 3 (UI cilası) |
| MSIX self-contained (97 MB); Store için framework bağımlı paket değerlendirilecek | Faz 8 |
| Geçici logolar (`Assets/*.png`) | Faz 8 |
| Store publisher kimliği (şu an imzasız paket OID'i) | Faz 8 |

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 1 — İskelet, pencere ve MSIX" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 19/19, UI 8/8 (Sandbox). Sonuç: `PHASE1.md` → 1.7 Sonuç.

**Özet:** Solution yapısı, boş ama gerçek pencere, MSIX paketi ve UI test altyapısı.

**Hedefler:**

- [x] Kök `CLAUDE.md` ve `README.md` WinUI sürümü için yeniden yazılır. Python'a özgü kurallar `legacy/CLAUDE.md`'ye
  taşınır.
- [x] `legacy/tests/*.bat` dosyalarındaki `.venv` yolları düzeltilir; Python sürümü `legacy/` içinden
  çalıştırılabilir kalır.

- [x] Geliştirme ortamı: .NET 10 SDK ve Windows App SDK (kullanıcı onayıyla kurulum)
- [x] "Planlanan Yapı"daki projeler; Core'un WinUI bağımlılığı yok
- [x] Pencere: `SetTitleBar` ile özel başlık çubuğu, pin, kapat, Mica, konum/boyut hatırlama (W2)
- [x] Tek kopya: `AppInstance` ile ikinci açılış mevcut pencereyi öne getirir (W3)
- [x] Yerel MSIX paketi (test sertifikası) kurulup açılıyor
- [x] FlaUI test projesi: uygulamayı açan/kapatan temel test
- [x] Windows Sandbox koşucusu: `.wsb` yapılandırması, sandbox içi kurulum betiği, sonuçların `tmp/` altına
  dönmesi. Küçültülmüş pencerede fare girdisi riski burada denenir (S2).

**Detay:** `PHASE1.md`
