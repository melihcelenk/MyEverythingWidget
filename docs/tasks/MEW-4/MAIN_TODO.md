# TODO: [MEW-4] MyEverythingWidget'ı WinUI ile Sıfırdan Yazmak (Microsoft Store)

> **📌 Referans Dokümanlar:**
>
> - `MAIN_TODO.md` - Bu dosya (ana takip)
> - `PHASE{N}.md` - Her fazın detaylı implementasyon planı (`/h-phase N` ile açılır)
> - `questions/` - Açık sorular (BirdsAEye soru kartları)
> - Davranış kaynağı: `docs/tasks/MEW-3/TODO.md` → "Hedef Davranış (Android Launcher Mantığı)",
>   `docs/tasks/MEW-3/TODO4.md` → "Test DSL", `tests/humanized/drag/*.dsl`
> - Store/paketleme referansı: TaskTimerWidget → `docs/general/BUILD_AND_PUBLISH_GUIDE.md`

---

## İçindekiler

- Branch Bilgisi
- Genel İlerleme
- Karar Panosu
- 1. Task Definition
  - 1.1 Mevcut Durum
  - 1.2 İstenen
  - 1.3 Kapsam (özellik eşleştirmesi)
  - 1.4 Kabul Kriterleri
  - 1.5 Test Senaryoları
  - 1.6 Error Case'leri
- 2. Preanalysis
  - 2.1 Mevcut Yapı
  - 2.2 Teknik Analiz
  - 2.3 Test Altyapısı Analizi
- 3. Solution Suggestions
- 4. Kararlar
- Faz 1 — İskelet, pencere ve MSIX
- Faz 2 — Grid motoru, durum ve kalıcılık (Core)
- Faz 3 — Grid UI: sürükle-bırak ve boyutlandırma
- Faz 4 — Kategoriler
- Faz 5 — Uygulama ekleme ve otomatik ikon
- Faz 6 — Notlar, resimler ve Ctrl+V
- Faz 7 — Ayarlar ve eski veriyi içe aktarma
- Faz 8 — UI testleri, performans ve Store paketi

---

## 🌿 Branch Bilgisi

**Branch:** `feature/MEW-4-winui-rewrite`
**Nereden açıldı:** `feature/MEW-3-drag-drop-grid-refactor`
**Nereye merge edilecek (PR target):** `master`

**Standart dışı durum:** Branch master'dan değil MEW-3'ten açıldı.

- MEW-3'te master'a henüz girmemiş 78 commit var.
- `legacy/` klasörünün Python'un en güncel sürümünü içermesi için MEW-3 taban alındı.
- Bu yüzden master'a açılacak PR, MEW-3 commit'lerini de içerir.

**Repo düzeni (S1 → A):**

| Yol | İçerik |
|-----|--------|
| `legacy/` | Python/PySide6 sürümü; `main.py`, `models`, `services`, `widgets`, `window`, `tests`, `requirements.txt`, `README.md` |
| `src/`, `tests/` | WinUI sürümü (Faz 1'de oluşur) |
| `docs/` | Ortak; MEW-1..MEW-4 dokümanları yerinde kalır |

---

## 📊 Genel İlerleme

| Faz | Başlık | Durum | Tamamlanma | Dosya |
|-----|--------|-------|------------|-------|
| Faz 1 | İskelet, pencere ve MSIX | 🟢 Tamamlandı | 100% | `PHASE1.md` |
| Faz 2 | Grid motoru, durum ve kalıcılık (Core) | 🟢 Tamamlandı | 100% | `PHASE2.md` |
| Faz 3 | Grid UI: sürükle-bırak ve boyutlandırma | 🟢 Tamamlandı | 100% | `PHASE3.md` |
| Faz 4 | Kategoriler | 🟢 Tamamlandı | 100% | `PHASE4.md` |
| Faz 5 | Uygulama ekleme ve otomatik ikon | 🟢 Tamamlandı | 100% | `PHASE5.md` |
| Faz 6 | Notlar, resimler ve Ctrl+V | 🟢 Tamamlandı | 100% | `PHASE6.md` |
| Faz 7 | Ayarlar ve eski veriyi içe aktarma | 🟢 Tamamlandı | 100% | `PHASE7.md` |
| Faz 8 | UI testleri, performans ve Store paketi | ⏳ Bekliyor | 0% | `PHASE8.md` |

**Durum etiketleri:**

| Etiket | Anlamı |
|--------|--------|
| 🟢 Tamamlandı | Faz bitti, fazın tüm testleri geçti |
| 🟡 Kısmi | Bir kısmı bitti; neyin beklediği faz notunda yazılı |
| ⏳ Bekliyor | Başlamadı |
| 🔴 Bloke | Bir karar ya da dış bağımlılık bekleniyor; neyin beklendiği yazılı |

---

## Karar Panosu

| # | Karar | Durum | Öneri / Karar | Nerede |
|---|-------|-------|---------------|--------|
| S1 | Kod hangi repoda duracak | 🟢 VERİLDİ | A: bu repo, Python sürümü `legacy/` altında | `questions/S01-repo-yeri.md` |
| S2 | Gerçek fare/klavye kullanan UI testleri bu masaüstünde mi koşacak | 🟢 VERİLDİ | B: Windows Sandbox, ajan çalıştırır | `questions/S02-ui-test-ortami.md` |
| K1 | Teknoloji yığını | 🟢 VERİLDİ | WinUI + Windows App SDK 2.x, .NET 10 | Kararlar → K1 |
| K2 | Grid kontrolü | 🟢 VERİLDİ | Özel sabit konumlu panel; `GridView` değil | Kararlar → K2 |
| K3 | Test stratejisi | 🟢 VERİLDİ | DSL motoru C#'a taşınır, mevcut `.dsl` dosyaları korunur | Kararlar → K3 |
| K4 | `create_app_and_note.dsl` beklentisi | 🟢 VERİLDİ | Kurallardan türetilen beklenti esas | Kararlar → K4 |
| K5 | Çoklu çarpışma kuralı | 🟢 VERİLDİ | Atomik; yerleşemezse bırakma iptal | Kararlar → K5 |
| K6 | Uygulama ekleme ve ikon | 🟢 VERİLDİ | Kurulu uygulama seçici + sürükle-bırak, ikon otomatik | Kararlar → K6 |
| K7 | Ctrl+V kapsamı | 🟢 VERİLDİ | Widget'ın her yerinde | Kararlar → K7 |
| K8 | Tema ve minimum Windows sürümü | 🟢 VERİLDİ | Sistemi izler; Windows 10 19041+ | Kararlar → K8 |
| K9 | Kapsam sınırı | 🟢 VERİLDİ | Özellik eşitliği + düzeltmeler; yeni özellikler sonraki sürüm | Kararlar → K9 |

S1 ve S2 dışındaki kararlar, kullanıcının "zevk ve tasarım kararlarını ajan versin" yönündeki talimatına göre
ajan tarafından verildi. Kullanıcı kullanım sırasında beğenmediği bir şey görürse bu kararlar yeniden açılır.

---

## 1. Task Definition

### 1.1 Mevcut Durum

- Uygulama PySide6 (Qt Widgets) ile yazılmış, yaklaşık 6.200 satır uygulama kodu ve 8.000 satır test kodu var.
- **Görünüm:**
  - Başlık çubuğu koyu, içerik ise elle yazılmış açık renk stilde kalıyor; sistem koyu temasıyla uyumsuz.
  - Windows 11 görünümü yok: Mica, Fluent kontrolleri ve sistem animasyonları kullanılmıyor.
- **Image sekmesi:** Ctrl+V çalışmıyor.
- **Uygulama ekleme:**
  - Yalnız dosya yolu yazılarak yapılabiliyor.
  - Uygulamanın kendi ikonu alınmıyor; yerine emoji/ikon/upload sekmeli bir seçici var.
- **Sürükle-bırak grid:** MEW-3 boyunca Qt üzerinde defalarca düzeltilmeye çalışıldı.
  - `MEW-3/TODO4.md` → "Bug 1": 2x1 not sağ kenara taşınınca bir sola yerleşiyor.
  - Bu hata "testler geçiyor ama gerçek uygulamada sorun devam ediyor" olarak kayıtlı.
- **Humanized UI testleri:** Gerçek fareyi koordinatla sürüyor ve kırılgan.
  - `MEW-3/TODO6.md` → "Known Issues": `create_app_and_note` dialog koordinatları yüzünden başarısız.
- **Store:** Python için paketleme elle ve zahmetli.
  - `MEW-1/ANALYSIS.md` → "Store Deployment Comparison": PyInstaller + MSIX adımları.

### 1.2 İstenen

- Uygulama WinUI ile sıfırdan yazılacak. Öncelik, Windows'ta modern ve akıcı bir masaüstü uygulaması olması.
- Microsoft Store'da yayınlanabilecek MSIX paketi üretilecek.
- Mevcut davranışlar korunacak. Bunlar MEW-3 kuralları ve `.dsl` testleriyle tanımlı, özellikle sürükle-bırak.
- Yukarıdaki dört sorun (görünüm, Ctrl+V, uygulama ekleme, grid) giderilecek.
- İş, kullanıcının elle test etmesine dayanmadan, otomatik testlerle doğrulanarak yürütülecek.
- Kullanıcı en sonda uygulamayı kullanıp beğenmediğini bildirecek.

### 1.3 Kapsam (özellik eşleştirmesi)

| Alan | Python sürümünde | WinUI sürümünde |
|------|------------------|-----------------|
| Pencere | Özel başlık çubuğu, pin (always-on-top), kapat, tek kopya | Aynısı; `SetTitleBar`, Mica, konum/boyut hatırlama |
| Grid | 5x5, 80px hücre, açık konum, span 1-3 | Aynı ölçüler ve kurallar (bkz. K2) |
| Kategoriler | Ekle (+), Rename, Delete, sürükleyerek sırala, tekerlekle kaydır | Aynısı |
| Uygulama kartı | Open, Change Icon, Edit, Rename, Delete; EXE/URL/Folder açma | Aynısı + kurulu uygulama seçici, otomatik ikon (bkz. K6) |
| Not kartı | Copy düğmesi, Edit, Resize, kategoriye taşı, Delete; varsayılan 2x1 | Aynısı |
| Hızlı not | "Add a quick note..." kutusu + Add | Aynısı |
| Resim kartı | Ekle, Resize, kategoriye taşı, Delete; span en-boy oranından | Aynısı + Ctrl+V her yerde (bkz. K7) |
| Kalıcılık | `%LOCALAPPDATA%\MyEverythingWidget\app_state.json` | Paket yerel klasörü; eski dosya içe aktarılır |
| Ayarlar | Yok | Tema (System/Light/Dark), always-on-top |

Kapsam dışı (sonraki sürüm, bkz. K9): sistem tepsisi, global kısayol, Windows ile başlama, komut çalıştırıcı,
bulut eşitleme.

### 1.4 Kabul Kriterleri

Grid kuralları (kaynak: `MEW-3/TODO.md` → "Temel Kurallar"):

| # | Kriter |
|---|--------|
| G1 | Bir öğe boş hedefe bırakıldığında (örnek: A1 R1C1 → R2C2) yalnız o öğe taşınır; başka hiçbir öğenin konumu değişmez. |
| G2 | Bir öğe dolu hedefe bırakıldığında ve hedefteki öğe kaynağın boşalan alanına sığıyorsa iki öğe yer değiştirir (örnek: A1 R1C1 → R1C3, A2 R1C1'e gelir). |
| G3 | Çok hücreli bir öğe bırakıldığında kapladığı tüm hücreler kontrol edilir (örnek: 2x1 N1 R2C1-C2 → R2C4; R2C5'teki A1 R2C1'e gelir, N1 R2C4-C5'e yerleşir). |
| G4 | Hedefteki öğe kaynağa sığmıyorsa ilk boş uygun hücreye taşınır (okuma sırası: satır satır, soldan sağa). |
| G5 | Bir öğe taşındığında veya silindiğinde diğer öğeler yerinde kalır; boş hücreler kendiliğinden dolmaz. |
| G6 | Öğe grid dışına taşacak bir hedefe bırakıldığında (örnek: 2x1 not R1C5'e) bırakma iptal olur ve öğe eski yerine döner. |
| G7 | Sürüklenen öğenin görüntüsü ekranda kapladığı gerçek boyuttadır (2x1 not 2x1 görünür) ve fare imleci tutulan noktada kalır. |
| G8 | Sürükleme sırasında bırakılacak hücrelerin tamamı vurgulanır (2x1 için iki hücre). |
| G9 | Yeni eklenen öğe ilk boş uygun hücreye yerleşir; grid doluysa öğe eklenmez ve "Grid is full" uyarısı görünür. |
| G10 | Resize ile span 1-3 arasında değişir; yeni alan doluysa resize uygulanmaz ve öğe eski boyutunda kalır. |

Uygulama, not, resim ve pencere:

| # | Kriter |
|---|--------|
| U1 | "Add app" seçicisi Start menüsündeki kurulu uygulamaları (Win32 ve Store) ikonlarıyla listeler ve ada göre arar (örnek: "code" → Visual Studio Code). |
| U2 | Seçilen uygulama, uygulamanın kendi ikonuyla eklenir; kullanıcı ikon seçmez. |
| U3 | Widget üzerine bir `.exe`, `.lnk` ya da klasör sürüklenip bırakıldığında kendi ikonuyla uygulama kartı oluşur. |
| U4 | Tarayıcıdan bir URL bırakıldığında ya da elle URL girildiğinde site ikonuyla kart oluşur; ikon alınamazsa ad baş harfli bir ikon kullanılır. |
| U5 | Karta tıklamak hedefi açar (EXE çalışır, URL tarayıcıda açılır, klasör Explorer'da açılır). |
| U6 | Hedefi artık bulunmayan bir karta tıklandığında uygulama çökmez; "Target not found" uyarısı görünür. |
| N1 | Hızlı not kutusuna yazıp Enter'a basınca 2x1 not kartı oluşur ve kutu temizlenir; boş metinle not oluşmaz. |
| N2 | Not kartındaki Copy düğmesi not metnini panoya kopyalar. |
| I1 | Widget odaktayken Ctrl+V basıldığında panodaki içerik türüne göre kart oluşur (bkz. K7). |
| I2 | Resim kartının span'i en-boy oranından hesaplanır (örnek: 16:9 → 3x2, kare → 2x2, 4:3 → 2x1). |
| W1 | Tema "System" iken uygulama Windows açık/koyu temasını izler; tema değişince yeniden başlatmadan güncellenir. Hiçbir yerde açık ve koyu stiller karışık görünmez. |
| W2 | Pin düğmesi always-on-top'ı açar/kapatır; durum ve pencere konumu yeniden açılışta korunur. |
| W3 | Uygulama ikinci kez başlatılınca yeni pencere açılmaz, mevcut pencere öne gelir. |
| D1 | İlk açılışta eski `app_state.json` varsa kategoriler, uygulamalar, notlar ve resimler konumlarıyla içe aktarılır; ikinci açılışta tekrar aktarılmaz. |

### 1.5 Test Senaryoları

| Kabul kriteri | Hangi test kapsıyor |
|---------------|---------------------|
| G1-G6, G9, G10 | Core DSL testleri: mevcut üç `.dsl` + her kural için yeni `.dsl` (Faz 2) |
| G7, G8 | UI testi (FlaUI): sürükleme sırasında ekran görüntüsü + vurgulanan hücre sayısı (Faz 3, Faz 8) |
| G1-G3 uçtan uca | UI testi: gerçek sürüklemeyle `.dsl` senaryosu koşturulur, sonuç durum dosyasından okunur (Faz 3) |
| U1, U2 | Infrastructure entegrasyon testi: bilinen bir uygulama (Notepad) listede ve ikonu boş değil (Faz 5) |
| U3, U4 | ViewModel testi (bırakılan veri → kart) + UI testi (Faz 5) |
| U5, U6 | Launcher servis testi; sahte hedef ve silinmiş hedef (Faz 5) |
| N1, N2 | ViewModel testi + pano servis testi (Faz 6) |
| I1, I2 | Pano ayrıştırma testi (bitmap, metin, dosya) + span hesap testi (Faz 6) |
| W1 | UI testi: açık ve koyu temada ekran görüntüsü, renk örneklemesiyle uyum kontrolü (Faz 7) |
| W2, W3 | UI testi: yeniden başlatma, ikinci kopya (Faz 1) |
| D1 | İçe aktarma testi: `tests/state/initial_test_state.json` ve gerçek dosya biçimi örneğiyle (Faz 7) |

### 1.6 Error Case'leri

- Durum dosyası bozuk ya da okunamıyor: uygulama açılır, bozuk dosya `app_state.corrupt-<tarih>.json` olarak
  saklanır, boş durumla devam edilir ve kullanıcıya bilgi verilir. Veri sessizce silinmez.
- Durum dosyası yazılamıyor: işlem geri alınmaz, hata loglanır, kullanıcıya uyarı gösterilir. Yazma atomik
  yapılır (geçici dosya + değiştirme).
- Pano erişimi reddedildi ya da pano boş: Ctrl+V hiçbir şey yapmaz, çökme olmaz.
- İkon çıkarılamadı (izin, bozuk dosya, ağ yok): ad baş harfli varsayılan ikon kullanılır.
- Resim dosyası silinmiş: kart "Image not found" yer tutucusuyla görünür, silinebilir.
- Grid dolu: G9.
- Geçersiz bırakma hedefi: G6.

---

## 2. Preanalysis

### 2.1 Mevcut Yapı

| Katman | Dosyalar | Not |
|--------|----------|-----|
| Model | `models/app_shortcut.py`, `models/note.py`, `models/category.py` | `grid_row`, `grid_col`, `col_span`, `row_span`; `NoteType`: text, image, link, file |
| Grid mantığı | `window/grid/` (`mover.py`, `collision_detector.py`, `cell_calculator.py`, `grid_manager.py`) | Kurallar UI'dan kısmen ayrılmış; WinUI'da tamamen saf Core'a alınacak |
| Sabitler | `window/grid/constants.py` | 5x5 grid, 80px hücre, boşluk 0 |
| Durum | `window/app_state.py`, `services/storage_service.py` | JSON: `categories`, `apps`, `notes` |
| Resim | `services/image_storage_service.py`, `services/image_grid_calculator.py` | Resimler göreli `data/images` yoluna yazılıyor |
| UI | `widgets/`, `window/` | Qt Widgets + elle stil |

### 2.2 Teknik Analiz

**Sorunlar:**

- **Tema:** Elle yazılmış stiller sistem paletiyle karışıyor. Kök neden Qt Widgets'ın Windows 11 tema sistemini
  kullanmaması.
- **Ctrl+V:** Kısayol yalnız dialog içindeki belirli bir widget'a bağlı ve odak orada olmadığında tetiklenmiyor.
  WinUI'da Ctrl+V pencere düzeyinde `KeyboardAccelerator` ile ele alınacak.
- **Uygulama ekleme:** Kurulu uygulamaları listeleyen ya da ikon çıkaran bir servis yok; bu yüzden ikon seçici
  eklenmiş.
- **Grid:** Qt sürükle-bırak ile pixmap/hotspot hesapları elle yapılıyor (`widgets/draggable_mixin.py`). G7 ve G3
  hatalarının kaynağı burası.

**Mevcut Metrikler:**

- Python uygulaması açık ve boşta yaklaşık 100 MB bellek kullanıyor (2026-10-30 ölçümü, `tasklist`).
- Gerçek kullanıcı verisi küçük: 1 kategori, 1 uygulama, 1 not.

### 2.3 Test Altyapısı Analizi

- `.dsl` biçimi grid davranışını okunur ve kesin tanımlıyor. Bu, yeni sürümün asıl şartnamesi olacak.
  - Konumlar 1 tabanlı (`R2C3` = 2. satır, 3. sütun; `tests/humanized/runner/parser.py`).
- `create_app_and_note.dsl` beklentisi kurallarla çelişiyor (bkz. K4).
- Humanized testlerin kırılganlığı koordinat tahmininden geliyor. Örnekler: dialog konumu tahmini, sabit
  bekleme süreleri.
  - FlaUI öğeleri UI Automation ağacından `AutomationId` ile bulur; koordinat tahmini gerekmez.
  - Sürükleme ise yine gerçek fare girdisi ister (bkz. S2).

---

## 3. Solution Suggestions

### Plan A: WinUI + Windows App SDK 2.x + .NET 10 (Recommended)

- **Efor:** Orta-yüksek (8 faz). Grid mantığı saf C# olduğu için hızlı test edilir.
- **Risk:** Düşük-orta.
  - Microsoft Build 2026'da WinUI'ı Windows'un yerel üretim platformu olarak yeniden öne çıkardı.
  - Yeni bir framework planlanmıyor.
  - TaskTimerWidget aynı yığınla Store'da yayında.
- **Ölçeklenebilirlik:** Yüksek. Mica, tema, MSIX, Store güncellemeleri hazır geliyor.
- **Teknik Borç:** Yalnız Windows. Linux hedefi bırakılmış olur.

**Planlanan Yapı:**

```
src/
  MyEverythingWidget.Core/            saf .NET 10: modeller, GridEngine, kurallar, durum (WinUI bağımlılığı yok)
  MyEverythingWidget.Infrastructure/  Windows API: depolama, pano, ikon çıkarma, kurulu uygulamalar, başlatıcı
  MyEverythingWidget.App/             WinUI: View, ViewModel (CommunityToolkit.Mvvm), MSIX paketi
tests/
  MyEverythingWidget.Core.Tests/      xUnit: DSL testleri, model, kalıcılık
  MyEverythingWidget.App.Tests/       xUnit: ViewModel testleri
  MyEverythingWidget.UiTests/         FlaUI: gerçek pencere üzerinde testler
  Grid/*.dsl                          davranış şartnamesi
```

```
Kullanıcı sürükler ──> GridPanel (UI) ──> GridViewModel ──> GridEngine.TryMove (Core)
                                                                  │
                                              ┌──── kabul ────────┴──── red ────┐
                                              v                                  v
                                       yeni konumlar                        öğe geri döner
                                              │
                                    StateStore.Save (atomik) ──> GridPanel animasyonla günceller
```

### Plan B: Avalonia 11 + .NET 10

- **Efor:** Orta. XAML benzer; sistem entegrasyonları (ikon, pano, kurulu uygulamalar) yine Windows'a özel yazılır.
- **Risk:** Orta. Fluent tema taklit; Windows 11 hissi tam değil.
- **Ölçeklenebilirlik:** Yüksek, Linux/macOS açık kalır.
- **Teknik Borç:** Store paketlemesi ve Windows entegrasyonu elle.

### Karşılaştırma

| Kriter | Plan A (WinUI) | Plan B (Avalonia) |
|--------|----------------|-------------------|
| Windows 11 görünümü | Yerel | Taklit |
| Store / MSIX | Hazır, TaskTimerWidget'ta denenmiş | Elle |
| Çapraz platform | Yok | Var |
| Önceki deneyim | TaskTimerWidget | Yok |

### Öneri

Plan A. Öncelik Windows ve Store; çapraz platform artık bir gereksinim değil.

### ✅ Karar Kılınan Çözüm

Henüz yok. Kullanıcı planın bütününü onaylamadı. Kullanıcı "S1 ve S2 cevaplanınca başla" talimatını verdi; bu
iki karar cevaplanınca Plan A ile Faz 1'e geçilir.

---

## 4. Kararlar

### K1 — Teknoloji yığını

**Mevcut durum:** TaskTimerWidget .NET 8 ve Windows App SDK 1.7 kullanıyor. .NET 8 desteği Kasım 2026'da bitiyor.

**Karar:**

| Bileşen | Seçim |
|---------|-------|
| UI | WinUI, Windows App SDK 2.x (2026-10 itibarıyla kararlı sürüm 2.6.4) |
| Runtime | .NET 10 (LTS) |
| MVVM | CommunityToolkit.Mvvm |
| DI ve log | Microsoft.Extensions.DependencyInjection, Microsoft.Extensions.Logging + dosya log'u |
| JSON | System.Text.Json (source generator); Newtonsoft kullanılmaz |
| Test | xUnit, FlaUI |

**Durum:** 🟢 VERİLDİ. TaskTimerWidget'tan yalnız paketleme ve yayın adımları alınır, eski sürümler alınmaz.

### K2 — Grid kontrolü

**Mevcut durum:** Bir önceki öneride grid için `GridView` (yeniden sıralamayı hazır veren kontrol) önerilmişti.

**Problem:** `GridView` öğeleri sırayla dizer; sabit konum, boş hücre ve span kurallarını (G1-G6) desteklemez.

**Karar:**

- Grid, öğeleri `(satır, sütun, span)` ile yerleştiren özel bir `Panel` olarak yazılır.
- Kuralları Core'daki `GridEngine` uygular; UI yalnızca sonucu çizer.
- Taşınan öğeler implicit animasyonla yeni yerine kayar.

**Durum:** 🟢 VERİLDİ.

### K3 — Test stratejisi

**Karar:**

- Mevcut üç `.dsl` dosyası olduğu gibi `tests/Grid/` altına alınır.
- C# DSL ayrıştırıcısı her `.dsl` dosyası için ayrı bir xUnit testi üretir; `GridEngine` bu testlerle doğrulanır.
- Her kabul kriteri için en az bir `.dsl` senaryosu yazılır.
- Aynı `.dsl` dosyaları, UI testinde gerçek sürüklemeyle de koşturulabilir.
- ViewModel'ler UI olmadan test edilir.
- FlaUI testleri öğeleri `AutomationId` ile bulur; koordinat tahmini ve sabit bekleme kullanılmaz.

**Durum:** 🟢 VERİLDİ.

### K4 — `create_app_and_note.dsl` beklentisi

**Mevcut durum:** Kurallar şu sonucu veriyor:

- N1 ilk boş yere yerleşir: R1C1-C2.
- A1 sonraki boş yere yerleşir: R1C3.
- `Drag(N1, R1C2)` ile N1'in hedefi R1C2-C3 olur; A1 ile çarpışır, A1 kaynağa (R1C1) gider.

Dosyadaki beklenti ise N1'i R2C3-C4'te gösteriyor. Test `MEW-3/TODO6.md`'de zaten başarısız olarak kayıtlı.

**Karar:** Kurallardan türetilen beklenti esas alınır.

```
A1 N1 N1 .  .
.  .  .  .  .
```

Düzeltilmiş dosya yeni test klasörüne yazılır; Python reposundaki dosyaya dokunulmaz.

**Durum:** 🟢 VERİLDİ.

### K5 — Çoklu çarpışma kuralı

**Mevcut durum:** Kurallar tek çarpışan öğeyi tanımlıyor. Örnek: 2x1 not, yan yana iki 1x1 uygulamanın üstüne
bırakılırsa ne olacağı yazılı değil.

**Karar:**

- Çarpışan öğeler okuma sırasıyla işlenir.
- Her biri önce kaynağın boşalan alanına, sığmazsa ilk boş uygun hücreye yerleşir.
- Biri bile yerleşemezse bırakma tamamen iptal olur ve hiçbir öğe yer değiştirmez (atomik).

**Durum:** 🟢 VERİLDİ. Bu kural için ayrı `.dsl` senaryoları yazılır.

### K6 — Uygulama ekleme ve ikon

**Karar:**

- **Birinci yol — "Add app":** Kurulu uygulamalar `shell:AppsFolder` üzerinden listelenir (Win32 ve Store
  uygulamaları) ve aranabilir.
- **İkinci yol — sürükle-bırak:** Widget'a `.exe`, `.lnk`, klasör ya da URL bırakılabilir.
- **Üçüncü yol — elle:** Yol veya URL girilir ("Browse..." dahil).
- **İkon:**
  - Win32 uygulamaları, kısayollar ve klasörler için `IShellItemImageFactory` kullanılır.
  - Store uygulamalarında paket logosu kullanılır.
  - URL'de sitenin favicon'u alınır; alınamazsa baş harf ikonu.
- Emoji/ikon/upload sekmeli seçici kaldırılır. Kartın sağ tık menüsünde yalnız "Change icon..." (resim dosyası
  seç) ve "Reset icon" kalır.

**Durum:** 🟢 VERİLDİ.

### K7 — Ctrl+V kapsamı

**Karar:** Ctrl+V widget penceresinin her yerinde ve seçili kategoride çalışır:

| Panodaki içerik | Sonuç |
|-----------------|-------|
| Bitmap (örnek: ekran görüntüsü) | Resim kartı |
| Resim dosyası (örnek: Explorer'da kopyalanan `.png`) | Resim kartı |
| `.exe`, `.lnk`, klasör | Uygulama kartı |
| URL metni | URL uygulama kartı |
| Düz metin | Not kartı |

Bir metin kutusu odaktayken Ctrl+V normal yapıştırma yapar.

**Durum:** 🟢 VERİLDİ.

### K8 — Tema ve minimum Windows sürümü

**Karar:**

- Tema varsayılan olarak sistemi izler; Ayarlar'da System/Light/Dark seçilebilir.
- Renkler yalnız WinUI tema kaynaklarından gelir; elle sabit renk yazılmaz.
- Arka plan Windows 11'de Mica, Windows 10'da düz tema rengi.
- Minimum sürüm Windows 10 19041 (TaskTimerWidget ile aynı Store kitlesi).

**Durum:** 🟢 VERİLDİ.

### K9 — Kapsam sınırı

**Karar:** Bu task özellik eşitliği ve "Mevcut Durum"daki sorunların çözümüyle sınırlıdır. Kapsam dışı kalanlar:

- Sistem tepsisi
- Global kısayol
- Windows ile başlama
- Komut çalıştırıcı
- Bulut eşitleme

Bunlar ayrı task'lara bırakılır.

**Durum:** 🟢 VERİLDİ.

---

## Faz 1 — İskelet, pencere ve MSIX

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

---

## Faz 2 — Grid motoru, durum ve kalıcılık (Core)

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 79/79. Sonuç: `PHASE2.md` → 2.7 Sonuç.

**Özet:** Sürükle-bırak kurallarının tamamı UI'sız C# kodunda, `.dsl` testleriyle.

**Hedefler:**

- [x] Modeller: Category, AppItem, NoteItem, ImageItem; ortak `GridPlacement` (satır, sütun, span)
- [x] C# DSL ayrıştırıcı ve test üreteci (Python biçimiyle birebir uyumlu, 1 tabanlı konum)
- [x] `GridEngine`: G1-G6, G9, G10 ve K5
- [x] Mevcut üç `.dsl` + her kriter için yeni senaryolar geçiyor (K4'teki düzeltmeyle)
- [x] `StateStore`: versiyonlu JSON şeması, atomik yazma, bozuk dosya davranışı

**Detay:** `PHASE2.md`

---

## Faz 3 — Grid UI: sürükle-bırak ve boyutlandırma

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 99/99, UI 20/20 (Sandbox). Sonuç: `PHASE3.md` → 3.5 Sonuç.

**Özet:** Özel grid paneli ve kartlar; sürükleme görüntüsü, hücre vurgusu, animasyon, resize.

**Hedefler:**

- [x] `GridPanel` (K2) ve kart şablonları (uygulama, not, resim)
- [x] Sürükleme görüntüsü gerçek boyutta, imleç tutulan noktada (G7)
- [x] Hedef hücrelerin tamamı vurgulanıyor; geçersiz hedefte farklı vurgu (G8, G6)
- [x] Taşınan öğeler animasyonla kayıyor
- [x] Resize tutamacı, hücreye oturma (G10)
- [x] UI testi: `.dsl` senaryoları gerçek sürüklemeyle koşuyor (çalıştırma ortamı S2'ye bağlı)

**Detay:** `PHASE3.md`

---

## Faz 4 — Kategoriler

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 128/128, UI 28/28 (Sandbox). Sonuç: `PHASE4.md` → 4.5 Sonuç.

**Özet:** Sekmeler: ekle, yeniden adlandır, sil, sürükleyerek sırala; öğeyi başka kategoriye taşı.

**Hedefler:**

- [x] `TabView` ile kategori sekmeleri ve "+" sekmesi
- [x] Rename (satır içi), Delete (onaylı; içindeki öğe sayısı gösterilir)
- [x] Sekmeleri sürükleyerek sıralama, tekerlekle kaydırma
- [x] Kart menüsünde "Move to" → kategori; hedef kategoride ilk boş hücreye yerleşir

**Detay:** `PHASE4.md`

---

## Faz 5 — Uygulama ekleme ve otomatik ikon

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 170/170, UI 33/33 (Sandbox). Sonuç: `PHASE5.md` → 5.6 Sonuç.

**Özet:** Kurulu uygulama seçici, sürükle-bırakla ekleme, otomatik ikon, başlatma.

**Hedefler:**

- [x] `InstalledAppsService` (Win32 + Store, arama) (U1)
- [x] `IconService`: exe, lnk, klasör, Store uygulaması, favicon, baş harf yedeği (U2, U4)
- [x] Widget'a dosya/URL bırakma (U3, U4)
- [x] `LauncherService`: EXE, URL, klasör; eksik hedef uyarısı (U5, U6)
- [ ] Kart menüsü: Open, Edit, Rename, Change icon..., Reset icon, Delete — Rename Faz 6, Change/Reset icon Faz 8

**Detay:** `PHASE5.md`

---

## Faz 6 — Notlar, resimler ve Ctrl+V

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 206/206, UI 41/41 (Sandbox). Sonuç: `PHASE6.md` → 6.5 Sonuç.

**Özet:** Not ve resim kartları, hızlı not, pencere düzeyinde Ctrl+V.

**Hedefler:**

- [x] Hızlı not kutusu (N1), not kartı: Copy, Edit, Resize, Move to, Delete (N2)
- [x] Resim kartı: dosyadan ekleme, en-boy oranından span (I2), "Image not found" yer tutucusu
- [x] `ClipboardService` + pencere düzeyinde Ctrl+V; içerik türü tablosu (K7, I1)
- [x] "Add" menüsü (alt çubukta "+ Add" menüsü): App, Note, Image

**Detay:** `PHASE6.md`

---

## Faz 7 — Ayarlar ve eski veriyi içe aktarma

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 231/231, UI 47/47 (Sandbox). Sonuç: `PHASE7.md` → 7.5 Sonuç.

**Özet:** Ayarlar sayfası, tema doğrulaması, Python sürümünün verisini içe aktarma.

**Hedefler:**

- [x] Ayarlar: Theme (System/Light/Dark), Always on top, About
- [x] Açık/koyu tema UI testi (W1)
- [x] `LegacyImporter`: `%LOCALAPPDATA%\MyEverythingWidget\app_state.json` ve resim dosyaları (D1)

**Detay:** `PHASE7.md`

---

## Faz 8 — UI testleri, performans ve Store paketi

**Durum:** ⏳ Bekliyor

**Özet:** Uçtan uca test turu, bellek/başlama süresi ölçümü, Store'a hazır paket ve listeleme dokümanları.

**Hedefler:**

- [ ] Tüm kabul kriterlerinin testleri geçiyor (1.5'teki tablo)
- [ ] Ölçüm: soğuk başlama süresi, boşta bellek (Python sürümüyle karşılaştırmalı)
- [ ] Store paketi (x64 + arm64), uygulama ikonları, ekran görüntüleri
- [ ] Store listeleme ve gizlilik politikası taslağı (TaskTimerWidget dokümanları örnek alınarak)
- [ ] Partner Center gönderimi kullanıcı tarafından yapılır

**Detay:** `PHASE8.md`

---

## Kaynaklar

- [Windows App SDK downloads (Microsoft Learn)](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/downloads)
- [Windows Latest — Build 2026, WinUI](https://www.windowslatest.com/2026/06/04/microsoft-is-killing-windows-11s-web-app-slop-encourages-devs-to-build-native-apps-using-winui/)
- [FlaUI](https://github.com/FlaUI/FlaUI)
