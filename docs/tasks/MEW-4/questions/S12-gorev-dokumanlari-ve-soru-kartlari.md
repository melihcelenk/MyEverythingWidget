---
id: S12
status: resolved
decider: user
priority: major
asked: 2026-11-18
resolved: 2026-11-18
---
# S12 — Repo halka açılırken görev dokümanları ve soru kartları ne olsun?

**Mevcut durum:** `docs/tasks/` altındaki faz dokümanlarında ve soru kartlarında kullanıcı mesajları birebir, gündelik dille alıntılanmış; S08–S11 henüz commit'lenmedi.

**Soru:** Görev dokümanlarını ve soru kartlarını halka açık repoda nasıl tutalım?

## Bağlam

### Ne buldum

- **Birebir alıntılar:** Faz dokümanlarının çoğunda "İstekler (birebir)" bölümü ve Problem satırlarında mesajlar
  olduğu gibi duruyor. Örnekler:
  - `PHASE10.md`: Windows emoji paneline (Win+.) yönlendirmeyi reddeden, gündelik dilde bir alıntı.
  - `PHASE14.md`: içeriğin yaklaşık yarım saniye sonra geldiğini bildiren, gündelik dilde bir alıntı.
  - En çok alıntı: `PHASE10.md` (14 satır), `PHASE9.md` (8), `MAIN_TODO.md` (6), `PHASE11.md`, `PHASE13.md`.
- **Soru kartları:** Bağlam bölümlerinde ve Sonuç'ta kısa alıntılar var (ör. S08'de rutin kayıtların takvimde
  görüneceğini belirten not düzeltmesi, S10'da taslak onayını ve commit/push talebini bildiren mesaj). Cevap bölümü çoğunlukla yalnız seçenek harfi.
- **Gizli bilgi:** Yok. Şifre, anahtar, şirket iş numarası (HA-…), iç adres ya da kişisel dosya yolu ne dosyalarda
  ne git geçmişinde bulunmadı.
- **Kural zaten var:** Genel kuralın (USER_REQUIREMENTS_TRACKING) "Konuşma dili ve birebir alıntı repoya yazılmaz;
  asıl söz talimat defterinde durur" diyor. Eski faz dokümanları bu kuraldan önce yazıldığı için alıntı içeriyor.
  Talimat defteri (`TALIMATLAR.md`) zaten git'e girmiyor.

### Kararların geçmişi neden değerli

Soru kartları "neden böyle yapıldı" sorusunun cevabı: seçenekler, öneri, verilen karar ve uygulanan sonuç. Bu,
açık kaynak bir projede katkı verecek biri için de değerli. Sorun içerik değil, dil.

## Seçenekler

### A — Repoda kalsın, dil resmîleştirilsin ⭐

- **Faz dokümanları:**
  - Birebir alıntılar resmî gereksinim cümlelerine çevrilir: `Gereksinim (T29): …`. Anlam ve kapsam aynen kalır.
  - "İstekler (birebir)" bölümleri "Gereksinimler" olur.
- **Soru kartları (S01–S11):**
  - Bağlam ve Sonuç'taki alıntılar aynı şekilde yazılır.
  - Cevap bölümü yalnız seçilen seçeneği ve varsa resmî bir notu taşır.
  - Temizlikten sonra S08–S11 commit'lenir.
- **Bundan sonrası:** Kartlar baştan bu dille yazılır; asıl söz yalnız talimat defterinde kalır.
- **Artısı:** Karar geçmişi korunur; repo dışarıya düzgün görünür; mevcut kurala uyulur.
- **Eksisi:** Bir kerelik temizlik işi (17 faz dokümanı, 11 kart). Git geçmişindeki eski haller kalır; onları da
  silmek geçmişi yeniden yazmayı (force push) gerektirir. Bunu önermiyorum.

### B — Görev dokümanları halka açık repodan çıksın

- `docs/tasks/` repodan kaldırılır ve `.gitignore`'a girer (ya da ayrı, gizli bir repoda tutulur). Açık repoda
  yalnız `docs/general/` kalır.
- **Artısı:** En az iş; dışarıya hiç süreç dokümanı görünmez.
- **Eksisi:** Karar geçmişi açık repodan kaybolur; eski haller git geçmişinde yine durur.

### C — Olduğu gibi kalsın

- Kartlar her zamanki gibi push'lanır; temizlik yapılmaz.

## Öneri

**A** — karar geçmişini tutma isteğinle ve zaten var olan "birebir alıntı repoya yazılmaz" kuralıyla uyumlu.
Git geçmişini yeniden yazmayı önermiyorum: eski hallerde gizli bilgi yok, yalnız gündelik dil var.

## Cevap

**A — Repoda kalsın, dil resmîleştirilsin**

## Sonuç

A uygulandı: görev dokümanları ve soru kartları repoda kalıyor, dilleri resmîleştirildi.

- **Faz dokümanları:** Birebir alıntılar `Gereksinim: …` cümlelerine çevrildi; anlam ve kapsam korundu.
  - En çok değişenler: `PHASE9.md` (12 alıntı), `PHASE10.md` (17), `PHASE11.md` (10), `MAIN_TODO.md` (3).
  - "İstekler (birebir)" başlıkları "Gereksinimler" oldu.
  - `PHASE1.md`–`PHASE8.md`, `PHASE15.md` ve `PHASE16.md`'de alıntı yoktu.
- **Eski task dokümanları:** `MEW-1/TODO.md` ve `MEW-3/TODO.md`'deki alıntılar da çevrildi.
- **Soru kartları:** S02, S03, S05–S10 ve S12'deki alıntılar resmî ifadeye çevrildi. Başlık alanları (status,
  decider) değişmedi.
  - S09'daki not metninde şirket iş numaraları vardı; o satır yalnız "dört satırdan oluşuyor" diye yazıldı.
  - S09 hiç commit'lenmediği için git geçmişinde de şirket iş numarası yok (taramayla doğrulandı).
- **Kontrol:**
  - Bütün görev dokümanlarında gündelik dil taraması yapıldı.
  - Kalan "birebir" sözcükleri kuralın ve sorunun adı, kullanıcı sözü değil.
  - Faz dokümanlarının hepsi şablon denetiminden geçiyor.
- **Commit:** Kartlar (S08–S14) temizlikten sonra commit'lendi.
- **Bundan sonrası:** Kartlar baştan resmî dille yazılacak; asıl söz yalnız talimat defterinde kalacak.
- **Ayrıntı:** `PHASE17.md` → 17.8.

Kontrol: uygulandı — `docs/tasks` altında "İstekler (birebir)" başlığı ve gündelik dil ifadesi kalmadı (yalnız bu kartın kendi açıklaması); 17 soru kartı git'te izleniyor.
