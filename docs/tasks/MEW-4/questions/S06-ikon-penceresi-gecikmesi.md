---
id: S6
status: resolved
decider: user
priority: major
asked: 2026-10-30
resolved: 2026-11-18
---
# S6 — İkon penceresinin geç açılması: hangi çözüm?

**Mevcut durum:** Gecikmenin sebebi bulundu. Pencerenin kendisi geç çiziliyor; ilk açılışta en büyük pay renkli emoji fontunun ilk kullanımı.

**Soru:** Aşağıdaki çözümlerden hangisiyle ilerleyeyim?

## Bağlam

Ölçüm Sandbox'ta yapıldı; senin bilgisayarın daha hızlı, sayılar orantılı olarak daha küçüktür.

| Adım | 1. açılış | 2. ve sonraki açılışlar |
|------|-----------|-------------------------|
| Pencere ve içeriğin kod ile kurulması | 71 ms | 8 ms |
| Yerleşim (56 emoji düğmesi, sekmeler) | 370 ms | 156 ms |
| Diyaloğun açılması (`Opened`) | +2,2 s | +20 ms |
| Ekranda görünmesi | ~3,3 s | ~0,43–0,67 s |

- **Çizim adımları:**
  - Pencere ekrana tek seferde, sekmeleriyle birlikte geliyor.
  - Ondan sonra sekmeler ayrıca değişmiyor; 30 ms aralıklı kareler aynı.
  - Gecikme, menüye tıklamak ile pencerenin belirmesi arasında.
- **İlk açılış:**
  - 2,2 saniyenin sebebi renkli emoji fontunun (Segoe UI Emoji) ilk kez çizilmesi.
  - Bunu, açılıştan sonra emojileri görünmeden bir kez çizdirerek doğruladım: arayüz 2,6 s dondu.
  - O denemeyi geri aldım; kodda değişiklik yok.
- **Sonraki açılışlar:** ~0,5 s'nin bileşenleri:
  - 56 tam `Button`'ın yerleşimi (~150 ms).
  - WinUI'nin diyalog açılış animasyonu (~250 ms).
- **Ana penceredeki kategori sekmeleri:** pencereyle birlikte, ilk karede çiziliyor; sorun orada değil.

## Seçenekler

### A — Emoji ızgarasını hafiflet + fontu arka planda ısıt ⭐

- **Hafif ızgara:** 56 `Button` yerine her emoji için tek bir hafif öğe (metin + üzerine gelince vurgu, tıklama ve
  klavye ile seçim). Yerleşim ~150 ms'den onlarca ms'ye iner.
- **Arka planda ısıtma:** Fontun ilk yüklenmesini uygulama açıldıktan sonra arayüzü dondurmadan, arka plan iş
  parçacığında yap. Windows'un metin motoruyla (DirectWrite) emojileri bir kez ölçmek fontu belleğe alır.
- ✅ İlk açılış da sonraki açılışlar da hızlanır.
- ❌ Arka plan ısıtmanın arayüz tarafındaki çizim maliyetini ne kadar düşürdüğü ölçülerek doğrulanmalı; yetmezse
  ilk açılışta yine bir miktar bekleme kalır (sonucu raporlarım).

### B — Pencereyi hemen aç, emojileri açıldıktan sonra doldur

- Pencere sekmeler ve alt düğmelerle hemen görünür; emoji ızgarası bir an sonra dolar.
- ✅ Tıklamaya anında tepki.
- ❌ İlk açılışta emojiler gelene kadar pencere birkaç saniye donuk kalabilir (font maliyeti yerinde durur).
- ❌ Önce pencerenin, sonra içeriğin geldiği bir görüntü oluşur; bu, bildirilen içeriğin sonradan gelmesi sorununa
  benzeyebilir.

### C — Yalnız hafif ızgara (A'nın ilk yarısı)

- Sonraki açılışlar hızlanır; ilk açılışın font maliyeti kalır.

## Öneri

A. Hem her açılıştaki yarım saniyeyi hem ilk açılıştaki uzun beklemeyi hedefliyor. Her iki etkiyi de ölçen bir test
yazıp (tıklamadan pencerenin ekranda görünmesine kadar geçen süre) sonucu sayılarla getiririm.

## Cevap

**A — Emoji ızgarasını hafiflet + fontu arka planda ısıt**

## Sonuç

A uygulandı (2026-10-31), commit `072d03c`, push'lu; PR #1 güncellendi.

- **Hafif ızgara:** emoji ızgarası `Button` yerine hafif `EmojiCell` hücreleriyle. Fare, Enter/Boşluk ve UI
  Automation (Invoke) ile seçim korunuyor.
- **Isınma:**
  - Önerdiğim arka plan iş parçacığı yolu işe yaramadı. Font dosyasını okumak da, DirectWrite ile önceden yerleşim
    yaptırmak da ilk açılışı değiştirmedi; maliyet emojilerin **çizilmesinde**.
  - Bunun yerine emojiler açılıştan sonra, görünmeyen bir katmanda (opak zeminin arkasında) 60 ms arayla birer birer
    çiziliyor. Arayüzde fark edilir bir donma olmuyor.
- **Yeniden kullanım:** Isınma bitince ikon penceresi bir kez kuruluyor ve her açılışta yeniden kullanılıyor.
- **Ölçüm (Sandbox, yazılımla çizim):**
  - İlk açılış 3,6 s → 0,4–0,6 s.
  - Sonraki açılışlar ~0,5 s → 0,16–0,23 s.
  - "Önce" rakamları daha yavaş bir ölçüm yöntemiyle alındı (ayrıntı `PHASE14.md` → 14.5).
- **Bedel:** private bellek ~90 MB → ~139 MB (önceden çizilen emojiler ve hazır pencere).
- **Test altyapısı:** UI test süreci DPI'ya duyarlı yapıldı. Sandbox ekran ölçeği değişince renk örnekleyen testler
  eski kodda da düşüyordu.
- **Testler:** tam UI suite 73/74 → ölçüm düzeltmesinden sonra ilgili test 3/3; unit 293/293.

Kontrol: uygulandı — `EmojiCell.cs`, `EmojiFontWarmUp.cs` (`MainWindow.xaml.cs`:94), yeniden kullanılan pencere (`IconPickerDialog.Instances`), `TabAppearanceTests.IconDialog_OpensQuickly`, commit `072d03c`.
