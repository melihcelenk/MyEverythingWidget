---
id: S10
status: resolved
decider:
priority: major
asked: 2026-11-18
resolved: 2026-11-20
---
# S10 — Üç tanıtım görselinin taslağı (6. tur): bu haliyle çekeyim mi?

**Mevcut durum:** Taslaklar geri bildirime göre yenilendi (`mockups/mock-1-everything.png`, `mock-2-copy.png`, `mock-3-compact.png`); çekim yapılmadı.

**Soru:** Yeni taslakları onaylıyor musun, yoksa neyi değiştireyim?

## Bağlam

### 6. turda değişenler

- **3. görsel:** Compact ikon sağ üstte duruyor. İkondan widget'ın sağ üst köşesine sol aşağı inen bir ok var;
  okun üstünde "Click to expand" yazıyor. Widget o ikondan açılmış gibi görünüyor. Eski "One click opens it"
  etiketi kaldırıldı.

### 5. turda değişenler

- **Görev çubuğu:** Üç görselin altına Windows 11 tarzı bir görev çubuğu eklendi: Başlat düğmesi, arama kutusu,
  sabitlenmiş Edge, Explorer ve Downloads ikonları, sağda saat. Böylece widget'ın masaüstünde durduğu anlaşılıyor.
  3. görselde görev çubuğu koyu temada.
- **Gerçek çekimde:** Sandbox'ın kendi görev çubuğu Türkçe ve kalabalık olduğu için kullanılmayacak; çubuğu
  `scripts/capture-screenshots.ps1` aynı şekilde çizecek.

### 4. turda değişenler

- **2. görsel Ctrl+V'ye odaklandı.** Başlık: **"Copy it. Ctrl+V. Saved in a second."** (ikinci cümle vurgu
  renginde). Altında büyük Ctrl + V tuşları ve "Picture · Text · Link" simgeleri var.
- **Web sitesi de Ctrl+V ile:** Uygulamada tek satırlık bir adres yapıştırılınca web sitesi kartı oluyor (koddan
  doğrulandı). Ctrl+V ile eklenmiş üç kart (fotoğraf, not, imdb.com) mavi çerçeve ve "Ctrl+V" rozetiyle
  işaretlendi; yanlarında "Picture", "Text", "Link" etiketleri var.
- **Sağ tık menüsü** alttaki fotoğrafta tam haliyle duruyor; etiketi "Right-click".
- **Alt yazı:** "A picture, some text or a web link: copy it, press Ctrl+V on the widget and it is there. Right-click
  a picture to copy it again or edit it in Paint."

### 3. turda değişenler

- **Sağ tık menüsü 2. görsele taşındı** ve uygulamadaki gerçek haliyle tam gösteriliyor: Copy image, Edit in
  Paint, Move to, Delete. 1. görselde menü yok.
- **2. görsel yalnız not değil:** Bir not (imza, "Copied" işaretli), iki fotoğraf ve üç uygulama/site (Edge,
  Calculator, Explorer, imdb.com) var.
- **Ctrl+V ile resim:** Üstteki fotoğrafın yanında "Pictures paste with Ctrl+V too" etiketi var.
- **2. görselin başlığı:** **Paste it, keep it, use it again** — "Press Ctrl+V to keep any text or picture on your
  desktop. Copy it back with one click, or open a picture in Paint to edit it."

### 2. turda değişenler

- **Metinler:** Hepsi olumlu ve davet eden cümleler oldu; olumsuz yapı ("don't", "out of the way") kalmadı.
- **Web siteleri:** Herkesin tanıdığı, uygulama olmayan siteler kendi ikonlarıyla: imdb.com, wikipedia.org,
  booking.com, weather.com, nytimes.com. Kart adı alan adı olduğu için web sitesi olduğu ilk bakışta anlaşılıyor.
- **Uygulamalar:** Yazılımcıya özgü olanlar (PowerShell, Cmd, Issues…) çıktı: Edge, Explorer, Calculator,
  Downloads, Documents.
- **Notlar:** Herkesin kullandığı türden: imza, ev adresi, IBAN, hazır cevap, geri arama notu.

### Taslaklar

| # | Taslak | Başlık | Alt yazı |
|---|--------|--------|----------|
| 1 | `mockups/mock-1-everything.png` | **Everything you love, one click away** | Your apps, favourite websites, notes and photos, together on your desktop. |
| 2 | `mockups/mock-2-copy.png` | **Copy it. Ctrl+V. Saved in a second.** | A picture, some text or a web link: copy it, press Ctrl+V on the widget and it is there. Right-click a picture to copy it again or edit it in Paint. |
| 3 | `mockups/mock-3-compact.png` | **Always at hand, always on top** | Tuck the widget into a small icon on your desktop and open everything with one click. Sağ üstte compact ikon, ondan widget'a "Click to expand" oku. |

### Gerçek çekimde farklı olacaklar

- **Site ikonları:** Uygulama site ikonlarını internetten alır. Bunun için yalnız bu çekimde Sandbox'ın ağını açmam
  gerekiyor (UI testlerinde ağ kapalı kalır).
- **Sekme adları:** Taslakta "Work · Snippets · Inbox · Screens". Çekimde "Home · Work · Personal" gibi herkese uyan
  adlar kullanırım.

## Seçenekler

### A — Bu taslaklarla çek ⭐

- Üç görsel Sandbox'ta (yalnız bu çekim için ağ açık) gerçek uygulamayla çekilir; başlıklar ve mavi etiketler script
  ile eklenir; README ve Store listesi üç görsele göre güncellenir.

### B — Değişiklik yap, yeni taslak göster

- Cevaba neyi değiştireceğimi yaz; yalnız taslağı yenilerim, çekim yapmam.

## Öneri

**A** — 1. görsel dört kart türünü etiketleriyle tek bakışta gösteriyor; 2. görsel Ctrl+V, tek tıkla kopyalama ve
resmin menüsünü (Paint dahil) birlikte gösteriyor; metinlerin hepsi olumlu.

## Cevap

## Sonuç

Kullanıcı taslakları terminalde onayladı ve değişikliklerin commit'lenip push'lanmasını istedi. Sandbox'ta yeniden çekip çekmemeyi bana bıraktı.

- **Karar:** Taslaklar son görseller olarak kullanılıyor.
  - **Neden:** Kartlar, ikonlar ve pencereler zaten gerçek Sandbox çekimlerinden alındı. Yeniden çekim yalnız site
    ikonları için Sandbox'ın ağını açmayı gerektirir ve görsel farkı çok küçük olurdu.
- **Üretim:**
  - `scripts/compose-store-images.py` görselleri `docs/images/captures/` ve `docs/images/assets/` dosyalarından
    üretiyor; çıktısı taslaklarla piksel piksel aynı.
  - `docs/images/store-1.png` … `store-3.png` README ve Store listesinde kullanılıyor.
- **Ayrıntı:** `PHASE17.md` → 17.6.
