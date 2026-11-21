---
id: S21
status: resolved
decider: user
priority: major
asked: 2026-11-21
resolved: 2026-11-21
---
# S21 — Windows açılınca başlatma 1.0.2'ye girsin mi, nasıl?

**Mevcut durum:** Uygulama Windows açılınca kendiliğinden başlamıyor; 1.0.2 için dil, Ayarlar ve küçük simge değişiklikleri hazır (PR #7).
**Soru:** "Windows açılınca başlat" 1.0.2'ye eklensin mi; eklenirse varsayılanı ne olsun?

## Bağlam

- **Neden önemli:** Bir widget en çok bilgisayar açıldığında hazır beklediğinde işe yarıyor. Şu an kullanıcı uygulamayı
  her açılışta Başlat menüsünden açmak zorunda.
- **Nasıl yapılır:** Store uygulamaları bunu paket manifestindeki "startup task" ile yapıyor (`windows.startupTask`).
  - Windows bu görevi Ayarlar → Uygulamalar → Başlangıç listesinde gösteriyor; kullanıcı oradan da kapatabiliyor.
  - Uygulama görevi açmak için Windows'tan izin istiyor (`StartupTask.RequestEnableAsync`). İlk istekte Windows
    kullanıcıya bir onay penceresi gösteriyor.
  - Kullanıcı Windows Ayarları'ndan kapattıysa uygulama bunu kendi kendine yeniden açamıyor; Ayarlar'daki anahtar o
    durumda "Windows Ayarları'ndan açın" der.
- **Ayarlar'daki yer:** "Her zaman üstte" satırının altına bir anahtar daha: "Windows açılınca başlat". Pencere yine
  sığar.
- **Maliyet:** Yaklaşık yarım gün.
  - Manifest, anahtar ve 15 dilde metin.
  - Paketli uygulama testi (Sandbox'ta MSIX kurulu hâliyle).
  - Not: Geliştirme sürümü (paketsiz) bu özelliği kullanamıyor; anahtar orada gizlenir.
- **Kapsam dışı:** Başlangıçta widget'ın açık mı yoksa küçük simge olarak mı geleceği. Uygulama nasıl kapatıldıysa öyle
  açılıyor; bu değişmiyor.

## Seçenekler

### A — 1.0.2'ye girsin; varsayılan kapalı, Ayarlar'dan açılır ⭐

Kullanıcı isterse açar. Store kurallarıyla en uyumlu yol; kimse istemediği bir başlangıç uygulamasıyla karşılaşmaz.

### B — 1.0.2'ye girsin; ilk açılışta bir kez sorulsun

İlk açılışta küçük bir bilgi çubuğu: "Windows açılınca başlatılsın mı? [Evet] [Hayır]". Daha çok kişi açar ama ilk
açılışa bir adım ekler.

### C — 1.0.2'ye girmesin

1.0.2 yalnız hazır olan değişikliklerle hemen gönderilir; başlatma sonraki sürüme kalır.

## Öneri

A. Değer yüksek, maliyet düşük ve Store'un beklediği davranış bu. B'deki soru istenirse sonradan eklenebilir.

## Cevap

**C — 1.0.2'ye girmesin**

## Sonuç

C uygulandı:

- **Bu sürüm:** Windows açılınca başlatma bu sürüme girmedi. Sürüm, yeni özellikler (15 dil, yeni Ayarlar penceresi)
  içerdiği için 1.0.2 yerine 1.1.0 oldu (T138). Paketler hazırlandı (`PHASE18.md` → 18.9).
- **Sonraki sürüm:** Özellik GitHub projesinde "Windows Startup'ta Açma" taslağı olarak 1.2.0 için bekliyor. Taslak bu
  karta bağlantı veriyor.

Kontrol: uygulandı — 1.1.0 paketlerinin manifestinde başlangıç görevi (`windows.startupTask`) yok; GitHub projesinde
"Windows Startup'ta Açma" öğesi var.

