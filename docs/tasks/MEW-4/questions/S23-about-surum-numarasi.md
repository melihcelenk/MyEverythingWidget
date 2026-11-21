---
id: S23
status: answered
decider: user
priority: major
asked: 2026-11-21
---
# S23 — About kartı sürümü hep "1.0.0" gösteriyor: düzeltme hangi sürümle çıksın?

**Mevcut durum:** Store'a gönderilen 1.1.0 paketi About kartında "Sürüm 1.0.0" yazıyor; 1.0.1'de de böyleydi.
**Soru:** Düzeltmeyi yapıp sertifikasyondaki 1.1.0'ı geri çekerek yeniden mi gönderelim, yoksa bir sonraki sürüme mi bırakalım?

## Bağlam

- **Sebep:** About kartı sürümü programın derleme sürümünden okuyor
  (`MainViewModel.Version` → `Assembly.GetName().Version`). Projede bu sürüm hiç ayarlanmadığı için hep varsayılan
  `1.0.0` çıkıyor.
- **Store'un sürümü ayrı bir yerde:** Store paketinin sürümü `StoreIdentity.json`'dan paket manifestine yazılıyor ve
  1.0.1, 1.1.0 diye ilerledi. İki sürüm birbirinden habersiz; 1.0.0'da tesadüfen aynıydı.
- **Önerilen düzeltme:**
  - Paketli çalışırken About, sürümü doğrudan paketin kimliğinden (`Package.Current.Id.Version`) okur. Böylece tek
    kaynak `StoreIdentity.json` olur.
  - Geliştirme sürümünde (paketsiz) program sürümü gösterilir.
  - Test: paketli Sandbox testi, About'taki sürümün manifestteki sürümle aynı olduğunu kontrol eder.
- **1.1.0'ın durumu:** Partner Center'da "Update in certification", ön işleme aşamasında. Bu aşamada **Cancel
  certification** ile geri çekilip paketler değiştirilebiliyor; Store sayfası metinleri ve ayarlar korunur.

## Seçenekler

### A — Düzelt, 1.1.0'ı geri çekip yeniden gönder ⭐

Düzeltme ve testi yapılır, 1.1.0 paketleri yeniden oluşturulur. Sen Partner Center'da **Cancel certification**'a
basarsın; Packages'ta eski 1.1.0 paketlerini kaldırıp yenilerini yüklersin ve yeniden gönderirsin. Sertifikasyon
süresi baştan başlar.

### B — Gönderim kalsın, düzeltme 1.1.1'de çıksın

1.1.0 yayınlanır, About bir süre "1.0.0" yazar. Düzeltme hemen yapılır ve bir sonraki güncellemeyle (ya da ayrıca
1.1.1 olarak) gönderilir.

## Öneri

A. Gönderim henüz ön işlemede; geri çekmek ucuz. Kullanıcıya yanlış sürüm numarası göstermemek, destek taleplerinde
hangi sürümün kullanıldığını bilmek için de önemli.

## Cevap

**B — Gönderim kalsın, düzeltme 1.1.1'de çıksın**

B. Sonraki güncellemede düzeltilir, sorun olmaz, henüz pek kullanıcımız yok. Ama bunu garanti etmen gerekiyor, sana sürekli sürümü düzeltmen gerektiğini söylememeliyim.

## Sonuç

B uygulandı:

- **Gönderim:** Sertifikasyondaki 1.1.0 olduğu gibi kaldı; o sürümde About "1.0.0" gösterecek.
- **Düzeltme (bir sonraki güncellemede çıkacak):**
  - Bütün programların sürümü artık `StoreIdentity.json`'daki Store sürümünden okunuyor (`Directory.Build.props`).
  - About kartı bu sürümü gösteriyor. Sürümü yükseltmek için yalnız `StoreIdentity.json` değiştirilir; Store paketi ve
    About aynı numarayı taşır.
- **Garanti:** `Presentation.Tests/AppVersionTests.AboutVersion_IsTheStorePackageVersion`, About'taki sürümün
  `StoreIdentity.json`'dakiyle aynı olduğunu kontrol ediyor. İki sürüm ayrılırsa `dotnet test` kırmızı olur. Önce
  kırmızıydı (beklenen 1.1.0, gelen 1.0.0), düzeltmeden sonra yeşil; bütün birim testleri 384/384.

Kontrol: uygulandı — `Directory.Build.props` sürümü `StoreIdentity.json`'dan alıyor; `AppVersionTests` yeşil ve About
artık 1.1.0 gösteriyor (sonraki Store güncellemesinde kullanıcılara ulaşacak).

