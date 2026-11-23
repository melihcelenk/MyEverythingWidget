# Faz 5 — Kurulu olmayan aile widget'ını indirmeye yönlendirme ve kurulu halin gösterimi

> **Durum:** 🟡 Kısmi (5.2 kullanıcının indirme menüsünü görmesini bekliyor) · **Tamamlanma:** 80% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

Kompakt simgeye sağ tıklanınca, kurulu olmayan aile widget'ları artık "Task Timer Widget uygulamasını indir" diye
görünüyor; tıklanınca Microsoft Store'daki sayfası açılıyor. Kurulu olanlar önceki gibi adlarıyla görünüyor ve
tıklanınca simgenin yanında açılıyor. Kullanıcı indirme menüsünü gördükten sonra kurulu hal de bu bilgisayarda
açılıp gösterilir.

## Problem

- **Gereksinim (T12):** Aile widget'ı kurulu değilse menü, onu indirmeye yönlendirir.
- **Gereksinim (T12):** Kullanıcı indirme menüsünü gördükten sonra widget'ın kurulu olduğu hal hazırlanır ve
  uygulama onunla açılıp gösterilir.
- **Mevcut durum:** Kurulu üye yoksa menüde yalnız "Aileden başka widget yüklü değil" yazıyordu; kullanıcının
  denemesinde (geliştirme sürümü paketsiz olduğu için) bu çıktı.

## Çözüm

- **Bilinen aile widget'ları:** `Core/Family/KnownFamilyMembers` yayımlanmış aile widget'larını ve Store ürün
  kimliklerini tutar (şimdilik Task Timer Widget, `9NF0N9LN349G`). Yeni bir aile widget'ı yayımlanınca buraya eklenir.
- **Menü:** Kurulu üyeler kenarlarını önce seçer; kurulu olmayan bilinen widget'lar kalan kenarlara "{0} indir"
  düğmesi olarak gelir (`FamilySlot.IsInstalled = false`). Aynı widget hem kurulu hem bilinen ise bir kez, kurulu
  olarak görünür.
- **Tıklama:** Kurulu değilse `ms-windows-store://pdp/?ProductId=…` ile Store sayfası açılır; simgeyi izleyen üyeler
  listesine eklenmez.
- **Metin:** `FamilyGet` ("Get {0}") 15 dilde.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 5.1 | Kurulu olmayan aile widget'ı menüde indirme düğmesi olarak görünür ve Store sayfasını açar. | 🟢 Tamamlandı |
| 5.2 | Kurulu hal bu bilgisayarda hazırlanıp uygulama onunla açılarak gösterilir. | ⏳ Bekliyor (kullanıcının indirme menüsünü görmesi) |
| 5.3 | UI testleri Sandbox dışında kullanıcının panosuna yazmaz. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- [ ] Geliştirme sürümünde sağ tık: simgenin sağında "Task Timer Widget uygulamasını indir"; tıklanınca Store açılıyor.
- [ ] Kurulu halde sağ tık: "Task Timer Widget"; tıklanınca Task Timer simgenin yanında açılıyor.

## Kalan

- **5.2:** Kullanıcı indirme menüsünü gördükten sonra.

## Ayrıntılar

### 5.1 — Kurulu olmayan aile widget'ı menüde indirme düğmesi olarak görünür ve Store sayfasını açar.

- **Mevcut durum:** Kurulu üye yoksa yalnız bilgi metni vardı.
- **Problem:** Gereksinim (T12): kurulu değilse indirmeye yönlendirilir.
- **Çözüm:** Yukarıdaki Çözüm bölümü.
- **Dosyalar:** `src/MyEverythingWidget.Core/Family/KnownFamilyMembers.cs`, `src/MyEverythingWidget.Core/Family/FamilyServices.cs`,
  `src/MyEverythingWidget.Presentation/FamilyMenuViewModel.cs`, `src/MyEverythingWidget.Infrastructure/Family/UriFamilyLauncher.cs`,
  `src/MyEverythingWidget.App/Bindings.cs`, `src/MyEverythingWidget.App/App.xaml.cs`, `Localization/Strings*.resx`
- **Testler:** `KnownFamilyMembersTests` (2); `FamilyMenuViewModelTests`: indirme önerisi, Store sayfası, kurulu olanın
  bir kez görünmesi, kurulu olanların kenar önceliği (4); Sandbox: `WidgetFamilyTests.FamilyWidgetThatIsNotInstalled_IsOfferedForDownload`
  (Task Timer'ı geçici kaldırıp sonra yeniden kurar) — `WidgetFamilyTests` 4/4 ve `PackagedAppTests` yeşil. Görüntü:
  `screens/family-menu-download.png`.
- **Durum:** 🟢 Tamamlandı.

### 5.2 — Kurulu hal bu bilgisayarda hazırlanıp uygulama onunla açılarak gösterilir.

- **Mevcut durum:** Kurulu hal yalnız Sandbox'ta denendi.
- **Problem:** Gereksinim (T12): kullanıcı kurulu hali kendi bilgisayarında görmek istiyor.
- **Çözüm:** Geliştirme paketleri (imzasız MEW ve Task Timer) Store sürümlerinden farklı paket kimliğiyle kurulur;
  Store sürümleri ve verileri etkilenmez. Paketli geliştirme MEW'i açılır.
- **Dosyalar:** —
- **Testler:** Kullanıcının gözü.
- **Durum:** ⏳ Bekliyor.

### 5.3 — UI testleri Sandbox dışında kullanıcının panosuna yazmaz.

- **Mevcut durum:** `ImageCopyTests.LaunchWithImage`, Sandbox denetiminden önce panoya yazıyordu; bu bilgisayarda
  `dotnet test` kullanıcının panosunu değiştiriyor, pano meşgulken de test hatası veriyordu.
- **Problem:** UI testleri kullanıcının masaüstüne dokunmamalı.
- **Çözüm:** `SandboxClipboard` panoya her erişimden önce Sandbox denetimini yapıyor; Sandbox dışında test atlanıyor.
- **Dosyalar:** `tests/MyEverythingWidget.UiTests/Infrastructure/SandboxClipboard.cs`
- **Testler:** Bu bilgisayarda `dotnet test`: 546 test, 0 hata (UI testleri atlandı).
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- Paketsiz MEW de uzantı kataloğunu okuyabiliyor (ilk Sandbox koşusu bunu gösterdi); bu yüzden geliştirme sürümü
  de kurulu aile widget'larını görüyor.
- Store'un açılması Sandbox'ta denenemez (ağ yok); testte yalnız düğme metni kontrol ediliyor.

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 5
