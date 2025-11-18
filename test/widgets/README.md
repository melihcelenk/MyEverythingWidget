# Widget Testing Strategy

## Testing Approach

Bu projede layout problemlerini (spacing, overlap, alignment) tespit etmek için **iki yöntem** kullanıyoruz:

1. **Overlap Detection Tests** - `tester.getRect()` ile gerçek zamanlı overlap kontrolü
2. **Golden Testing** - Alchemist ile görsel regresyon tespiti

### Neden Golden Testing?

Traditional widget testlerde pixel koordinatları ve boyutları elle hesaplamak:
- ❌ Hata yapmaya açık
- ❌ Bakımı zor
- ❌ Görsel problemleri görmek imkansız

Golden testing ile:
- ✅ Görsel regresyonları otomatik tespit eder
- ✅ Layout değişikliklerini %12.29 hassasiyetle yakalar
- ✅ Diff görüntüleri ile değişiklikleri görsel olarak inceler
- ✅ CI/CD pipeline'a entegre edilebilir

### Kurulum

```yaml
# pubspec.yaml
dev_dependencies:
  alchemist: ^0.13.0
```

### Test Çalıştırma

**Golden baseline oluşturma/güncelleme:**
```bash
flutter test --update-goldens test/widgets/icon_picker_golden_test.dart
```

**Golden testleri çalıştırma:**
```bash
flutter test test/widgets/icon_picker_golden_test.dart
```

### Test Başarısız Olduğunda

Test başarısız olursa, `test/widgets/failures/` klasöründe şu dosyalar oluşur:

- `*_masterImage.png` - Baseline (beklenen) görüntü
- `*_testImage.png` - Yeni render edilen görüntü
- `*_isolatedDiff.png` - Farklılıklar (siyah/beyaz)
- `*_maskedDiff.png` - Maskelenmiş farklılıklar

**Örnek Analiz:**

```
Golden "icon_picker_emoji_grid.png": Pixel test failed, 12.29%, 16279px diff detected.
```

Bu durumda:
1. `failures/` klasöründeki diff görüntülerini incele
2. Değişiklik beklenen mi?
   - ✅ Evet → `--update-goldens` ile baseline'ı güncelle
   - ❌ Hayır → Kodu düzelt ve tekrar test et

### Örnek: Spacing Problemi Tespiti

**Problem:** Emojiler birbirine yapışmış, spacing çok az (4px)

**Çözüm Adımları:**

1. Golden test çalıştır → Baseline oluştur
2. Görüntüyü incele → Problem görünür
3. Spacing'i artır (4px → 12px)
4. Test tekrar çalıştır → **%12.29 fark tespit edilir!**
5. Diff görüntüsünü incele → Beyaz alanlar spacing artışını gösterir
6. Baseline'ı güncelle → `--update-goldens`

### Best Practices

1. **Her layout değişikliğinden önce golden test çalıştır**
2. **Diff görüntülerini mutlaka incele** - otomatik kabul etme
3. **Golden dosyalarını git'e commit et** - ekip genelinde tutarlılık
4. **CI pipeline'da golden testleri çalıştır** - regresyon önle
5. **Farklı platform'lar için ayrı golden'lar kullan** (windows/, ci/)

## Overlap Detection Tests (Recommended ✅)

`icon_picker_overlap_test.dart` dosyası gerçek overlap tespiti yapar.

### Nasıl Çalışır?

```dart
// Grid içindeki her item çiftini karşılaştır
for (int i = 0; i < count; i++) {
  for (int j = i + 1; j < count; j++) {
    final rect1 = tester.getRect(items.at(i));
    final rect2 = tester.getRect(items.at(j));

    // Overlap kontrolü
    expect(rect1.overlaps(rect2), false);
  }
}
```

### Avantajları

- ✅ **Gerçek overlap tespiti** - GridView parametrelerine değil, render edilen bileşenlere bakar
- ✅ **Hızlı** - Golden testlerden çok daha hızlı çalışır
- ✅ **Kesin** - Pixel-perfect accuracy
- ✅ **CI-friendly** - Platform bağımsız, font rendering sorunları yok

### Test Coverage

- ✅ Emoji grid items overlap detection
- ✅ Icon grid items overlap detection
- ✅ Horizontal spacing verification (≥12px)
- ✅ Vertical spacing verification (≥12px)

### Icon Picker Golden Test Coverage

- ✅ Emoji grid görsel snapshot
- ✅ Material icon grid görsel snapshot
- ✅ Upload area layout snapshot

### Kaynaklar

- [Alchemist Documentation](https://pub.dev/packages/alchemist)
- [Flutter Golden Testing Guide](https://docs.flutter.dev/cookbook/testing/widget/golden)
- [Best Practices Blog](https://vibe-studio.ai/insights/flutter-widget-testing-best-practices-golden-tests-and-screenshot-diffs)
