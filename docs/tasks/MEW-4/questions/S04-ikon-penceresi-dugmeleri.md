---
id: S4
status: resolved
decider:
priority: major
asked: 2026-10-30
resolved: 2026-11-17
---
# S4 — İkon penceresindeki "Image…" ve "Reset" düğmeleri nerede dursun?

**Mevcut durum:** Özellik geri gitmedi; düğmeler emoji ızgarasının altında duruyordu ve widget küçükken pencere kesildiği için görünmüyorlardı.

**Soru:** Düğmeleri pencerenin alt çubuğuna (Cancel'ın yanına) taşıdığım değişikliği tutayım mı, yoksa başka bir düzen mi istersin?

## Bağlam

- **Ne oldu:**
  - Ekrandaki uygulama son sürüm (12:35 derlemesi, `9114b4c`).
  - "Change icon…" penceresinde emoji ızgarası, "Image…" ve "Reset to original" aynı ekranda; Faz 10'da konuştuğumuz
    tasarım bu.
  - İki düğme ızgaranın **altında** duruyordu. Pencere widget'tan büyük olamadığı için küçük widget'ta ızgaranın alt
    satırları ve iki düğme kesiliyordu. Senin ekran görüntündeki durum bu.
- **Testler neden yakalamadı:** Testler düğmeye UI Automation ile basıyordu, ekranda görünüp görünmediğine bakmıyordu.
- **Ne yaptım:**
  - Sana sormadan bir düzeltme yazdım; commit'lenmedi, push'lanmadı.
  - Düğmeleri pencerenin alt çubuğuna taşıdım: `Image…` · `Reset to original` · `Cancel`. Bu çubuk her zaman görünür.
  - Emoji ızgarasını, sığmazsa kaydırılabilir yaptım.
  - En küçük (2x2) widget'ta iki düğmenin ekranda olduğunu ve gerçek tıklamayla Reset'in çalıştığını ölçen bir test
    ekledim.
  - Bu testlerin hepsi geçti (7/7); tam UI suite koşuyor.

## Seçenekler

### A — Değişikliği tut: düğmeler alt çubukta, Cancel'ın yanında ⭐

- ✅ Widget ne kadar küçük olursa olsun üç seçenek de görünür.
- ✅ Windows'un standart diyalog düzeni.
- ❌ Alt çubukta üç düğme yan yana olur; dar pencerede yazılar kısalabilir.

### B — Düğmeler emoji ızgarasının üstünde, ızgara kaydırılır

- ✅ Seçenekler ilk bakışta en üstte görünür.
- ❌ Cancel ayrı bir yerde (altta) kalır.

### C — Değişikliği geri al

- Kod, push'lu son hâline (`9114b4c`) döner.

## Öneri

A. Üç seçenek her boyutta görünür kalıyor ve test bunu en küçük pencerede doğruluyor.

## Cevap

## Sonuç

Kullanıcı kartı cevaplamadan yeni bir tasarım tarif etti: iki sekme ("Select icon" / "Select image"), Reset Cancel'ın
solunda, resim tarafında gözat + sürükle-bırak + Ctrl+V. Bu kartın seçenekleri o tasarımla geçersiz kaldı; plan
onayı `S05-ikon-penceresi-sekmeler.md` kartında soruluyor. Commit'lenmemiş düzeltme onay gelene kadar bekliyor.
