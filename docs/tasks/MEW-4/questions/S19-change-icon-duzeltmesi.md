---
id: S19
status: answered
decider: user
priority: critical
asked: 2026-11-20
---
# S19 — "Change icon" donmasının düzeltmesi ve 1.0.1 güncellemesi

**Mevcut durum:** Sebep bulundu (S18): pencere ekranda değilken sekmesi geri alınınca WinUI takılıyor; Store'daki 1.0.0 sürümünde bu hata var.
**Soru:** Aşağıdaki düzeltmeyi yapıp 1.0.1 olarak Store'a gönderilecek paketi hazırlayayım mı?

## Bağlam

- **Hata:** "Change icon" penceresinde "Select image" sekmesine geçip Cancel ya da Esc ile kapatınca, pencereyi bir
  sonraki açışta uygulama donuyor. Kullanıcı yalnız uygulamayı kapatarak kurtulabiliyor. Döküm ve Sandbox testi aynı
  yeri gösteriyor: `IconPickerDialog.Reset()` → `_iconTab.IsSelected = true`.
- **Neden:** Pencere hızlı açılsın diye bir kez kurulup tekrar kullanılıyor. Her açılışta sekme "Select icon"a geri
  alınıyor, ama bu iş pencere henüz ekranda değilken yapılıyor. Sekme çubuğu (`SelectorBar`) o an görsel ağaçta
  olmadığı için WinUI seçim değişikliğinde sonsuz döngüye giriyor.
- **Test (kırmızı):** `AppItemTests.IconDialog_OpensAgain_AfterItWasUsedOnce`, `ImageTabThenCancel` ve
  `ImageTabThenEscape` senaryolarında başarısız oluyor (6 senaryodan 2'si).

## Seçenekler

### A — Sekmeyi pencere açıldıktan sonra geri al ⭐

Sekme, pencere ekrana geldiğinde (`ContentDialog.Opened`) "Select icon"a alınır. Pencere yine tekrar kullanılır, açılış
hızı aynı kalır. Değişiklik `IconPickerDialog.cs` içinde birkaç satır.

### B — Sekmeyi kapanırken geri al

Sekme, pencere kapanırken (`Closing`, pencere hâlâ ekrandayken) "Select icon"a alınır. Kapanış anında sekmenin bir an
değiştiği görülebilir.

### C — Pencereyi her açılışta yeniden kur

Tekrar kullanma kaldırılır. Sekme sorunu kökten kalkar, ama emoji ızgarası her açılışta yeniden kurulduğu için pencere
daha yavaş açılır. Tekrar kullanma da zaten bunun için eklenmişti.

## Öneri

A. Pencere hızlı açılmaya devam eder ve seçim, sekme çubuğu ekrandayken değişir. Ardından:

- Testin altı senaryosu ve tam UI test takımı (~12 dk) Sandbox'ta çalıştırılır.
- Sürüm 1.0.1 yapılır (`StoreIdentity.json`) ve iki Store paketi hazırlanır.
- Değişiklikler yeni bir branch ve PR ile gelir.
- Store'a gönderim senin Partner Center hesabınla yapılır (Packages bölümüne yeni paketler).

## Cevap

**A — Sekmeyi pencere açıldıktan sonra geri al**

## Sonuç

A uygulandı:

- **Düzeltme:** `IconPickerDialog` sekmeyi artık pencere ekrana geldiğinde (`ContentDialog.Opened`) "Select icon"a alıyor.
  Pencere ekranda değilken sekme çubuğuna dokunulmuyor. Pencere yine bir kez kurulup tekrar kullanılıyor, açılış
  hızı değişmedi.
- **Testler:**
  - `AppItemTests.IconDialog_OpensAgain_AfterItWasUsedOnce`: 6/6 (düzeltmeden önce 4/6).
  - Birim testleri 309/309.
  - Tam UI takımı 104 testten 103'ü geçti. Geçmeyen
    `CompactAndMenuTests.IconOnTheRight_OpensWithTheRightEdgesLinedUp_AndShrinksBackToTheSamePlace(bottom: True)`
    Sandbox'ın fare girişinden geldi (`SendInput failed with error 5`), tek başına yeniden çalıştırılınca 2/2 geçti.
- **Sürüm:** `StoreIdentity.json` → `1.0.1.0`. İki Store paketi hazır:
  - `tmp/store-x64/MyEverythingWidget.App_1.0.1.0_x64_Test/MyEverythingWidget.App_1.0.1.0_x64.msix`
  - `tmp/store-arm64/MyEverythingWidget.App_1.0.1.0_arm64_Test/MyEverythingWidget.App_1.0.1.0_arm64.msix`
- **Kalan:**
  - Değişiklikler commit'lenmedi.
  - Store'a yeni gönderimi kullanıcı Partner Center'dan yapacak: Update → Packages → eski paketleri kaldırıp yenilerini
    yüklemek.

Kontrol: uygulandı — `IconPickerDialog.cs`'te `Reset()` sekmeye dokunmuyor, `Opened` olayı sekmeyi seçiyor; paket
manifestlerinde `Version="1.0.1.0"`.

