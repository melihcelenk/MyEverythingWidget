---
id: S6
status: open
decider:
priority: major
asked: 2026-10-30
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
- ❌ "Önce pencere, sonra içerik" görüntüsü; şikâyet ettiğin "sonradan gelme" hissine benzeyebilir.

### C — Yalnız hafif ızgara (A'nın ilk yarısı)

- Sonraki açılışlar hızlanır; ilk açılışın font maliyeti kalır.

## Öneri

A. Hem her açılıştaki yarım saniyeyi hem ilk açılıştaki uzun beklemeyi hedefliyor. Her iki etkiyi de ölçen bir test
yazıp (tıklamadan pencerenin ekranda görünmesine kadar geçen süre) sonucu sayılarla getiririm.

## Cevap

## Sonuç
