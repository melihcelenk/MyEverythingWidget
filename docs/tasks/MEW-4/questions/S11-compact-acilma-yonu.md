---
id: S11
status: resolved
decider: user
priority: major
asked: 2026-11-18
resolved: 2026-11-18
---
# S11 — Compact ikon ekranın sağındayken widget hangi yöne açılsın?

**Mevcut durum:** Widget, ikonun sol üst köşesinden sağa doğru açılıyor; ekrana sığmazsa sola itiliyor. Küçültünce ikon widget'ın sol üst köşesine gidiyor, yani ilk yerinden sola kaymış oluyor.

**Soru:** Düzeltmeyi yalnız yatayda mı (A), yoksa dikeyde de mi (B) yapayım?

## Bağlam

- **Neden:** `MainWindow.ApplyLayoutMode` hem açarken hem küçültürken pencerenin sol üst köşesini sabit tutuyor.
  - **Açarken:** Widget ikonun sol üst köşesinden sağa doğru açılıyor. Ekrandan taşınca `WindowPlacement.FitInside`
    onu sola itiyor; widget ekranın sağ kenarına yapışıyor, ikonun sağ kenarıyla hizalanmıyor.
  - **Küçültürken:** İkon, sola itilmiş widget'ın sol üst köşesine konuyor. Böylece ilk yerinden sola kaymış oluyor.
- **İstenen:** Ekranın sağındaki ikona tıklayınca widget'ın sağ kenarı ikonun sağ kenarına denk gelsin. Küçültünce
  ikon eski yerine dönsün.

## Seçenekler

### A — Yalnız yatay

- İkon ekranın sağ yarısındaysa widget sola doğru açılır: sağ kenarları hizalı.
- Sol yarıdaysa bugünkü gibi sağa doğru açılır.
- Küçültünce ikon, widget'ın açıldığı köşeye döner; açıp kapatınca ikonun yeri değişmez.

### B — Yatay ve dikey ⭐

- A'daki kural dikeyde de uygulanır. İkon ekranın alt yarısındaysa widget yukarı doğru açılır: alt kenarları
  hizalı.
- Böylece ikon hangi köşedeyse widget o köşeden açılır ve küçültünce ikon aynı yere döner.
- Örnek: sağ alttaki ikon widget'ın sağ alt köşesi olur.

## Öneri

**B** — sağ alt köşe, ikonun en çok konduğu yerlerden biri. Yalnız yatay düzeltmede widget orada aşağı taşar ve
yukarı itilir; küçültünce ikon yine kayar.

- **Test:** Önce saf mantık için unit testler yazılır (ikonun bulunduğu çeyreğe göre widget nereye açılır,
  küçültünce ikon nereye döner). Ardından Sandbox'ta bir UI testi (ikon sağ üstteyken aç-kapat, ikon yerinde
  kalmalı). Yalnız ilgili testler çalışır (~2–3 dk).

## Cevap

**B — Yatay ve dikey**

## Sonuç

B uygulandı (yatay ve dikey).

- **Açılış:** Widget ikonun ekran köşesine en yakın köşesinden açılıyor. Sağ üstteki ikonda sağ ve üst kenarlar,
  sağ alttakinde sağ ve alt kenarlar hizalı.
- **Küçültme:** İkon aynı köşeye, yani tam eski yerine dönüyor. Widget arada taşındıysa ikon, widget'ın ekran köşesine
  en yakın köşesine gidiyor.
- **Değişen davranış:** Widget ilk kez küçültüldüğünde ikon artık widget'ın sağ üst köşesinde çıkıyor (önceden sol
  üst). Bu beklentiyi ölçen eski UI testi de buna göre güncellendi.
- **Testler:**
  - Core: `CompactCornerTests`; Core testleri 203/203.
  - UI: `CompactAndMenuTests` 8/8 (sağ üst ve sağ altta aç-kapat dahil), `WindowLayoutTests` 12/12.
  - Tam UI seti çalıştırılmadı.
- **Ayrıntı:** `PHASE17.md` → 17.7.

Kontrol: uygulandı — `MainWindow.ApplyLayoutMode` `WindowPlacement.NearestCorner/AlignCorner` kullanıyor; `CompactCornerTests` (Core) ve `CompactAndMenuTests.IconOnTheRight_OpensWithTheRightEdgesLinedUp_AndShrinksBackToTheSamePlace` (sağ üst ve sağ alt) geçiyor.
