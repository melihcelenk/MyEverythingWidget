# Faz 3 — MEW: aile üyelerini bulma, sağ tıkta dört yön, açma ve kenara yerleştirme

> **Durum:** ⏳ Bekliyor · **Tamamlanma:** 0% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

MEW'in kompakt simgesi hub olur. Yüklü aile üyelerini kendiliğinden bulur. Simgeye sağ tıklanınca dört yanında bu
üyeler görünür. Birine tıklanınca o widget açılır ve simgenin o kenarına yerleşir.

## Problem

- **Gereksinim (örnek kullanım):** MEW simgesine sağ tıklanınca dört yanında diğer widget uygulamaları açılabilir.
- **Mevcut durum:** Kompakt simgenin sağ tık menüsünde yalnız MEW'in kendi komutları var.

## Çözüm

- **Keşif:** Aile uzantısı kataloğu açılır; üye kurulunca ya da kaldırılınca liste güncellenir.
- **Menü:** Sağ tıkta simgenin dört yanında üyeler gösterilir. Her üye manifestinde önerdiği kenarı bildirir; o kenar
  doluysa saat yönünde sıradaki boş kenara geçer (S03 → A). Kullanıcı ayarı yok.
- **Açma ve yerleşme:** Protokolle açılır; üye çalışıyorsa mesaj kanalından konum gönderilir.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 3.1 | MEW yüklü aile üyelerini bulur ve kurulup kaldırılmalarını izler. | ⏳ Bekliyor (Faz 1) |
| 3.2 | Sağ tık menüsünün görsel taslağı gösterilir. | ⏳ Bekliyor (Faz 1) |
| 3.3 | Sağ tıkta üyeler simgenin dört yanında görünür. | ⏳ Bekliyor (3.2 onayı) |
| 3.4 | Tıklanan üye açılır ve simgenin o kenarına yerleşir. | ⏳ Bekliyor (Faz 2) |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Dört yönde kim nerede duracak? | A: widget önerir, doluysa sıradaki boş kenar | 🟢 Verildi (A) | S03 |

## Nasıl kontrol edilir

- [ ] Task Timer kuruluyken MEW simgesine sağ tıklanınca Task Timer bir yönde görünüyor.
- [ ] Ona tıklanınca Task Timer açılıp simgenin o kenarına yerleşiyor.
- [ ] Task Timer kaldırılınca o yön boşalıyor.

## Kalan

- **3.1–3.4:** Faz 1 ve Faz 2'yi bekliyor.

## Ayrıntılar

### 3.1 — MEW yüklü aile üyelerini bulur ve kurulup kaldırılmalarını izler.

- **Mevcut durum:** MEW başka uygulamalardan habersiz.
- **Problem:** Hub'ın üyeleri kod değişikliği olmadan tanıması gerekir.
- **Çözüm:** Infrastructure katmanında katalog servisi; Presentation'da üye listesi.
- **Dosyalar:** `src/MyEverythingWidget.Infrastructure`, `src/MyEverythingWidget.Presentation`
- **Testler:** Liste mantığı birim testi; Sandbox'ta iki paketle keşif.
- **Durum:** ⏳ Bekliyor.

### 3.2 — Sağ tık menüsünün görsel taslağı gösterilir.

- **Mevcut durum:** Yalnız `WIDGET_FAMILY.md`'de metin taslağı var.
- **Problem:** Tasarım değişikliği kodlanmadan önce görsel taslakla onaylanır.
- **Çözüm:** Taslak `mockups/` altında hazırlanır ve gösterilir.
- **Dosyalar:** `mockups/`
- **Testler:** —
- **Durum:** ⏳ Bekliyor.

### 3.3 — Sağ tıkta üyeler simgenin dört yanında görünür.

- **Mevcut durum:** Sağ tık menüsünde yalnız MEW komutları var.
- **Problem:** Gereksinimdeki dört yönlü açılış.
- **Çözüm:** Onaylanan taslağa göre kompakt simge menüsü. Kenar ataması Core'da: önerilen kenar, doluysa saat
  yönünde sıradaki boş kenar; aynı kenarı isteyenlerden önce kurulan kenarı alır (S03 → A).
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml(.cs)`
- **Testler:** Kenar ataması birim testleri (tek üye, aynı kenarı isteyen iki üye, dört kenar dolu); Sandbox UI testi.
- **Durum:** ⏳ Bekliyor.

### 3.4 — Tıklanan üye açılır ve simgenin o kenarına yerleşir.

- **Mevcut durum:** —
- **Problem:** Açılan widget hub'ın yanında durmalı; ekran kenarında içeri kaydırılmalı.
- **Çözüm:** Konum hesabı ortak kütüphanedeki `Placement.NextTo` (Faz 1.5); açma protokolle, konum kanal mesajıyla.
- **Dosyalar:** `src/MyEverythingWidget.Infrastructure`, `src/MyEverythingWidget.App`
- **Testler:** Konum hesabı birim testleri; Sandbox'ta iki paketle açma ve konum.
- **Durum:** ⏳ Bekliyor.

### Doğrulanmayan / dikkat edilmesi gereken

- Sandbox'a iki paketi birlikte kurmak için `scripts/test-ui.ps1` genişletilecek.

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 3
- `WIDGET_FAMILY.md` → 4. Yaklaşımlar → A
