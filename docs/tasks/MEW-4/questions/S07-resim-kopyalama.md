---
id: S7
status: resolved
decider: user
priority: major
asked: 2026-11-03
resolved: 2026-11-18
---
# S7 — "Resim kopyalama işini geliştir": hangi yön?

**Mevcut durum:** Resim kartından panoya kopyalama yok; resmi widget'a almak ise Ctrl+V, sürükle-bırak ve "Image…" ile çalışıyor.

**Soru:** "Resim kopyalama" ile hangisini kastediyorsun?

## Bağlam

Bugün resimle ilgili durum şöyle:

| Yön | Bugün |
|-----|-------|
| Widget'tan dışarı: resim kartını panoya kopyalamak | **Yok.** Not kartlarında sağ üstte "Copy" düğmesi var; resim kartlarında ne düğme ne menü öğesi var. Sağ tık menüsünde yalnız "Move to" ve "Delete". |
| Dışarıdan widget'a: Ctrl+V | Ekran görüntüsü, kopyalanmış resim dosyası ve metin kart olur. |
| Dışarıdan widget'a: sürükle-bırak | Dosya, klasör ve bağlantılar uygulama kartı olur. Resim dosyası sürüklenince resim kartı değil, uygulama kartı oluyor. |
| Resmi büyük görme | Karta tıklayınca ayrı pencerede açılıyor. |

## Seçenekler

### A — Resim kartından panoya kopyalama ⭐

- Resim kartının üzerine gelince, not kartındaki gibi sağ üstte "Copy" düğmesi çıkar.
- Sağ tık menüsünde de "Copy image" olur.
- Resim panoya resim olarak gider: Paint, Word, Teams, tarayıcı gibi yerlere yapıştırılabilir.
- Büyük görüntüleme penceresinde Ctrl+C de aynı işi yapar.

### B — Widget'a resim almayı iyileştir

- Explorer'dan sürüklenen resim dosyası, uygulama kartı yerine resim kartı olur.
- Tarayıcıdan sürüklenen ya da kopyalanan resim (bağlantı değil, resmin kendisi) resim kartı olur.

### C — İkisi birden (A + B)

### D — Başka bir şey

- Cevap'a ne istediğini yaz.

## Öneri

A. "Kopyalama" en doğrudan resmi widget'tan alıp başka yere yapıştırmak demek ve bugün hiç yok. B'deki "resim dosyasının uygulama kartı olması" da bir eksik; istersen C ile birlikte yapayım.

## Cevap

**C — İkisi birden (A + B)**

## Sonuç

C uygulandı (2026-11-17). Değişiklikler commit'lenmedi; commit senin. Ayrıntı: `PHASE15.md`.

- **A — Kopyalama:**
  - Resim kartının üzerine gelince sağ üstte kopyalama düğmesi çıkıyor.
  - Sağ tık menüsünde "Copy image" var.
  - Görüntüleme penceresinde Ctrl+C çalışıyor.
  - Resim panoya hem resim (Paint, Word, sohbet) hem dosya (Explorer) olarak gidiyor; widget kapansa da panoda kalıyor.
- **B — Resim alma:**
  - Sürüklenen resim dosyası artık uygulama kartı değil, resim kartı oluyor; resim + program birlikte bırakılırsa ikisi
    de doğru kart oluyor.
  - Bir uygulamadan sürüklenen resmin kendisi (bitmap) de resim kartı oluyor.
- **Ek düzeltme:**
  - Ayarlar kapanınca "Settings" ipucu ızgaranın köşesinde asılı kalıyordu; artık kalmıyor.
  - Bu hata, tema testlerinin düşmesinden bulundu.
- **Sınır:**
  - Tarayıcılar resmi sürüklerken çoğunlukla resmin adresini gönderir; o durumda eskisi gibi web sitesi kartı oluşur.
  - Tarayıcıda "Resmi kopyala" + Ctrl+V resim kartı verir.
- **Testler:**
  - 3 yeni UI testi (kopyalama) ve 3 yeni unit testi (bırakma); hepsi önce kırmızı, sonra yeşil.
  - Tam UI suite 77/77 + 1; unit 296/296.
- **Test edilemeyen:** Gerçek Explorer/tarayıcı sürükle-bırakı Sandbox'ta otomatik test edilemiyor; elle denenmeli.

Kontrol: uygulandı — `ClipboardWriter.cs`, `CopyImageButton`/`CopyImageMenuItem`/viewer Ctrl+C, `AddDroppedAsync` + `AddDroppedPictureAsync`; `ImageCopyTests` 3 + `NotesImagesPasteTests` 3 test, tam UI 77/77 (çalışma kopyasında, commit edilmedi).
