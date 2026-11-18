---
id: S8
status: resolved
decider: user
priority: major
asked: 2026-11-18
resolved: 2026-11-18
---
# S8 — GitHub ve Store ekran görüntüleri: hangi senaryolar, nasıl çekilsin?

**Mevcut durum:** README'de hiç ekran görüntüsü yok; Store için yalnız UI testlerinin rastgele verili görüntüleri var.

**Soru:** Düzeltilmiş 5 senaryo uygun mu, ve görüntüleri hangi yolla çekeyim (A, B ya da C)?

## Bağlam

Gereksinim: Görüntülerde en kullanışlı kullanım senaryoları gösterilmeli; kullanıcı her görüntüde widget'ı hangi
amaçla kullanabileceğini görebilmeli. Rastgele resim ve not olmayacak. Her görüntü tek bir kullanım amacını anlatmalı ve altına bir satır açıklama yazılmalı.

### İlk taslağa gelen düzeltmeler

- **Notlar:** "Standup 09:30" gibi rutin kayıtlar takvimde zaten görünür; widget'ın amacı bu değil. Notlar **sık
  kullanılan** metinler ve **aceleyle alınan** notlar olmalı.
- **Komut:** `git pull --rebase` klavyeden kolayca yazılır; notta durmasının bir faydası görünmez. Uzun, ezberlenmeyen
  bir komut gerçekten işe yaradığını gösterir.
- **Resimler:** Klavye kısayolları tablosu çok yazılı ve kafa karıştırıcı. Resim kartı yazı değil görsel olmalı. Asıl
  kullanım: **anlık ekran almak gereken durumlar**, örneğin bir hata ekranı; o anda başka bir yere konamayan görüntü
  buraya konur.

### Önerilen senaryolar (5 görüntü, sıralı), düzeltmelere göre

| # | Başlık (README / Store) | Ne görünüyor |
|---|--------------------------|--------------|
| 1 | **Your daily launcher** | "Work" sekmesi: Edge, Terminal, proje klasörü, sık açılan iki web sitesi (ör. bir iş takip ve bir dokümantasyon sitesi). Not yok; yalnız tek tıkla açılan uygulama, klasör ve siteler. |
| 2 | **Text you copy again and again** | Sarı notlar, sık kullanılan ve yazması uzun metinler: tek satıra sığmayan bir komut (ör. `docker run --rm -it -v "${PWD}:/app" -w /app mcr.microsoft.com/dotnet/sdk:10.0 dotnet test --filter Category=Smoke`), e-posta imzası, sık verilen kargo/fatura adresi (örnek adres). Bir notun kopyalama düğmesi "Copied" durumunda. |
| 3 | **Jot it down before it's gone** | Aceleyle alınmış kısa notlar: telefonda söylenen bir sipariş/takip numarası, "Ali'yi geri ara — fatura farkı 240 TL", bir toplantıda geçen bağlantı. Ctrl+V ile panodaki metnin nota dönüştüğü an. |
| 4 | **Grab a screen the moment you see it** | Bir hata ekranının (ör. örnek bir uygulamanın "Something went wrong" penceresi, hata kodu görünür) ekran görüntüsü Ctrl+V ile resim kartı olmuş; büyük görüntüleyicide açık, sağ tık menüsünde "Copy" ve "Edit in Paint". Yanında küçük bir ikinci görüntü kartı (ör. bir grafik ya da tasarım taslağı). |
| 5 | **Out of the way when you don't need it** | Masaüstünde 1x1 compact ikon (her zaman üstte) ve yanında açılmış hali; koyu tema. Sekmeler (Work · Personal) bu görüntüde görünür. |

Hata ekranı ve görseller benim tarafımdan üretilir (kurmaca bir uygulama adıyla); gerçek bir ürünün, kişinin ya da
şirketin bilgisi içermez. Store en az 1, en çok 10 görüntü alıyor; 1366x768 ya da üstü önerilir.

## Seçenekler

### A — Sandbox'ta otomatik çek ⭐

- Yukarıdaki veri bir tohum dosyasıyla (`MEW_DATA_DIR`) hazırlanır, `scripts/capture-screenshots.ps1` Sandbox'ta
  uygulamayı açıp her senaryoyu çeker ve `docs/images/` altına koyar.
- Artısı: tekrar üretilebilir; her sürümde aynı komutla yenilenir; senin masaüstüne ve verine dokunulmaz.
- Eksisi: Sandbox'ta yalnız Windows'un kendi uygulamaları var (Edge, Terminal, Notepad, Paint, Explorer). VS Code,
  Outlook, Spotify gibi uygulamalar görünmez; yerlerine Windows uygulamaları ve web siteleri konur.

### B — Senin bilgisayarında, hazır veriyle

- Aynı veriyi bir klasöre hazırlarım; sen `MEW_DATA_DIR` ile o klasörü gösteren bir kısayolla uygulamayı açıp
  görüntüleri kendin çekersin (Win+Shift+S).
- Artısı: gerçek uygulama ikonları (VS Code, Spotify…) ve gerçek masaüstü arka planı.
- Eksisi: elle çekim; her sürümde tekrar senin işin.

### C — İkisi birden

- README ve Store taslağı A ile otomatik çekilir; Store'a gidecek son görüntüleri istersen B ile kendi masaüstünde
  yenilersin.

## Öneri

**C**, A'dan başlayarak: önce Sandbox'ta otomatik çekip README'yi bitireyim, görüntüleri gör; gerçek uygulama
ikonlarını istersen aynı veriyle kendi makinende çekersin. Senaryolarda değiştirmek istediğin metin (komut, not, hata
ekranı) varsa cevaba yaz.

## Cevap

**A — Sandbox'ta otomatik çek**

## Sonuç

A uygulandı: görüntüler Sandbox'ta otomatik çekiliyor.

- **Komut:** `pwsh scripts/capture-screenshots.ps1` (~3 dk). `ShowcaseScreenshots` 5 senaryoyu kurup çekiyor, script
  her birini 1366x768'lik başlıklı sayfaya yerleştirip `docs/images/showcase-1.png` … `showcase-5.png` olarak yazıyor.
- **Senaryolar:** Düzeltilmiş tablodaki gibi.
  - Notlar sık kopyalanan ve aceleyle alınan metinler.
  - Uzun komut `docker run … dotnet test --filter …`.
  - Resim kartında uydurma "Ledgerly" uygulamasının hata ekranı ve bir grafik var.
- **Görünüm:**
  - Uygulama kartlarında gerçek kabuk ikonları var.
  - Web kartlarında emoji var (Sandbox'ta ağ yok).
  - Masaüstü düz renk: duvar kâğıdı ve görev çubuğu görünmüyor.
- **Nerede kullanılıyor:** README ("What you can use it for") ve `docs/general/STORE_LISTING.md` bu dosyaları
  kullanıyor.
- **Ayrıntı:** `PHASE17.md` → 17.2.

Kontrol: uygulandı — Sandbox çekimi `ShowcaseScreenshots.cs` + `scripts/capture-screenshots.ps1` ile yapılıyor, çekimler `docs/images/captures/` altında; README bunlardan üretilen `store-1..3.png`'yi kullanıyor (S10 ile üçe indi).
