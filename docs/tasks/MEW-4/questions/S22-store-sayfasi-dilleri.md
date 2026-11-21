---
id: S22
status: resolved
decider: user
priority: blocker
asked: 2026-11-21
resolved: 2026-11-21
---
# S22 — Store sayfası 14 dilde "Incomplete": çevirelim mi, kaldıralım mı?

**Mevcut durum:** Paket 15 dili bildirdiği için Partner Center her dil için bir Store sayfası istiyor; İngilizce dışındaki 14'ü "Incomplete" ve gönderim bu yüzden bekliyor.
**Soru:** Store sayfasını 14 dile çevirip içeri aktaralım mı, yoksa bu dilleri Store sayfasından kaldırıp yalnız İngilizceyle mi gönderelim?

## Bağlam

- **Yanılgım:** Daha önce "diğer diller için ayrı Store sayfası gerekmiyor" demiştim. Bu yanlıştı: Partner Center,
  paketin bildirdiği her dil için Store sayfası bekliyor (Manage Store listing languages → "Languages supported in
  packages").
- **Uygulamanın kendisi:** Hangi seçenek seçilirse seçilsin uygulama 15 dilde çalışır. Bu karar yalnız Store
  sayfasının metinleriyle ilgili.
- **Bir dilin sayfasında olanlar:** Açıklama, kısa açıklama, özellik listesi, anahtar kelimeler, "What's new" ve ekran
  görüntüleri. Ekran görüntüleri İngilizce kalabilir.
- **İçeri aktarma:** Store listings sayfasındaki **Export listings** düğmesi bütün dillerin alanlarını içeren bir CSV
  dosyası verir; **Import listings** aynı dosyayı geri yükler. Böylece 14 dil tek seferde doldurulur.

## Seçenekler

### A — 14 dile çevirip CSV ile içeri aktar ⭐

Sen **Export listings** ile CSV'yi indirip yolunu yazarsın. Ben 14 dilin metinlerini (uygulamadaki çevirilerle aynı
terimlerle) doldururum. Sen **Import listings** ile geri yüklersin. Store'da her dildeki kullanıcı kendi dilinde sayfa
görür ve kendi dilindeki aramalarda uygulama daha kolay bulunur. Ek süre: yaklaşık 30–45 dakika (çoğu bende).

### B — 14 dili Store sayfasından kaldır, yalnız İngilizce

Her satırdaki **Remove** ile 14 dil kaldırılır ve **Save**'e basılır. Gönderim hemen yapılabilir; bu dillerdeki
kullanıcılar İngilizce sayfayı görür. Çeviri sonraki sürüme kalır.

## Öneri

A. Uygulama zaten 15 dilde. Store sayfası da o dillerde olursa yeni dillerin getirisi Store'da da görünür. CSV ile
yükleme tek seferde olur. Acele varsa B de güvenli; A sonraki sürümde yapılır.

## Cevap

**A — 14 dile çevirip CSV ile içeri aktar**

## Sonuç

A uygulandı:

- **Kaynak:** Kullanıcı, Partner Center'dan Store sayfalarının CSV'sini indirdi (`Export listings`).
- **Çeviri:** İngilizce sayfanın şu alanları 14 dile çevrildi: açıklama, "What's new", kısa açıklama, 7 özellik, 3 görsel
  başlığı, 7 anahtar kelime.
  - Çeviriyi üç alt ajan yaptı; uygulamadaki çevirilerle aynı terimler kullanıldı.
  - Store'un uzunluk sınırları ve yapı (paragraf, "• " maddeleri) otomatik olarak kontrol edildi.
- **Kopyalananlar:** Ekran görüntüleri (İngilizce görsellerin adresleri), geliştirici adı, telif satırı ve uygulama adı
  her dile İngilizce sayfadan kopyalandı.
- **Çıktı:** `tmp/listings/import.csv` (git'e girmez). Hiçbir dilde gerekli alan boş değil.
- **Kalan:** Kullanıcı dosyayı `Import listings` ile yükleyip gönderimi yapacak.

Kontrol: uygulandı — kullanıcı `tmp/listings/import.csv`'yi Partner Center'a içe aktardı ve 1.1.0 gönderimini yaptı; Partner Center "Update in certification" gösteriyor (gönderim, 15 dilin Store sayfası "Complete" olmadan başlatılamıyor).
