---
id: S5
status: resolved
decider: user
priority: major
asked: 2026-10-30
resolved: 2026-11-18
---
# S5 — İkon penceresi: iki sekmeli düzen doğru anlaşıldı mı?

**Mevcut durum:** Tarif ettiğin iki sekmeli ikon penceresini aşağıdaki gibi anladım; koda henüz başlamadım.

**Soru:** Bu plana göre yapayım mı?

## Bağlam

- Gereksinim: "Change icon" başlığının yerine "Select icon" adlı bir sekme, yanına da "Select image" adlı ikinci bir
  sekme gelmeli; sekmeler arasında geçiş yapılabilmeli. "Reset to original" düğmesi "Cancel" düğmesinin soluna
  alınmalı. Resim seçme sekmesinde dosyaya gözatmanın yanı sıra resmi sürükleyip bırakma ve Ctrl+V ile doğrudan
  yapıştırma da desteklenmeli.
- Bu istek S4'ün yerine geçiyor. S4'te sorduğum, düğmeleri alt çubuğa taşıyan düzeltme commit'lenmemişti. Bu plan
  onaylanırsa o düzeltme bu tasarımla değiştirilir.

## Plan

```
┌──────────────────────────────────────┐
│ [ Select icon ] [ Select image ]     │  ← başlık yerine iki sekme
│ ──────────────────────────────────── │
│  Select icon sekmesi:                │
│   😀 🚀 📁 …  emoji ızgarası         │  ← sığmazsa kaydırılır; tıklayınca uygulanır, pencere kapanır
│                                      │
│  Select image sekmesi:               │
│   ┌ - - - - - - - - - - - - - - - ┐  │
│     Drop an image here            │  │  ← resim sürükle-bırak
│   │ or paste it with Ctrl+V       │  │  ← Ctrl+V ile panodaki resim
│     [ Browse… ]                   │  │  ← dosya seçici
│   └ - - - - - - - - - - - - - - - ┘  │
│ ──────────────────────────────────── │
│          [ Reset to original ] [Cancel] │  ← alt çubuk, her zaman görünür
└──────────────────────────────────────┘
```

- **Sekmeler:** pencere başlığı ("Change icon") kaldırılıp yerine "Select icon" ve "Select image" sekmeleri gelir.
  Pencere "Select icon" sekmesiyle açılır.
- **Select icon:** bugünkü emoji ızgarası. Pencere küçükse ızgara kaydırılır; sekme başlıkları ve alt çubuk kesilmez.
- **Select image:**
  - Üç yol: resim dosyasını alana sürükleyip bırakmak, panodaki resmi Ctrl+V ile yapıştırmak ya da "Browse…" ile
    dosya seçmek.
  - Bırakılan dosya yolu ya da panodaki bir resim dosyası (Explorer'da kopyalanmış) da kabul edilir.
  - Resim gelince ikon olarak uygulanır ve pencere kapanır. Resim olmayan bir şey bırakılırsa alanda kısa bir uyarı
    çıkar.
- **Alt çubuk:** `Reset to original` · `Cancel`; Reset, Cancel'ın solunda.
- **Kart menüsü:** menüdeki öğenin adı "Change icon…" olarak kalır; değiştirilecek olan yalnız pencerenin içi.
- **Testler:**
  - En küçük (2x2) widget'ta iki sekme başlığının ve iki alt düğmenin ekranda olduğu.
  - Sekmeler arası geçiş.
  - Emoji seçimi.
  - Ctrl+V ile resim yapıştırma.
  - Resim dosyası bırakma (yol üzerinden; Explorer'dan gerçek sürükleme Sandbox'ta zaten test edilemiyor).
  - Reset.

## Seçenekler

### A — Plandaki gibi yap ⭐

### B — Değişiklikle yap

- Neyi farklı istediğini Cevap'a yaz (ör. kart menüsündeki adın da değişmesi, pencerenin "Select image" sekmesiyle
  açılması).

## Öneri

A.

## Cevap

**A — Plandaki gibi yap**

## Sonuç

A uygulandı (2026-10-30), commit `ba90b16`, push'lu; PR #1 güncellendi.

- **Sekmeler:** Pencere başlığı yerine "Select icon" ve "Select image" sekmeleri var. Pencere "Select icon" ile
  açılıyor.
- **Select icon:** emoji ızgarası; sığmazsa kaydırılıyor.
- **Select image:**
  - Bırakma alanı, "Browse…" düğmesi ve Ctrl+V. Resim ya da resim dosyası gelince ikon yapılıyor ve pencere kapanıyor.
  - Resim olmayan bir şey gelirse alanda "That is not an image." yazıyor.
- **Alt çubuk:** `Reset to original` · `Cancel`; en küçük (2x2) widget'ta da görünüyor.
- **Ctrl+V çakışması:** İkon penceresi açıkken ana pencerenin Ctrl+V'si devre dışı; yapıştırılan resim ızgaraya kart
  olarak eklenmiyor.
- **Testler:** 5 yeni/güncellenen UI testi; tam UI suite 71/71 + 1, unit 293/293.
- **Kalanlar:**
  - Explorer'dan gerçek sürükle-bırak Sandbox'ta otomatik test edilemiyor; aynı kod yolu Ctrl+V ile yapıştırılan
    dosyayla test edildi.
  - Sonar bu turda çalıştırılamadı (IDE dosyaları tanımıyordu).
- **Ayrıntı:** `PHASE13.md`.

Kontrol: uygulandı — `IconPickerDialog.cs` (`SelectIconTab`/`SelectImageTab`, `BrowseImageButton`, `ImageDropArea`, Ctrl+V, `Reset to original` + `Cancel`), `WindowLayoutTests` 4 testi, commit `ba90b16`.
