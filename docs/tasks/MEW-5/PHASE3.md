# Faz 3 — MEW: aile üyelerini bulma, sağ tıkta dört yön, açma ve kenara yerleştirme

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

MEW'in kompakt simgesi hub oldu. Yüklü aile üyelerini kendiliğinden buluyor. Simgeye sağ tıklanınca dört yanında bu
üyeler görünüyor; birine tıklanınca o widget açılıp simgenin o kenarına yerleşiyor. Hiç üye yoksa simgenin sağında
"Aileden başka widget yüklü değil" yazıyor.

## Problem

- **Gereksinim (örnek kullanım):** MEW simgesine sağ tıklanınca dört yanında diğer widget uygulamaları açılabilir.
- **Gereksinim (T6):** İş bitene kadar sürdürülür ve testleri yapılır; 12.43–13.05 arasında canlı test yapılmaz.
- **Mevcut durum:** Kompakt simgenin sağ tık menüsü yoktu; MEW başka uygulamalardan habersizdi.

## Çözüm

- **Hub:** MEW çalıştığı sürece `HubServer` açık; bağlanan üyeler görev çubuğundan çekiliyor.
- **Keşif:** `AppExtensionFamilyCatalog`, `com.melihcelenk.widgetfamily` uzantısını bildiren paketleri her sağ tıkta
  yeniden okuyor; kurulan ya da kaldırılan üye yeniden başlatmadan görünür ya da düşer. Yalnız paketli MEW'de çalışır.
- **Menü:** Her üye manifestinde önerdiği kenarı bildirir; o kenar doluysa saat yönünde sıradaki boş kenara geçer
  (S03 → A). Menü, simgenin etrafında, pencere dışına taşan bir açılır pencere (`FamilyPopup`).
- **Açma ve yerleşme:** Tıklanan üye `<protokol>:open?edge=…&anchor=…` adresiyle açılıyor; üye kendini simgenin o
  kenarına yerleştiriyor (zaten açıksa öne geliyor).

```
                 [ Üst üye ]
   [ Sol üye ]  [ MEW simgesi ]  [ Sağ üye: Task Timer Widget ]
                 [ Alt üye ]
```

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 3.1 | MEW yüklü aile üyelerini bulur ve kurulup kaldırılmalarını izler. | 🟢 Tamamlandı |
| 3.2 | Sağ tık menüsünün görsel taslağı gösterilir. | 🟢 Tamamlandı (`screens/`) |
| 3.3 | Sağ tıkta üyeler simgenin dört yanında görünür. | 🟢 Tamamlandı |
| 3.4 | Tıklanan üye açılır ve simgenin o kenarına yerleşir. | 🟢 Tamamlandı |
| 3.5 | İki paket birlikte Sandbox'ta uçtan uca test edilir. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Dört yönde kim nerede duracak? | A: widget önerir, doluysa sıradaki boş kenar | 🟢 Verildi (A) | S03 |

## Nasıl kontrol edilir

- [ ] Task Timer kuruluyken MEW simgesine sağ tıklanınca Task Timer sağda görünüyor.
- [ ] Ona tıklanınca Task Timer açılıp simgenin sağına yerleşiyor.
- [ ] Task Timer kaldırılınca menüde "Aileden başka widget yüklü değil" yazıyor.

## Kalan

- Yok.

## Ayrıntılar

### 3.1 — MEW yüklü aile üyelerini bulur ve kurulup kaldırılmalarını izler.

- **Mevcut durum:** MEW başka uygulamalardan habersizdi.
- **Problem:** Hub'ın üyeleri kod değişikliği olmadan tanıması gerekir.
- **Çözüm:** `Package.appxmanifest`'e `windows.appExtensionHost` eklendi. `AppExtensionFamilyCatalog` uzantıları
  bulur, özelliklerini (`#text` iç içe yapısı) `FamilyExtensionProperties` ile metne çevirir ve
  `FamilyMember.TryRead` ile okur; eksik bildirim loglanıp atlanır. Paketsiz çalışmada boş liste döner.
- **Dosyalar:** `src/MyEverythingWidget.Infrastructure/Family/`, `src/MyEverythingWidget.Core/Family/FamilyServices.cs`,
  `src/MyEverythingWidget.App/Package.appxmanifest`
- **Testler:** `FamilyExtensionPropertiesTests` (4).
- **Durum:** 🟢 Tamamlandı.

### 3.2 — Sağ tık menüsünün görsel taslağı gösterilir.

- **Mevcut durum:** Yalnız `WIDGET_FAMILY.md`'de metin taslağı vardı.
- **Problem:** Tasarım değişikliği görsel taslakla gösterilir.
- **Çözüm:** Taslak bu dokümanın Çözüm bölümünde; gerçek görüntüler Sandbox testinden: `screens/family-menu.png`
  (menü), `screens/family-menu-at-edge.png` (ekran kenarında), `screens/family-member-placed.png` (yerleşmiş Task
  Timer). Kullanıcı işin bitmesini istediği için (T6) menü taslakla birlikte kodlandı; beğenilmezse düzen değiştirilir.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml`, `screens/*.png`
- **Testler:** —
- **Durum:** 🟢 Tamamlandı.

### 3.3 — Sağ tıkta üyeler simgenin dört yanında görünür.

- **Mevcut durum:** Kompakt simgenin sağ tık menüsü yoktu.
- **Problem:** Gereksinimdeki dört yönlü açılış.
- **Çözüm:** `EdgeAssignment` (Core) kenarları dağıtır; `FamilyMenuViewModel` dört kenarın üyesini tutar;
  `MainWindow.Family.cs` sağ tıkta (`ContextRequested`) listeyi yenileyip menüyü açar. Her düğmenin yeri üyenin
  kendi yerleşim kuralıyla (`Placement.NextTo`) hesaplanır: ekran kenarında düğme ekranda kalır ve üyenin gerçekten
  açılacağı tarafa (karşı kenar) geçer. İlk Sandbox koşusu düğmenin ekran dışına taştığını gösterdi; bu kuralla
  düzeltildi (`40e1609`). Düğme metni üyenin manifestteki
  adı; üye yoksa yeni çevrilmiş `FamilyEmpty` metni (15 dil).
- **Dosyalar:** `src/MyEverythingWidget.Core/Family/EdgeAssignment.cs`, `src/MyEverythingWidget.Presentation/FamilyMenuViewModel.cs`,
  `src/MyEverythingWidget.App/MainWindow.xaml`, `MainWindow.Family.cs`, `Bindings.cs`, `Localization/Strings*.resx`
- **Testler:** `EdgeAssignmentTests` (6), `FamilyMenuViewModelTests` (menü: 3), `LocalizationCoverageTests`; Sandbox:
  `WidgetFamilyTests` (ekran kenarı testi dahil).
- **Durum:** 🟢 Tamamlandı.

### 3.4 — Tıklanan üye açılır ve simgenin o kenarına yerleşir.

- **Mevcut durum:** —
- **Problem:** Açılan widget hub'ın yanında durmalı; ekran kenarında içeri kaydırılmalı.
- **Çözüm:** `UriFamilyLauncher` açma adresini başlatır; konumu üye ortak kütüphanedeki `Placement.NextTo` ile kendisi
  hesaplar (Faz 1.5).
- **Dosyalar:** `src/MyEverythingWidget.Infrastructure/Family/UriFamilyLauncher.cs`, `MainWindow.Family.cs`
- **Testler:** `FamilyMenuViewModelTests` (açma: 2); Sandbox: `WidgetFamilyTests`.
- **Durum:** 🟢 Tamamlandı.

### 3.5 — İki paket birlikte Sandbox'ta uçtan uca test edilir.

- **Mevcut durum:** Sandbox'ta yalnız MEW kuruluyordu.
- **Problem:** Görev çubuğu, tek örnek ve yerleşme yalnız gerçek paketlerle doğrulanabilir (Faz 2.4 dahil).
- **Çözüm:** `scripts/build-member-msix.ps1` Task Timer'ın imzasız, bağımsız (self-contained) paketini üretir;
  `scripts/test-ui.ps1` onu MEW'in yanına kurar. `WidgetFamilyTests`:
  1. Task Timer tek başına görev çubuğunda.
  2. MEW açılınca görev çubuğundan kalkıyor.
  3. Sağ tıkta sağda görünüyor; tıklanınca simgenin sağına yerleşiyor.
  4. Simge sürüklenince peşinden geliyor (Faz 4).
  5. MEW çökünce açık kalıp görev çubuğuna dönüyor (S04).
  6. İkinci başlatma ikinci pencere açmıyor.
  7. Simge ekranın sağ kenarındayken menü ekranda kalıyor, Task Timer solda açılıyor.

  Sonuç: `WidgetFamilyTests` 3/3; tüm UI paketi 131 test. Tüm pakette `PackagedAppTests` bir kez kaldı: aile testleri
  paketli MEW'i kompakt modda bırakıyordu (aynı paket verisi). Aile testleri artık bitince paketli MEW'in ayarlarını
  siliyor; ikisi birlikte yeniden koşuldu, 4/4 yeşil.
- **Dosyalar:** `scripts/build-member-msix.ps1`, `scripts/test-ui.ps1`, `tests/MyEverythingWidget.UiTests/WidgetFamilyTests.cs`,
  `tests/MyEverythingWidget.UiTests/Infrastructure/Taskbar.cs`
- **Testler:** `WidgetFamilyTests` (3).
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- Sonar IDE'de çalışmadı (dosyalar tanınmadı); derleme 0 uyarı, 0 hata.

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 3
- `WIDGET_FAMILY.md` → 4. Yaklaşımlar → A
