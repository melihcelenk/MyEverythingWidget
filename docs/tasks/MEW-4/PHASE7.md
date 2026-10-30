# MEW-4 Faz 7 — Ayarlar ve eski veriyi içe aktarma

> Önce: `PHASE6.md` · Sonra: `PHASE8.md` (UI testleri, performans ve Store paketi)

## İçindekiler

- Durum Panosu
- 7.1 Kapsam
- 7.2 Ayarlar
- 7.3 Eski verinin içe aktarılması
- 7.4 Testler
- 7.5 Sonuç
- 7.6 Bulunan sorunlar

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| Tema (System, Light, Dark), Always on top, About | 🟢 Tamamlandı | W1 |
| Python verisinin ilk açılışta içe aktarılması | 🟢 Tamamlandı | D1 |
| Tema değişiminde seçili sekme rengi | 🟢 Tamamlandı | 7.6.1 |
| Sistem sürükle-bırakı kullanan UI testinin ayrı süreçte koşması | 🟢 Tamamlandı | 7.6.2 |

---

## 7.1 Kapsam

- Başlık çubuğunda dişli düğmesi → Settings: Theme, Always on top, About (sürüm, gizlilik notu, GitHub bağlantısı).
- Değişiklikler hemen uygulanır ve `settings.json`'a kaydedilir.
- İlk açılışta Python sürümünün verisi içe aktarılır, sonuç durum çubuğunda bildirilir.

---

## 7.2 Ayarlar

| Ayar (ekranda) | Değerler | Varsayılan | Kayıt |
|----------------|----------|------------|-------|
| "Theme" | "Use Windows setting", "Light", "Dark" | "Use Windows setting" | `settings.json` → `theme`: `System`, `Light`, `Dark` |
| "Always on top" | açık / kapalı | kapalı | `settings.json` → `isAlwaysOnTop` |

Faz 1'den kalan, `theme` alanı olmayan `settings.json` dosyaları "Use Windows setting" ile açılır.

---

## 7.3 Eski verinin içe aktarılması

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

## 7.4 Testler

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

## 7.5 Sonuç

Faz 7 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`) | 231/231 |
| UI (Sandbox) | 47/47 (46 ana süreç + 1 ayrı süreç) |
| Sonar | 0 bulgu |

---

## 7.6 Bulunan sorunlar

### 7.6.1 Koyu temada seçili sekme açık gri kalıyordu

- **Mevcut durum:** Ekran görüntüsünde koyu yüzeyin üstünde açık gri bir sekme vardı; ilk tema testi bunu yakalamamıştı.
- **Problem:** Sekme rengi `StaticResource` ile verilmişti. Bu, açılıştaki temaya göre bir kez çözülür, tema değişince
  güncellenmez.
- **Çözüm:**
  - Önce hatayı yakalayan test yazıldı: seçili sekme yüzeyle aynı tonda olmalı. Test kırmızıydı (sekme 144, yüzey 40).
  - Sonra renk tema sözlükleriyle (`ThemeDictionaries`) verildi.
- **Durum:** ✅ Düzeltildi; test iki temada da yeşil.

### 7.6.2 Sekme sürükleme testi tam koşuda düşüyordu

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
