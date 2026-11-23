# Widget ailesi: My Everything Widget ile Task Timer Widget'ın birlikte çalışması (araştırma)

GitHub project 4 → "TaskTimerWidget ile birlikte çalışma / Ortak Çatı Araştırma". Karar kartı:
`questions/S05-widget-ailesi-yaklasimi.md`. Task takibi: `MAIN_TODO.md`.

**Karar (S05 → A, 2026-11-22):** Widget'lar ayrı uygulama olarak kalır; MEW'in kompakt simgesi hub olur
(4. bölüm, A). Aşamalar 5. bölümde ve `MAIN_TODO.md` → Genel İlerleme'de.

## 1. Problemler

| # | Problem | Bugün |
|---|---------|-------|
| P1 | Görev çubuğu kalabalık | Her widget görev çubuğunda ayrı bir düğme olarak görünüyor ("Task Timer", "My Everything …"). Yeni widget eklendikçe artacak. |
| P2 | Ortak çatı yok | Uygulamalar birbirinden habersiz. İleride yazılacak widget'ların bağlanabileceği bir yapı yok. |
| P3 | Hızlı erişim | Örnek istek: kompakt simgeye sağ tıklanınca dört yanında diğer widget'lar açılabilsin. |

## 2. Mevcut durum

| | My Everything Widget | Task Timer Widget |
|--|----------------------|-------------------|
| Repo | `C:\Kodlar\MyEverythingWidget` (`master`) | `C:\Kodlar\TaskTimerWidget` (`master`) |
| Teknoloji | WinUI 3, Windows App SDK 2.6, .NET 10 | WinUI 3, Windows App SDK 1.7, .NET 8 |
| Dağıtım | Microsoft Store (MSIX, full trust) | Microsoft Store (MSIX, full trust) |
| Yayıncı | Melih Celenk | Melih Celenk (aynı Partner Center hesabı) |
| Pencere | Kompakt simge, her zaman üstte, tam ekranda gizlenir | Küçük her zaman üstte kart |

İki uygulamanın **aynı yayıncıdan** gelmesi önemli: Windows aynı yayıncının paketlerine ortak bir klasör
(publisher cache folder) verebiliyor.

## 3. Kullanılabilecek Windows mekanizmaları

| Mekanizma | Ne sağlar | Not |
|-----------|-----------|-----|
| `AppWindow.IsShownInSwitchers = false` | Pencere görev çubuğundan ve Alt+Tab'dan kalkar | Tek satır. P1'in asıl çözümü; ama widget'a görev çubuğu dışında bir giriş noktası gerekir. |
| App Extension (`windows.appExtension` + `AppExtensionCatalog`) | Hub, yüklü "aile üyelerini" bulur; yüklenince/kaldırılınca olay alır. Üye; adını, simgesini ve açılış adresini manifestte bildirir | Paketli masaüstü uygulamalarında çalışır (Windows Terminal'in fragment uzantıları bu yolla bulunur). Yeni widget eklemek = manifeste bir blok. |
| Protokol aktivasyonu (`windows.protocol`, ör. `tasktimer:`) | Hub, üyeyi "aç / şu kenara yerleş" diye başlatır | Store uygulaması için standart; üye kapalıysa açılır. |
| Adlandırılmış kanal (named pipe) | Çalışan uygulamalar arası anlık mesaj: "göster", "gizle", "konumun şu", "kompakta geç" | Full-trust paketlerde serbest. Küçük JSON mesajları yeter. |
| Publisher cache folder (`windows.publisherCacheFolders`) | Aynı yayıncının uygulamaları ortak bir klasörü paylaşır | Ortak ayarlar (tema, hangi kenarda kim var) için. |
| Pencereyi başka sürecin görev çubuğu düğmesinde gruplama (AppUserModelID) | Widget'lar görev çubuğunda tek düğme altında toplanır | Kullanıcının "görev çubuğu düğmelerini birleştir" ayarına bağlı; sabitlenmiş simgede tutarsızlık. Önerilmez. |
| Bildirim alanı (tray) simgesi | Görev çubuğu düğmesi yerine saatin yanında küçük simge | Her widget kendi tray simgesini koyarsa kalabalık oraya taşınır; yalnız hub koymalı. |

## 4. Yaklaşımlar

### A — Ayrı uygulamalar, ortak aile protokolü; MEW hub olur ⭐

- Her widget Store'da ayrı ürün olarak kalır.
- MEW'in kompakt simgesi **hub** olur. Aile üyelerini App Extension ile bulur, sağ tıkta dört yanda gösterir.
- Hub çalışırken üyeler görev çubuğundan çekilir (`IsShownInSwitchers = false`). Görev çubuğunda tek düğme kalır:
  MEW. Hub yoksa (kullanıcı yalnız Task Timer'ı kurmuşsa) üye bugünkü gibi kendi düğmesiyle çalışır.
- Üyeyi açma: protokol aktivasyonu. Konum/göster/gizle: named pipe.
- Yeni widget = manifeste App Extension bloğu + küçük ortak kütüphane (pipe istemcisi, protokol adresleri).

Sağ tık önizlemesi:

```
                 [ ⏱ Task Timer ]
                        ▲
   [ (boş) ]  ◀  [ MEW simgesi ]  ▶  [ (boş) ]
                        ▼
                 [ (boş) ]
```

Bir yöne tıklanınca o widget açılır ve simgenin o kenarına yapışık yerleşir. Yön boşsa gizlenir ya da "Store'da
diğer widget'lar" bağlantısı olur.

### B — Tek uygulamada birleştirme

- Task Timer, MEW'in içine modül olarak taşınır: bir süreç, ayrı pencereler, tek görev çubuğu düğmesi.
- Yerleşim ve haberleşme en kolay olan yol; protokol ve pipe gerekmez.
- Ama Task Timer'ın Store ürünü ve mevcut kullanıcıları ayrı kalır ya da emekliye ayrılır.
- Task Timer .NET 8 / SDK 1.7 → .NET 10 / SDK 2.x'e taşınmalı.
- Her yeni widget MEW'i büyütür; MEW'i istemeyen biri yalnız zamanlayıcıyı kuramaz.

### C — Yalnız görev çubuğunu sadeleştir

- Her uygulama görev çubuğundan çekilir ve tray simgesine geçer; entegrasyon yapılmaz.
- P1 kısmen çözülür (kalabalık tray'e taşınır), P2 ve P3 çözülmez.

### Karşılaştırma

| Ölçüt | A | B | C |
|-------|---|---|---|
| P1 görev çubuğu | 🟢 tek düğme | 🟢 tek düğme | 🟡 tray'e taşınır |
| P2 ileride yeni widget | 🟢 manifest bloğu | 🟡 MEW'e kod | 🔴 yok |
| P3 dört yönlü açılış | 🟢 | 🟢 | 🔴 |
| Store ürünleri | Ayrı kalır | Tek ürün | Ayrı kalır |
| İş miktarı | Orta (iki repo) | Büyük (taşıma) | Küçük |
| Risk | Süreçler arası senkron (konum, kapanış) | TTW kullanıcılarının geçişi | Düşük |

## 5. Önerilen yol (A) ve aşamalar

| Aşama | İçerik | Çıktı |
|-------|--------|-------|
| 1 | Ortak sözleşme: App Extension adı, protokol adresleri, pipe mesajları (sürümlü JSON). Küçük paylaşılan kütüphane. | Doküman + kütüphane + birim testleri |
| 2 | TTW: protokol aktivasyonu, pipe sunucusu, hub varken görev çubuğundan çekilme. SDK 1.7 → 2.x güncellemesi bu aşamaya girebilir. | TTW sürümü |
| 3 | MEW: üyeleri bulma, sağ tıkta dört yön, açma ve kenara yerleştirme. | MEW sürümü |
| 4 | Birlikte hareket: hub sürüklenince üyeler de kayar; tam ekranda birlikte gizlenir. | İsteğe bağlı |

Test: iki paket birlikte Windows Sandbox'a kurulur. UI testi hub'dan Task Timer'ı açar, görev çubuğu düğmesi sayısını
ve konumu doğrular.

## 6. Açık konular (karar verildikten sonra netleşecek)

- ~~Hub her zaman MEW mi olacak, yoksa ayrı, küçük bir "launcher" uygulaması mı?~~ **S01 → A:** hub MEW'in
  kompakt simgesi; ayrı launcher yok. Ayrı launcher, MEW'i kurmayanlara da
  görev çubuğu düzeni sağlar ama bir Store ürünü daha demektir.
- ~~Dört yön sabit mi (her widget kendi kenarı), kullanıcı mı seçer?~~ **S03 → A:** widget kenarını önerir, doluysa
  saat yönünde sıradaki boş kenar; kullanıcı ayarı yok.
- ~~Hub kapanırsa üyeler görev çubuğuna geri mi döner, onlar da mı kapanır?~~ **S04 → A:** açık kalır, görev
  çubuğuna geri döner.
