# Faz 7 — Ayarlar ve eski veriyi içe aktarma

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Başlık çubuğundaki dişli düğmesi artık bir Settings penceresi açıyor: tema (Windows ayarı, açık, koyu), "Always on top"
ve About (sürüm, gizlilik notu, GitHub bağlantısı). Değişiklikler hemen uygulanıyor ve kaydediliyor. Python sürümünü
kullanmış biri WinUI sürümünü ilk açtığında eski kategorileri, uygulamaları, notları ve resimleri bir kez içe
aktarılıyor; sonuç durum çubuğunda bildiriliyor.

## Problem

- WinUI sürümünde ayarlar sayfası yoktu; tema seçilemiyor, "Always on top" açılıp kapatılamıyordu.
- Python sürümünü kullananların verisi (`%LOCALAPPDATA%\MyEverythingWidget\app_state.json` ve resimler) yeni sürüme
  geçmiyordu.
- Tema değişince seçili sekme koyu yüzeyin üstünde açık gri kalıyordu (bu fazda bulundu).
- Sekme sürükleme testi diğer UI testlerinden sonra aynı süreçte koşunca düşüyordu (Faz 6'dan beri).

## Çözüm

- **Ayarlar (`SettingsDialog`, `MainViewModel`):** Theme, Always on top, About; değerler `settings.json`'a kaydedilir.
- **İçe aktarma (`LegacyImporter`, `LegacyMigrator`):** İlk açılışta Python verisi okunur, dönüştürülür ve kaydedilir;
  bu sürümün verisi asla üzerine yazılmaz.
- **Sekme rengi (`CategoryTabsView`):** Renk `StaticResource` yerine tema sözlükleriyle (`ThemeDictionaries`) verilir.
- **UI test koşucusu (`scripts/test-ui.ps1`):** `Isolation=OwnProcess` etiketli testler ayrı bir test sürecinde koşar.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 7.1 | Dişli düğmesi Theme, Always on top ve About içeren Settings penceresini açar. | 🟢 Tamamlandı |
| 7.2 | Seçilen tema yeniden başlatmadan uygulanır ve kaydedilir. | 🟢 Tamamlandı |
| 7.3 | Python sürümünün verisi ilk açılışta bir kez içe aktarılır. | 🟢 Tamamlandı |
| 7.4 | Tema değişince seçili sekme ızgara yüzeyiyle aynı tonda görünür. | 🟢 Tamamlandı (testlerde bulunan hata) |
| 7.5 | Sistem sürükle-bırakını kullanan UI testi ayrı bir test sürecinde koşar. | 🟢 Tamamlandı (kök neden bulunamadı) |

## Nasıl kontrol edilir

- [ ] Başlık çubuğundaki dişli düğmesine bas: Settings penceresinde "Theme", "Always on top" ve About görünmeli.
- [ ] "Theme" → "Dark" seç: widget yeniden başlamadan koyu olmalı; seçili sekme de koyu yüzeyle aynı tonda olmalı.
- [ ] Widget'ı kapatıp aç: seçilen tema korunmalı.
- [ ] "Always on top"ı aç ve başka bir pencereye tıkla: widget üstte kalmalı.
- [ ] Python sürümünün `app_state.json` dosyası olan bir makinede, WinUI sürümünün verisi yokken ilk kez aç: eski
  öğeler gelmeli ve "Imported 3 items from the previous version of My Everything Widget." gibi bir bilgi çıkmalı.
- [ ] Widget'ı yeniden aç: içe aktarma tekrar yapılmamalı.

## Kalan

- **7.5:** Sekme sürükleme testinin asıl kök nedeni (önceki testlerin aynı süreçte bıraktığı durum) bulunamadı; Faz 8'de
  izlenecek olarak bırakıldı (`PHASE8.md` → açık işler).

## Ayrıntılar

### 7.1 — Dişli düğmesi Theme, Always on top ve About içeren Settings penceresini açar.

- **Mevcut durum:** Ayarlar sayfası yoktu; Faz 1'den `settings.json` yalnız pencere bilgisini tutuyordu.
- **Problem:** Tema ve "Always on top" kullanıcı tarafından seçilebilmeli; sürüm ve gizlilik notu görülebilmeli.
- **Çözüm:**
  - Başlık çubuğunda dişli düğmesi → Settings: Theme, Always on top, About (sürüm, gizlilik notu, GitHub bağlantısı).
  - "Theme": "Use Windows setting", "Light", "Dark"; varsayılan "Use Windows setting"; kayıt `settings.json` →
    `theme`: `System`, `Light`, `Dark`.
  - "Always on top": açık / kapalı; varsayılan kapalı; kayıt `settings.json` → `isAlwaysOnTop`.
  - Değişiklikler hemen uygulanır ve kaydedilir.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/SettingsDialog.xaml`, `src/MyEverythingWidget.App/Views/SettingsDialog.xaml.cs`,
  `src/MyEverythingWidget.Presentation/MainViewModel.cs`, `src/MyEverythingWidget.Core/Settings/AppSettings.cs`
- **Testler:** `Presentation.Tests` → `SettingsViewModelTests`; `UiTests` → `AlwaysOnTopSwitch_PinsTheWindow`,
  `About_ShowsVersion`
- **Durum:** 🟢 Tamamlandı.

### 7.2 — Seçilen tema yeniden başlatmadan uygulanır ve kaydedilir.

- **Mevcut durum:** Widget her zaman Windows temasıyla açılıyordu.
- **Problem:** Açık ve koyu temada arayüz doğru boyanmalı ve seçim kalıcı olmalı (W1).
- **Çözüm:**
  - Tema seçimi hemen uygulanır ve `settings.json`'a yazılır.
  - Faz 1'den kalan, `theme` alanı olmayan `settings.json` dosyaları "Use Windows setting" ile açılır.
- **Dosyalar:** `src/MyEverythingWidget.Core/Settings/AppSettings.cs`, `src/MyEverythingWidget.Presentation/MainViewModel.cs`,
  `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `Core.Tests` → `ThemeSettingsTests`; `Presentation.Tests` → `SettingsViewModelTests`; `UiTests` →
  `SettingsAndMigrationTests.Theme_DarkAndLight_RepaintWithoutRestartAndArePersisted` (piksel ölçümü)
- **Durum:** 🟢 Tamamlandı.

### 7.3 — Python sürümünün verisi ilk açılışta bir kez içe aktarılır.

- **Mevcut durum:** WinUI sürümü Python sürümünün verisini okumuyordu.
- **Problem:** Kullanıcılar yeni sürüme geçince öğelerini kaybetmemeli (D1).
- **Çözüm:**
  - Kaynak: `%LOCALAPPDATA%\MyEverythingWidget\app_state.json`.
  - Bu sürümün `state.json`'ı varsa hiçbir şey yapılmaz; veri asla üzerine yazılmaz.
  - Python dosyası yoksa boş "General" kategorisiyle açılır.
  - Okunamıyorsa hiçbir şey yazılmaz; uyarı: "Items of the previous version could not be read, so they were not
    imported."
  - Okunuyorsa aktarılır; bilgi: "Imported 3 items from the previous version of My Everything Widget."
  - Bazı resimler bulunamıyorsa aktarılır; uyarı mesajına "1 image could not be found." eklenir.
  - Dönüştürme: kategoriler aynı adla ve sırayla, bilinmeyen kategori adı ilk kategoriye; uygulamalar (exe, url,
    folder) gerçek ikonlu uygulama kartı; metin notu not kartı; link ve dosya notu 1x1 uygulama kartı; resim notu
    `images\` altına kopyalanır (göreli yol Python dosyasının yanında da aranır).
  - Geçerli ve boş konum korunur; grid dışı ya da çakışan konum kategorinin ilk boş hücresine gider.
  - Test koşuları (`MEW_DATA_DIR` tanımlı) yalnız `MEW_LEGACY_STATE` ile açıkça verilen dosyayı okur; testler
    geliştiricinin gerçek Python verisine hiç dokunmaz.
- **Dosyalar:** `src/MyEverythingWidget.Core/Legacy/LegacyImporter.cs`, `src/MyEverythingWidget.Core/Legacy/LegacyStateReader.cs`,
  `src/MyEverythingWidget.Presentation/LegacyMigrator.cs`, `src/MyEverythingWidget.App/App.xaml.cs`
- **Testler:** `Core.Tests` → `LegacyImportTests` (11); `Presentation.Tests` → `LegacyMigratorTests` (7); `UiTests` →
  `PreviousVersionData_IsImportedOnFirstStartOnly`
- **Durum:** 🟢 Tamamlandı.

### 7.4 — Tema değişince seçili sekme ızgara yüzeyiyle aynı tonda görünür.

- **Mevcut durum:** Ekran görüntüsünde koyu yüzeyin üstünde açık gri bir sekme vardı; ilk tema testi bunu
  yakalamamıştı.
- **Problem:** Sekme rengi `StaticResource` ile verilmişti. Bu, açılıştaki temaya göre bir kez çözülür, tema değişince
  güncellenmez.
- **Çözüm:**
  - Önce hatayı yakalayan test yazıldı: seçili sekme yüzeyle aynı tonda olmalı. Test kırmızıydı (sekme 144, yüzey 40).
  - Sonra renk tema sözlükleriyle (`ThemeDictionaries`) verildi.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/CategoryTabsView.xaml`
- **Testler:** `UiTests` → `SelectedTab_MatchesGridSurface_AfterThemeChange` (Light, Dark); iki temada da yeşil
- **Durum:** 🟢 Tamamlandı.

### 7.5 — Sistem sürükle-bırakını kullanan UI testi ayrı bir test sürecinde koşar.

- **Mevcut durum:**
  - Sekme sürükleme testi tek başına ya da kategori testleriyle birlikte koşunca her seferinde geçiyor (6 koşu).
  - Faz 6'dan beri, diğer UI testlerinden sonra aynı süreçte koşunca düşüyordu.
- **Problem:** `TabView` sıralamayı sistemin sürükle-bırak mekanizmasıyla yapıyor. Ekran görüntüsünde sürüklemenin hiç
  başlamadığı görüldü.
- **Çözüm:**
  - Denenenler (3 deneme kuralı): sürükleme eşiğinden sonra duraklama (tam koşuda yine kırmızı); önce sekmeye tıklayıp
    pencereyi etkinleştirme (yine kırmızı); basılı kalan değiştirici tuş hipotezi (ölçüldü, Ctrl, Shift ve Alt basılı
    değildi).
  - Test `Isolation=OwnProcess` etiketiyle işaretlendi.
  - Sandbox koşucusu etiketli testleri aynı sandbox içinde, ayrı bir test sürecinde, diğerlerinden önce çalıştırıyor;
    sonuç iki koşunun birleşimi.
- **Dosyalar:** `tests/MyEverythingWidget.UiTests/CategoryTests.cs`, `scripts/test-ui.ps1`
- **Testler:** Tam UI koşusu 47/47 (46 ana süreç + 1 ayrı süreç)
- **Durum:** 🟢 Tamamlandı (uygulamanın davranışı tutarlı; asıl kök neden bulunamadı ve Faz 8'de izlenecek).

### Doğrulanmayan / dikkat edilmesi gereken

- **Sekme sürükleme testinin kök nedeni:** Önceki testlerin aynı süreçte bıraktığı durum bulunamadı; test ayrı süreçte
  koşuyor (7.5).
- **Gerçek Python verisi:** İçe aktarma testleri `tests/state/initial_test_state.json` ve gerçek dosya biçimi örneğiyle
  yapıldı (D1); testler geliştiricinin gerçek verisine dokunmaz.
- **Testler:** Unit 231/231, UI 47/47 (46 ana süreç + 1 ayrı süreç), Sonar 0 bulgu.

### Referanslar

- `MAIN_TODO.md` → Faz 7 — Ayarlar ve eski veriyi içe aktarma
- `MAIN_TODO.md` → 1.4 Kabul Kriterleri (W1, D1)
- `PHASE6.md` (önceki faz) · `PHASE8.md` (UI testleri, performans ve Store paketi)

### Önceki doküman içeriği

> Önce: `PHASE6.md` · Sonra: `PHASE8.md` (UI testleri, performans ve Store paketi)

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| Tema (System, Light, Dark), Always on top, About | 🟢 Tamamlandı | W1 |
| Python verisinin ilk açılışta içe aktarılması | 🟢 Tamamlandı | D1 |
| Tema değişiminde seçili sekme rengi | 🟢 Tamamlandı | 7.6.1 |
| Sistem sürükle-bırakı kullanan UI testinin ayrı süreçte koşması | 🟢 Tamamlandı | 7.6.2 |

---

#### 7.1 Kapsam

- Başlık çubuğunda dişli düğmesi → Settings: Theme, Always on top, About (sürüm, gizlilik notu, GitHub bağlantısı).
- Değişiklikler hemen uygulanır ve `settings.json`'a kaydedilir.
- İlk açılışta Python sürümünün verisi içe aktarılır, sonuç durum çubuğunda bildirilir.

---

#### 7.2 Ayarlar

| Ayar (ekranda) | Değerler | Varsayılan | Kayıt |
|----------------|----------|------------|-------|
| "Theme" | "Use Windows setting", "Light", "Dark" | "Use Windows setting" | `settings.json` → `theme`: `System`, `Light`, `Dark` |
| "Always on top" | açık / kapalı | kapalı | `settings.json` → `isAlwaysOnTop` |

Faz 1'den kalan, `theme` alanı olmayan `settings.json` dosyaları "Use Windows setting" ile açılır.

---

#### 7.3 Eski verinin içe aktarılması

Kaynak: `%LOCALAPPDATA%\MyEverythingWidget\app_state.json` (Python sürümü).

| Durum | Davranış |
|-------|----------|
| Bu sürümün `state.json`'ı var | Hiçbir şey yapılmaz; veri asla üzerine yazılmaz |
| Python dosyası yok | Boş "General" kategorisiyle açılır |
| Python dosyası okunamıyor | Hiçbir şey yazılmaz; uyarı: "Items of the previous version could not be read, so they were not imported." |
| Python dosyası okunuyor | Aktarılır; bilgi: "Imported 3 items from the previous version of My Everything Widget." |
| Bazı resimler bulunamıyor | Aktarılır; uyarı mesajına "1 image could not be found." eklenir |

Dönüştürme kuralları:

| Python'da | Yeni sürümde |
|-----------|--------------|
| Kategori (ada göre bağlı) | Aynı adla kategori, aynı sırayla |
| Bilinmeyen kategori adı | İlk kategori |
| Uygulama (exe, url, folder) | Uygulama kartı; emoji ikon yerine gerçek ikon oluşturulur |
| Metin notu | Not kartı |
| Link notu, dosya notu | Uygulama kartı (1x1) |
| Resim notu | Resim, `images\` altına kopyalanır; göreli yol Python dosyasının yanında da aranır |
| Geçerli ve boş konum | Korunur |
| Grid dışı ya da çakışan konum | Kategorinin ilk boş hücresi |

Test koşuları (`MEW_DATA_DIR` tanımlı) yalnız `MEW_LEGACY_STATE` ile açıkça verilen dosyayı okur. Böylece testler
geliştiricinin gerçek Python verisine hiç dokunmaz.

---

#### 7.4 Testler

| Kabul kriteri | Test |
|---------------|------|
| Tema ayarının kaydı | `Core.Tests` → `ThemeSettingsTests` |
| Tema, sürüm (ViewModel) | `Presentation.Tests` → `SettingsViewModelTests` |
| D1 okuma ve dönüştürme | `Core.Tests` → `LegacyImportTests` (11) |
| D1 göç akışı | `Presentation.Tests` → `LegacyMigratorTests` (7) |
| W1 tema uygulanması ve kalıcılık (piksel ölçümü) | `UiTests` → `SettingsAndMigrationTests.Theme_DarkAndLight_RepaintWithoutRestartAndArePersisted` |
| W1 seçili sekme | `UiTests` → `SelectedTab_MatchesGridSurface_AfterThemeChange` (Light, Dark) |
| Always on top anahtarı | `UiTests` → `AlwaysOnTopSwitch_PinsTheWindow` |
| About | `UiTests` → `About_ShowsVersion` |
| D1 uçtan uca, ikinci açılışta tekrar yok | `UiTests` → `PreviousVersionData_IsImportedOnFirstStartOnly` |

---

#### 7.5 Sonuç

Faz 7 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`) | 231/231 |
| UI (Sandbox) | 47/47 (46 ana süreç + 1 ayrı süreç) |
| Sonar | 0 bulgu |

---

#### 7.6 Bulunan sorunlar

##### 7.6.1 Koyu temada seçili sekme açık gri kalıyordu

- **Mevcut durum:** Ekran görüntüsünde koyu yüzeyin üstünde açık gri bir sekme vardı; ilk tema testi bunu yakalamamıştı.
- **Problem:** Sekme rengi `StaticResource` ile verilmişti. Bu, açılıştaki temaya göre bir kez çözülür, tema değişince
  güncellenmez.
- **Çözüm:**
  - Önce hatayı yakalayan test yazıldı: seçili sekme yüzeyle aynı tonda olmalı. Test kırmızıydı (sekme 144, yüzey 40).
  - Sonra renk tema sözlükleriyle (`ThemeDictionaries`) verildi.
- **Durum:** ✅ Düzeltildi; test iki temada da yeşil.

##### 7.6.2 Sekme sürükleme testi tam koşuda düşüyordu

- **Mevcut durum:**
  - Test tek başına ya da kategori testleriyle birlikte koşunca her seferinde geçiyor (6 koşu).
  - Faz 6'dan beri, diğer UI testlerinden sonra aynı süreçte koşunca düşüyordu.
- **Problem:** `TabView` sıralamayı sistemin sürükle-bırak mekanizmasıyla yapıyor. Ekran görüntüsünde sürüklemenin hiç
  başlamadığı görüldü.
- **Denenenler (3 deneme kuralı):**
  - Sürükleme eşiğinden sonra duraklama: tam koşuda yine kırmızı.
  - Önce sekmeye tıklayıp pencereyi etkinleştirme: yine kırmızı.
  - Basılı kalan değiştirici tuş hipotezi: ölçüldü, Ctrl, Shift ve Alt basılı değildi.
- **Çözüm:**
  - Bu test `Isolation=OwnProcess` etiketiyle işaretlendi.
  - Sandbox koşucusu etiketli testleri aynı sandbox içinde, ayrı bir test sürecinde, diğerlerinden önce çalıştırıyor;
    sonuç iki koşunun birleşimi.
- **Durum:** ✅ Tam koşu 47/47. Uygulamanın davranışı tutarlı; asıl kök neden (önceki testlerin aynı süreçte bıraktığı
  durum) bulunamadı ve Faz 8'de izlenecek.

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 7 — Ayarlar ve eski veriyi içe aktarma" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 231/231, UI 47/47 (Sandbox). Sonuç: `PHASE7.md` → 7.5 Sonuç.

**Özet:** Ayarlar sayfası, tema doğrulaması, Python sürümünün verisini içe aktarma.

**Hedefler:**

- [x] Ayarlar: Theme (System/Light/Dark), Always on top, About
- [x] Açık/koyu tema UI testi (W1)
- [x] `LegacyImporter`: `%LOCALAPPDATA%\MyEverythingWidget\app_state.json` ve resim dosyaları (D1)

**Detay:** `PHASE7.md`
