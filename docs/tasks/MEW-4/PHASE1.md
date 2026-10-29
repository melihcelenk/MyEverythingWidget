# MEW-4 Faz 1 — İskelet, pencere ve MSIX

> Önce: `MAIN_TODO.md` → Faz 1 · Sonra: `PHASE2.md` (Grid motoru, durum ve kalıcılık)

## İçindekiler

- Durum Panosu
- 1.1 Kapsam
- 1.2 Proje yapısı
- 1.3 Kabul kriterleri
- 1.4 Testler
- 1.5 Sandbox koşucusu
- 1.6 Kararlar
- 1.7 Sonuç

---

## Durum Panosu

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

## 1.1 Kapsam

- Boş ama gerçek bir widget penceresi açılır: özel başlık çubuğu, pin, kapat, Mica.
- Pencere ayarları (konum, boyut, always-on-top) kalıcıdır.
- Uygulama tek kopya çalışır.
- Testler üç katmanda koşar: Core, Presentation, UI (Sandbox).
- MSIX paketi üretilir.

Grid, kart ve kategori bu fazın kapsamında değildir (Faz 2-4).

---

## 1.2 Proje yapısı

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

## 1.3 Kabul kriterleri

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

## 1.4 Testler

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

## 1.5 Sandbox koşucusu

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

## 1.6 Kararlar

### Karar 1 — ViewModel'ler ayrı projede

**Mevcut durum:** `MAIN_TODO.md` ViewModel'leri App projesinde gösteriyordu.

**Karar:**

- ViewModel'ler WinUI'a bağımlı olmayan `Presentation` projesine konur.
- Böylece ViewModel testleri WinUI çalışma zamanı olmadan, normal `dotnet test` ile koşar.
- Pencere işlemleri (`IWindowService`) arayüzle soyutlanır, App projesinde uygulanır.

**Durum:** 🟢 VERİLDİ.

### Karar 2 — Geliştirme ve test için paketsiz, Store için MSIX

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

## 1.7 Sonuç

Faz 1 tamamlandı (2026-10-30). Bütün testler geçiyor.

| Test grubu | Sonuç | Nerede koştu |
|------------|-------|--------------|
| `Core.Tests` | 13/13 | Makine (`dotnet test`) |
| `Presentation.Tests` | 6/6 | Makine (`dotnet test`) |
| `UiTests` | 8/8 | Windows Sandbox (`scripts/test-ui.ps1`) |

### 1.7.1 Testlerin hata yakaladığının kanıtı

UI testleri kod yazıldıktan sonra yazıldığı için ayrıca bozma (mutation) denemesi yapıldı:

- Uygulamada üç davranış geçici olarak bozuldu: pin, konum kaydı, tek kopya kontrolü.
- Sandbox koşusunda beklenen 5 test kırmızı oldu; bozulmayan davranışların 2 testi yeşil kaldı.
- Kod geri alındı.

### 1.7.2 S2 riskinin sonucu

- Sandbox penceresi küçültülmüşken FlaUI testleri sorunsuz çalıştı.
- Bu fazdaki testler fare kullanmıyor (UI Automation pattern'leri ve Win32).
- Gerçek fare sürüklemesi ilk kez Faz 3'te denenecek.

### 1.7.3 Bulunan ve düzeltilen sorunlar

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

### 1.7.4 Sonraki fazlara bırakılanlar

| Konu | Faz |
|------|-----|
| Açılışta pin düğmesinde klavye odak çerçevesi görünüyor | Faz 3 (UI cilası) |
| MSIX self-contained (97 MB); Store için framework bağımlı paket değerlendirilecek | Faz 8 |
| Geçici logolar (`Assets/*.png`) | Faz 8 |
| Store publisher kimliği (şu an imzasız paket OID'i) | Faz 8 |
