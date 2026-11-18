---
id: S16
status: answered
decider: user
priority: major
asked: 2026-11-18
---
# S16 — About tasarımı: TaskTimerWidget'tan neyi birebir alalım?

**Mevcut durum:** About, Ayarlar penceresinin içinde bir bölüm; bağlantılar düz metin renginde, tek renk simgeli; sürüm ve yıl aynı satırda, altında gizlilik notu var.

**Soru:** About'u aşağıdaki maddelere göre nasıl yapayım?

## Bağlam

TaskTimerWidget'taki About ile şu anki hal arasındaki farklar:

| # | TaskTimerWidget | Şu anki hal |
|---|-----------------|-------------|
| 1 | Alttaki **"i" düğmesiyle açılan küçük bir açılır kart** (flyout); Ayarlar'dan ayrı | Ayarlar penceresinin içinde bir bölüm |
| 2 | Kartın kendi **renkli zemini** (yeşil) ve çerçevesi var | Ayarlar penceresinin zemini |
| 3 | Başlık kalın; altında **"Version 1.1.0.0"** ve **"2025"** ayrı satırlarda | "Version 1.0.0 · 2026" tek satırda |
| 4 | Ayırıcı çizgi, ardından **geliştirici adı** | Aynı |
| 5 | Bağlantılar **mavi** ve **renkli emoji simgeli**: ✉ e-posta, 🌐 Website, ⭐ Rate | Bağlantılar metin renginde, tek renk simgeli: e-posta, melihcelenk.com, GitHub |
| 6 | **Rate** (Store'da puan ver) bağlantısı var | Yok (uygulama henüz Store'da değil) |
| 7 | Gizlilik notu yok | Kısa gizlilik notu var |

## Seçenekler

### A — Birebir TaskTimerWidget gibi ⭐

- **Açılış:** Alttaki çubukta, ayarlar düğmesinin yanında bir "i" düğmesi olur ve About'u küçük bir açılır kart
  olarak açar. Ayarlar penceresinden About bölümü kalkar.
- **Kart içeriği, sırasıyla:**
  - Kalın başlık.
  - "Version 1.0.0" ve "2026" ayrı satırlarda.
  - Ayırıcı çizgi.
  - "Melih Çelenk".
  - Mavi ve emoji simgeli bağlantılar: ✉ e-posta (tıklayınca kopyalanır ve "Copied" görünür), 🌐 melihcelenk.com,
    ⭐ Rate.
- **Rate bağlantısı:** Store kimliği belli olunca eklenir; o zamana kadar gizli kalır.
- **Gizlilik notu ve GitHub bağlantısı:** Karttan çıkar. İstersen GitHub "</> Source code" olarak kalabilir.
- **Kartın zemini:** TaskTimerWidget'taki yeşil sabit bir renk. Bu projede kural "renkler yalnız tema
  kaynaklarından" olduğu için temanın vurgu renginin açık tonunu kullanırım; açık ve koyu temada otomatik uyum sağlar.
  Sabit yeşil istersen cevaba yaz.

### B — Ayarlar içinde kalsın, yalnız görünüm TaskTimerWidget gibi olsun

- Yer değişmez; 3, 5 ve 6 numaralı farklar uygulanır (ayrı satırlar, mavi ve emoji simgeli bağlantılar, Rate).

## Öneri

**A** — "TaskTimerWidget'taki gibi" isteğinin en doğrudan karşılığı bu. Cevaba özellikle şunları yaz:

- "i" düğmesinin yeri alttaki çubuk mu olsun?
- Kartın zemini vurgu renginin açık tonu mu, sabit yeşil mi?
- GitHub bağlantısı ve gizlilik notu kalsın mı?

Onayından sonra önce bir taslak görsel hazırlarım; kodlamaya taslak onaylanınca geçerim.

## Cevap

i düğmesi istemiyorum. 
O kısım aynı yeşil ama settings içinde daha küçük bir kart şeklinde
Yazı boyutları task timer widget ile aynı olmalı, seninkiler büyük
versiyon ve 2026 ayrı satırlar
emojiler aynı olmalı. isimler aynı olmalı. Rate vs onların hepsi aynı, website de task için web sitesi oluştur repoda, oranın linkini koy
rate için geçici olarak https://apps.microsoft.com/search/publisher?name=Melih%20Celenk bunu koyabilirsin.

## Sonuç
