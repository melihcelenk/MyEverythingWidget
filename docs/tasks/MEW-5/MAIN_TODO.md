# TODO: [MEW-5] Widget ailesi: My Everything Widget ve Task Timer Widget'ın birlikte çalışması

> **📌 Referans Dokümanlar:**
>
> - `MAIN_TODO.md` - Bu dosya (ana takip)
> - `WIDGET_FAMILY.md` - Araştırma: problemler, Windows mekanizmaları, yaklaşımlar, aşamalar
> - `PHASE{N}.md` - Her fazın detaylı planı (`/h-phase N` ile açılır)
> - `questions/` - Açık sorular (BirdsAEye soru kartları)
> - Yaklaşım kararı: `questions/S05-widget-ailesi-yaklasimi.md` (A; MEW-4'te S24 olarak açılmıştı)

---

## İçindekiler

- Branch Bilgisi
- Genel İlerleme
- Hazırlık Durumu
- Karar Panosu
- 1. Task Definition
  - 1.1 Mevcut Durum
  - 1.2 İstenen
  - 1.3 Kabul Kriterleri
  - 1.4 Test Senaryoları
  - 1.5 Error Case'leri
- 2. Preanalysis
- 3. Solution Suggestions
- Faz Özetleri

---

## 🌿 Branch Bilgisi

| Repo | Yol | Branch | Nereden açıldı | PR hedefi | Rolü |
|------|-----|--------|----------------|-----------|------|
| `MyEverythingWidget` (ana repo) | `C:\Kodlar\MyEverythingWidget` | `feature/MEW-5-widget-family` | `master` (`e452283`) | `master` | Hub: aile üyelerini bulma, sağ tık menüsü, yerleştirme; task dokümanları |
| `WidgetFamily` (yeni) | `C:\Kodlar\WidgetFamily` | `main` | — (yeni repo, `28af937`) | — | Ortak sözleşme ve kütüphane; `https://github.com/melihcelenk/WidgetFamily` |
| `TaskTimerWidget` | `C:\Kodlar\TaskTimerWidget` | `feature/MEW-5-widget-family` | `master` (`183bb2b`) | `master` | Aile üyesi: protokol, mesaj kanalı, görev çubuğundan çekilme |

TaskTimerWidget'ın `master`'ına doğrudan dokunulmaz; bütün iş bu branch'te yapılır.

**Repo düzeni (S02 → B):** Ortak sözleşme ayrı bir repoda durur ve iki uygulamaya git submodule olarak eklenir.

| Repo | GitHub | Rolü | Nasıl bağlanır |
|------|--------|------|----------------|
| `WidgetFamily` (yeni, açık kaynak, MIT) | `melihcelenk/WidgetFamily` | Ortak sözleşme: kütüphane, testleri, `docs/CONTRACT.md` | — |
| `MyEverythingWidget` | `melihcelenk/MyEverythingWidget` | Hub | `external/WidgetFamily` submodule'ü, projeye `ProjectReference` |
| `TaskTimerWidget` | `melihcelenk/TaskTimerWidget` | Üye | `external/WidgetFamily` submodule'ü, projeye `ProjectReference` |

GitHub'da anlaşılır olması için çok repolu projelerde yaygın düzen kullanılır:

- **README'ler:** Her repo README'sinde "Widget family" bölümü üç repoyu ve rollerini listeler. `WidgetFamily`
  README'si hangi uygulamaların kullandığını ve submodule olarak nasıl ekleneceğini anlatır.
- **Klonlama:** Uygulama README'lerinde `git clone --recurse-submodules` ve sonradan
  `git submodule update --init` komutları yazar.
- **Sürüm:** `WidgetFamily` SemVer etiketleriyle (`v0.1.0` …) ve `CHANGELOG.md` ile sürümlenir. Uygulamalar
  submodule'ü bir etikete sabitler, branch'e değil.
- **CI:** `WidgetFamily`'nin kendi CI'ı testleri koşar. Uygulama CI'larında checkout `submodules: true` ile yapılır.
- **Keşfedilebilirlik:** Üç repoya ortak bir GitHub topic'i (`melihcelenk-widget-family`) ve açıklamada aile adı
  eklenir.
- **Derleme bağımsızlığı:** `WidgetFamily` kendi `Directory.Build.props` ve `Directory.Packages.props` dosyalarını
  taşır. Böylece MEW'in derleme ayarları (merkezi paket sürümleri, uyarı = hata) submodule'e karışmaz; kütüphane
  her iki uygulamada aynı şekilde derlenir.

---

## 📊 Genel İlerleme

| Faz | Başlık | Durum | Tamamlanma | Dosya |
|-----|--------|-------|------------|-------|
| 1 | Ortak sözleşme: uzantı adı, protokol adresleri, mesajlar | 🟢 Tamamlandı | 100% | `PHASE1.md` |
| 2 | Task Timer: protokolle açılma, mesaj kanalı, hub varken görev çubuğundan çekilme | 🟢 Tamamlandı | 100% | `PHASE2.md` |
| 3 | MEW: aile üyelerini bulma, sağ tıkta dört yön, açma ve kenara yerleştirme | 🟢 Tamamlandı | 100% | `PHASE3.md` |
| 4 | Birlikte hareket: hub sürüklenince üyeler kayar, tam ekranda birlikte gizlenir | 🟢 Tamamlandı | 100% | `PHASE4.md` |
| 5 | Kurulu olmayan aile widget'ını indirmeye yönlendirme ve kurulu halin gösterimi | 🟢 Tamamlandı | 100% | `PHASE5.md` |

<!-- Durum ikonları: 🟢 Tamamlandı | 🟡 Kısmi | ⏳ Bekliyor | 🔴 Bloke (bir karar ya da dış bağımlılık bekleniyor) -->

Faz 3'ün sağ tık menüsü kodlanmadan önce görsel taslak gösterilir.

---

## ✅ Hazırlık Durumu

<!-- Durum: 🟢 Tamam | 🟠 Kısmi | 🔴 Yok | — (geçerli değil). Bu projede Lima kullanılmıyor. -->

| Bölüm | Durum | Kapsadığı | Son kontrol |
|-------|-------|-----------|-------------|
| Genel Dokümanlar | 🟢 Tamam | `docs/general/ARCHITECTURE.md` (aile sözleşmesi), `docs/general/DEVELOPMENT.md` (iki paketli Sandbox testi) | — |
| Devops Notları | — | Sunucu yok; iki Store paketi ayrı gönderilir | — |

---

## Karar Panosu

| # | Karar | Durum | Öneri / Karar | Nerede |
|---|-------|-------|---------------|--------|
| S05 | Ortak çatı yaklaşımı | 🟢 VERİLDİ | A: ayrı uygulamalar, MEW kompakt simgesi hub | `questions/S05-widget-ailesi-yaklasimi.md` |
| S01 | Hub kim olacak | 🟢 VERİLDİ | A: MEW'in kompakt simgesi; ayrı başlatıcı yok | `questions/S01-hub-kim.md` |
| S02 | Ortak sözleşme kodu iki repoda nasıl paylaşılacak | 🟢 VERİLDİ | B: `WidgetFamily` reposu, iki tarafa submodule | `questions/S02-ortak-kod-paylasimi.md` |
| S03 | Dört yönde kimin nerede duracağı | 🟢 VERİLDİ | A: widget kendi kenarını önerir, doluysa sıradaki boş kenar | `questions/S03-yon-yerlesimi.md` |
| S04 | Hub kapanınca üyelere ne olacak | 🟢 VERİLDİ | A: açık kalır, görev çubuğuna geri döner | `questions/S04-hub-kapaninca.md` |

---

## 📝 1. Task Definition

### 1.1 Mevcut Durum

- My Everything Widget (MEW) ve Task Timer Widget (TTW) Store'da ayrı ürünler, aynı yayıncıdan.
- Her biri görev çubuğunda ayrı bir düğme olarak görünüyor; widget sayısı arttıkça görev çubuğu kalabalıklaşıyor.
- Uygulamalar birbirinden habersiz; ileride yazılacak widget'ların bağlanabileceği ortak bir yapı yok.

### 1.2 İstenen

- Gereksinim: Görev çubuğu kalabalığı azalsın; widget'lar ayrı ayrı düğme olarak görünmesin.
- Gereksinim: MEW ile TTW birlikte çalışabilsin; ileride yazılacak başka widget'lar da aynı yapıya bağlanabilsin.
- Gereksinim (örnek kullanım): MEW simgesine sağ tıklanınca dört yanında diğer widget uygulamaları açılabilsin.

### 1.3 Kabul Kriterleri

- [x] İki uygulama birlikte çalışırken görev çubuğunda yalnız hub'ın düğmesi görünür.
- [x] TTW tek başına kuruluysa bugünkü gibi kendi görev çubuğu düğmesiyle çalışır.
- [x] Hub, yüklü aile üyelerini kendiliğinden bulur; bir üye kaldırılınca menüden düşer.
- [x] Hub'ın sağ tık menüsünden bir üye açılır ve hub'ın ilgili kenarına yerleşir.
- [x] Yeni bir widget, kendi manifestine aile bloğu ekleyerek ve sözleşmeyi uygulayarak, hub'da kod değişikliği
  gerektirmeden menüde görünür.

### 1.4 Test Senaryoları

| # | Senaryo | Beklenen |
|---|---------|----------|
| T1 | Yalnız TTW kurulu, açılır | Görev çubuğunda TTW düğmesi var |
| T2 | MEW ve TTW kurulu, ikisi açık | Görev çubuğunda yalnız MEW düğmesi var |
| T3 | MEW sağ tık → TTW yönü | TTW açılır (kapalıysa başlatılır), MEW'in o kenarına yerleşir |
| T4 | TTW zaten açıkken T3 | Yeni pencere açılmaz; mevcut pencere öne gelir ve yerleşir |
| T5 | TTW kaldırılır | MEW menüsünde TTW yönü boşalır |
| T6 | Mesaj kanalına bilinmeyen sürümde mesaj gelir | Mesaj yok sayılır, uygulama çalışmaya devam eder |

Testler: sözleşme ve mesaj işleme birim testleriyle; iki paketin birlikte davranışı Windows Sandbox'ta, iki paket
birlikte kurularak UI testiyle doğrulanır.

### 1.5 Error Case'leri

- Hub üyeye mesaj gönderirken üye kapanır → mesaj kaybolur, hub hata göstermez, üyeyi bir sonraki tıklamada yeniden
  başlatır.
- Üyenin bildirdiği protokol açılamaz (paket bozuk) → hub o yönü göstermez ve hatayı loglar.
- İki MEW örneği aynı anda hub olmaya çalışır → MEW tek örnek çalıştığı için oluşmaz; kanal adı zaten alınmışsa ikinci hub olmaz (S01 → A).
- Hub'ın kenarında üyeye yer yoksa (ekran kenarı) → üye karşı kenara ya da ekranın içine kaydırılır.

---

## 🔍 2. Preanalysis

Ayrıntı `WIDGET_FAMILY.md` → 2. ve 3. bölümlerde.

- **Teknoloji farkı:** MEW .NET 10 / Windows App SDK 2.6; TTW .NET 8 / Windows App SDK 1.7. Gereken mekanizmaların
  (görev çubuğundan çekilme, protokol aktivasyonu, uygulama uzantısı, named pipe) hepsi SDK 1.7'de de var; TTW'nin
  SDK güncellemesi bu task için zorunlu değil.
- **Ortak kod:** Paylaşılan sözleşme kütüphanesi iki tarafta da derlenebilmeli; .NET 8 hedeflenirse her iki uygulama
  kullanabilir (S02).
- **Test:** MEW'in Sandbox UI test altyapısı (`scripts/test-ui.ps1`) iki paketi birlikte kuracak şekilde genişletilir.

---

## 💡 3. Solution Suggestions

Seçilen: S05 → A. Karşılaştırma `WIDGET_FAMILY.md` → 4. bölüm.

---

## 🎯 Faz Özetleri

### 🟢 Faz 1 — Ortak sözleşme

**Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Ayrıntı:** [PHASE1.md](PHASE1.md)
Hub ile üyelerin birbirini nasıl bulduğu, açtığı ve hangi mesajları gönderdiği yazılır ve iki uygulamanın da
kullanacağı küçük bir kütüphanede (`WidgetFamily` reposu) kodlanır. Kartların MEW-5'e taşınması (T1) ve doküman düzeni (T2) tamamlandı.

### 🟢 Faz 2 — Task Timer tarafı

**Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Ayrıntı:** [PHASE2.md](PHASE2.md)
Task Timer aile üyesi olur: protokolle açılır, mesaj kanalını dinler, hub çalışırken görev çubuğundan çekilir.
İş TaskTimerWidget reposunda, `feature/MEW-5-widget-family` branch'inde yapılır.

### 🟢 Faz 3 — MEW tarafı

**Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Ayrıntı:** [PHASE3.md](PHASE3.md)
MEW'in kompakt simgesi yüklü üyeleri bulur, sağ tıkta dört yanında gösterir; tıklanan üye açılıp o kenara
yerleşir. Menü kodlanmadan önce görsel taslak gösterilir.

### 🟢 Faz 4 — Birlikte hareket (isteğe bağlı)

**Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Ayrıntı:** [PHASE4.md](PHASE4.md)
Hub sürüklenince yanına yerleşmiş üyeler de kayar; tam ekranda birlikte gizlenir.

### 🟢 Faz 5 — İndirmeye yönlendirme ve kurulu halin gösterimi

**Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Ayrıntı:** [PHASE5.md](PHASE5.md)
Kurulu olmayan aile widget'ları menüde "indir" düğmesiyle Store sayfasına yönlendiriyor; kurulu hal kullanıcının
bilgisayarında hazırlanıp gösteriliyor.
