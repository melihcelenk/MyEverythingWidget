# Faz 17 — Ayarlar penceresinin kenar boşluğu ve yayın hazırlığı

> **Durum:** 🟡 Devam ediyor · **Tamamlanma:** 75% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Ayarlar penceresi artık widget'ın iki yanından boşluk bırakıyor; aynı düzen bütün iletişim kutularına uygulandı. Widget
2 sütuna kadar küçültülse de içerik kırpılmıyor. README ve Store için beş kullanım senaryosunu anlatan ekran
görüntüsü Sandbox'ta tek komutla (`scripts/capture-screenshots.ps1`) çekiliyor. Kalan iş `master`'a birleştirme ve
Store gönderimi.

## Problem

- Ayarlar penceresi widget'ın bütün genişliğini kaplıyordu; iki yanda hiç boşluk yoktu (T10).
- README'de ekran görüntüsü yok; UI testlerinin görüntüleri rastgele veriyle çekilmiş. Görüntüler, uygulamanın hangi
  işler için kullanılabileceğini gösteren senaryoları içermeli (T10).

## Çözüm

- **İletişim kutuları (`DialogSizing.FitToWindow`):**
  - Bütün iletişim kutuları pencereden iki yanda 12 piksel boşluk bırakıyor. En geniş hali penceredeki yer kadar
    oluyor; WinUI'nin 320 piksellik en küçük genişliği dar pencerede bu genişliğe iniyor.
  - Pencere 320 pikselden darsa iç boşluk 24 yerine 12 piksel oluyor.
- **Ayarlar içeriği:** Sabit 300 piksel genişlik kaldırıldı. RadioButton ve ToggleSwitch'in en küçük genişliği
  sıfırlandı, böylece metinler kırpılmak yerine alt satıra geçiyor. Anahtarın yazısı da "On/Off" oldu; önceden
  sistem dilinde ("Kapalı") görünüyordu.
- **Ekran görüntüleri (S8 → A):**
  - `ShowcaseScreenshots` Sandbox'ta uydurma ama gerçekçi içerikle 5 senaryoyu kurup çekiyor.
  - `scripts/capture-screenshots.ps1` her çekimi 1366x768'lik başlıklı bir sayfaya yerleştirip `docs/images/`'a
    yazıyor; README ve Store aynı dosyaları kullanıyor.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 17.1 | Ayarlar ve diğer iletişim kutuları pencerenin iki yanından boşluk bırakır; dar pencerede içerik kırpılmaz. | 🟢 Tamamlandı |
| 17.2 | GitHub README'si kullanım senaryolarını gösteren ekran görüntüleriyle güncellenir. | 🟢 Tamamlandı |
| 17.3 | Branch `master`'a birleştirilir (PR #1). | ⏳ Bekliyor (kullanıcı) |
| 17.4 | Store gönderimi için ekran görüntüleri ve paket hazırlanır. | 🟡 Kısmi (görüntüler hazır; gönderim `PHASE8.md` → 8.6) |
| 17.5 | Not düzenleme penceresi çok satırlı notun tamamını gösterir. | 🟢 Tamamlandı |
| 17.6 | Tanıtım görselleri üçe iner; ilki uygulama, web sitesi, not ve fotoğrafı birlikte gösterir. | 🟢 Tamamlandı |
| 17.7 | Compact ikon ekranın sağındayken widget ikonla hizalı açılır; küçültünce ikon yerinde kalır. | 🟢 Tamamlandı |
| 17.8 | Repo halka açılmaya hazırlanır: görev dokümanlarının dili ve eksik standart dosyalar. | 🟡 Kısmi (halka açılınca gizli güvenlik bildirimi açılmalı) |

## Nasıl kontrol edilir

- [ ] Widget'ı normal boyutta açıp ayarlara gir: pencerenin sağında ve solunda boşluk görünmeli.
- [ ] Widget'ı 2 sütuna küçültüp ayarlara gir: "Use Windows setting" alt satıra geçmeli, "Close" düğmesi tam görünmeli.
- [ ] "Add", not düzenleme ve ikon değiştirme pencerelerinde de iki yanda boşluk olmalı.
- [ ] `docs/images/showcase-1.png` … `showcase-5.png` dosyalarına ve GitHub'daki README'ye bak: her görüntü tek bir
  kullanımı anlatmalı; rastgele resim ya da not olmamalı.

## Kalan

- **17.3:** PR #1'i kullanıcı birleştirecek.
- **17.4:** Store gönderimi kullanıcının Partner Center hesabıyla yapılır (`PHASE8.md` → 8.6); görüntüler hazır.

## Ayrıntılar

### 17.1 — Ayarlar ve diğer iletişim kutuları pencerenin iki yanından boşluk bırakır; dar pencerede içerik kırpılmaz.

- **Mevcut durum:** Ayarlar penceresi widget'ın kenarından kenarına uzanıyordu. WinUI iletişim kutuları en az 320
  piksel genişliğinde; widget ondan dar olunca kutu pencereye yapışıyordu.
- **Problem:** Ayarlar penceresinin iki yanında boşluk olmalı; şu an boşluk yok.
- **Çözüm:**
  - Yeni `DialogSizing.FitToWindow(dialog, root)`: `ContentDialogMinWidth` ve `ContentDialogMaxWidth` kaynaklarını
    pencere genişliği eksi 2x12 piksele göre ayarlıyor; kutu 320 pikselden darsa `ContentDialogPadding` 12 piksel.
  - Ayarlar, Add, not/metin düzenleme, ikon ve sekme adı pencerelerinin hepsi bunu açılmadan önce çağırıyor.
  - Ayarlar, Add, metin düzenleme ve ikon penceresindeki sabit genişlikler en çok genişliğe (`MaxWidth`) çevrildi.
  - Ayarlarda RadioButton ve ToggleSwitch'in `MinWidth` değeri 0; anahtar "On/Off" diyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/DialogSizing.cs`, `src/MyEverythingWidget.App/Views/SettingsDialog.xaml`,
  `src/MyEverythingWidget.App/MainWindow.xaml.cs`, `src/MyEverythingWidget.App/Views/AddAppDialog.xaml`,
  `src/MyEverythingWidget.App/Views/TextEditorDialog.cs`, `src/MyEverythingWidget.App/Views/IconPickerDialog.cs`,
  `src/MyEverythingWidget.App/Views/CategoryTabsView.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` → `SettingsDialog_KeepsAGapToTheWindowEdges`
  (5 ve 2 sütun):
  - İçerik pencerenin solundan, "Close" düğmesi sağından en az 34 piksel (dar pencerede 22) içeride.
  - Gizlilik metni düğmelerin sağ kenarını geçmiyor.
  - Her iki genişlikte ekran görüntüsü `settings-<n>-columns.png` olarak kaydediliyor.
- **Durum:** 🟢 Tamamlandı.

### 17.2 — GitHub README'si kullanım senaryolarını gösteren ekran görüntüleriyle güncellenir.

- **Mevcut durum:** README'de ekran görüntüsü yok.
- **Problem:** Görüntüler gerçekçi kullanım senaryolarını anlatmalı; rastgele resim ve not olmamalı.
- **Çözüm (S8 → A, Sandbox'ta otomatik):**
  - **Senaryolar:**
    1. Günlük başlatıcı: uygulama, klasör ve web siteleri.
    2. Sık kopyalanan metinler: uzun bir `docker run` komutu, imza, adres, SQL sorgusu; biri "kopyalandı" durumunda.
    3. Aceleyle alınan notlar: Ctrl+V ile panodan not.
    4. Anlık ekran: uydurma "Ledgerly" uygulamasının hata ekranı ve bir grafik; görüntüleyicide sağ tık menüsü.
    5. Compact ikon (koyu tema).
  - **Gerçekçilik:**
    - Uygulama kartları gerçek kabuk ikonlarını uygulamanın kendi `ShellIconStore`'u ile alıyor.
    - Sandbox'ta ağ olmadığı için web kartlarında emoji var.
  - **Çekim:**
    - Masaüstü düz renge çevriliyor (duvar kâğıdı ve görev çubuğu görünmüyor).
    - Her çekim pencerelerin 72 piksel çevresinden kırpılıyor.
  - **Normal UI koşusu:** Bu sınıf `Category=Showcase` trait'iyle normal UI koşusundan çıkarıldı.
  - **Ek düzeltme:** Test için yayımlanan uygulamaya `Assets` kopyalanmadığı için compact ikon boş görünüyordu. Assets
    artık publish'te kopyalanıyor (`CopyToPublishDirectory`).
- **Dosyalar:** `tests/MyEverythingWidget.UiTests/ShowcaseScreenshots.cs`, `tests/MyEverythingWidget.UiTests/Showcase/*.png`,
  `tests/MyEverythingWidget.UiTests/MyEverythingWidget.UiTests.csproj`, `scripts/capture-screenshots.ps1`,
  `scripts/test-ui.ps1`, `src/MyEverythingWidget.App/MyEverythingWidget.App.csproj`, `docs/images/showcase-*.png`,
  `README.md`, `docs/general/STORE_LISTING.md`, `docs/general/DEVELOPMENT.md`
- **Testler:** `pwsh scripts/capture-screenshots.ps1` → 5/5 çekim; görüntüler tek tek gözle kontrol edildi.
- **Durum:** 🟢 Tamamlandı.

### 17.3 — Branch `master`'a birleştirilir (PR #1).

- **Mevcut durum:** PR #1 açık.
- **Çözüm:** Kullanıcı inceleyip birleştirir.
- **Durum:** ⏳ Bekliyor (kullanıcı).

### 17.4 — Store gönderimi için ekran görüntüleri ve paket hazırlanır.

- **Mevcut durum:** Paket ve listeleme metni Faz 8'de hazırlandı; Store görüntüleri test verisiyle çekilmişti.
- **Çözüm:** Store görüntüleri 17.2'dekilerle aynı (1366x768, Store'un önerdiği en küçük boyut). Paket
  `scripts/publish-msix.ps1` ile; gönderim `PHASE8.md` → 8.6.
- **Durum:** 🟡 Kısmi (gönderim kullanıcıda).

### 17.5 — Not düzenleme penceresi çok satırlı notun tamamını gösterir.

- **Mevcut durum:** Çok satırlı bir notu "Edit" ile açınca metin kutusunda yalnız ilk satır görünüyor (T16).
- **Problem:** `TextEditorDialog` önce `Text`, sonra `AcceptsReturn` veriyor; WinUI tek satırlık kutuya verilen metni
  ilk satır sonunda kesiyor. "Save"e basılırsa notun geri kalanı silinir.
- **Çözüm (S9 → A):** `AcceptsReturn` ve `TextWrapping` artık metinden önce veriliyor; metin kutusu kurulduktan sonra
  `Text` atanıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/TextEditorDialog.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/NoteImagePasteTests.cs` →
  `EditNoteFromMenu_ShowsEveryLine_AndSavingUnchangedKeepsThem`. Test dört satırlık bir notu açıyor, düzenleme
  penceresinde dört satırın da olduğunu ve değiştirmeden kaydedince notun aynı kaldığını kontrol ediyor.
  - Düzeltmeden önce kırmızıydı: pencerede yalnız "First line of the note." vardı.
  - Düzeltmeden sonra `NoteImagePasteTests` 9/9 geçiyor.
- **Durum:** 🟢 Tamamlandı.

### 17.6 — Tanıtım görselleri üçe iner; ilki uygulama, web sitesi, not ve fotoğrafı birlikte gösterir.

- **Mevcut durum:** Beş görsel var; ilki yalnız uygulama ikonlarından oluşuyor, 4.'sü bir hata ekranı gösteriyor (T18).
- **Problem:** İlk görsel tek bakışta ilgi çekmeli; hata ekranı pazarlamada uygulamanın hatası gibi görünüyor.
- **Çözüm:** Üç görselin taslağı `mockups/` altında; onaydan sonra çekilecek. Fotoğraf Unsplash lisanslı bir manzara.
  S10'da soruldu.
  - 2. tur (T19): metinler olumlu; web siteleri herkesin tanıdığı siteler (imdb.com, wikipedia.org…); yazılımcıya
    özgü uygulamalar çıktı.
  - 3. tur (T21): fotoğrafın sağ tık menüsü gerçek haliyle (Copy image, Edit in Paint, Move to, Delete) 2. görselde;
    2. görselde not, iki fotoğraf ve uygulamalar birlikte; resmin de Ctrl+V ile eklendiği etiketle gösteriliyor.
  - 4. tur (T22): 2. görsel Ctrl+V'ye odaklandı ("Copy it. Ctrl+V. Saved in a second."); resim, metin ve web
    adresiyle eklenmiş üç kart vurgulu.
  - 5. tur (T23): üç görselin altına Windows 11 tarzı görev çubuğu; widget'ın masaüstünde durduğunu gösteriyor.
  - 6. tur (T24): 3. görselde compact ikon sağ üstte; ondan widget'a "Click to expand" yazılı ok.
- **Son hal (T25):** Taslaklar onaylandı ve son görseller olarak kullanılıyor. Kartlar, ikonlar ve pencereler gerçek
  Sandbox çekimlerinden alındığı için ayrıca yeniden çekim yapılmadı.
  - `scripts/compose-store-images.py` görselleri `docs/images/captures/` altındaki çekimlerden ve
    `docs/images/assets/` altındaki fotoğraf ve site ikonlarından üretiyor; çıktısı taslaklarla piksel piksel aynı.
  - `scripts/capture-screenshots.ps1` çekimleri `docs/images/captures/`'a yazıp bu betiği çalıştırıyor.
  - README ve `STORE_LISTING.md` üç görsele (`docs/images/store-1.png` … `store-3.png`) geçti.
  - Fotoğraf kaynakları `docs/images/assets/CREDITS.md`'de.
- **Dosyalar:** `scripts/compose-store-images.py`, `scripts/capture-screenshots.ps1`, `docs/images/store-*.png`,
  `docs/images/captures/`, `docs/images/assets/`, `README.md`, `docs/general/STORE_LISTING.md`,
  `docs/general/DEVELOPMENT.md`, `docs/tasks/MEW-4/mockups/`
- **Durum:** 🟢 Tamamlandı.

### 17.7 — Compact ikon ekranın sağındayken widget ikonla hizalı açılır; küçültünce ikon yerinde kalır.

- **Mevcut durum:** Sağdaki ikona tıklayınca widget ekranın sağ kenarına yapışık açılıyor; küçültünce ikon widget'ın
  sol üst köşesine, yani sola kayıyor (T26).
- **Problem:** `ApplyLayoutMode` açarken ve küçültürken hep sol üst köşeyi sabit tutuyor; ekrana sığmayan widget
  `FitInside` ile sola itiliyor.
- **Çözüm (S11 → B, yatay ve dikey):**
  - `WindowPlacement.NearestCorner` ikonun ekranın hangi çeyreğinde olduğunu buluyor (merkezi hangi yarıda).
  - `WindowPlacement.AlignCorner` widget'ı ikonun o köşesinden açıyor: sağ üstteki ikonda sağ ve üst kenarlar, sağ
    alttakinde sağ ve alt kenarlar hizalı.
  - Küçültünce ikon aynı köşeye dönüyor. `MainWindow` açılış köşesini ve widget'ın açıldığı yeri hatırlıyor. Widget
    sonradan taşındıysa ikon, widget'ın ekran köşesine en yakın köşesine gidiyor.
  - Widget ilk kez küçültülünce de aynı kural geçerli. Varsayılan konum sağ üst olduğu için ikon widget'ın sağ üst
    köşesinde çıkıyor (önceden sol üst).
- **Dosyalar:** `src/MyEverythingWidget.Core/Geometry/WindowCorner.cs`, `src/MyEverythingWidget.Core/Geometry/WindowPlacement.cs`,
  `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:**
  - `tests/MyEverythingWidget.Core.Tests/Geometry/CompactCornerTests.cs`: dört çeyrek, ikinci monitör, açılınca kenar
    hizası, açıp kapatınca ikonun aynı yere dönmesi. Önce derlenmeyerek kırmızıydı; Core testleri 203/203 geçiyor.
  - `CompactAndMenuTests.IconOnTheRight_OpensWithTheRightEdgesLinedUp_AndShrinksBackToTheSamePlace` (sağ üst ve
    sağ alt). Kırmızıyken widget ikonun sağ kenarını 43 piksel geçiyordu.
  - `CompactAndMenuTests.CompactIcon_AppearsExactlyAtTheWidgetCorner` testinin yerine
    `CompactIcon_AppearsAtTheWidgetCornerNearestTheScreenCorner` geldi. Eski test ikonun hep widget'ın sol üst
    köşesinde çıkmasını bekliyordu; S11 kararı bu beklentiyi değiştirdi.
  - `CompactAndMenuTests` 8/8, `WindowLayoutTests` 12/12 geçiyor.
- **Durum:** 🟢 Tamamlandı.

### 17.8 — Repo halka açılmaya hazırlanır: görev dokümanlarının dili ve eksik standart dosyalar.

- **Mevcut durum:** Repo gizli. Denetim sonucu (T28):
  - **Temiz olanlar:** Dosyalarda ve git geçmişinde gizli bilgi, şirket iş numarası ya da kişisel dosya yolu yok.
  - **Dil sorunu:** Faz dokümanlarında ve soru kartlarında kullanıcı mesajları birebir, gündelik dille alıntılanmış.
  - **Eksik dosyalar:** `SECURITY.md`, `CONTRIBUTING.md`, CI, repo açıklaması ve etiketleri yok.
- **Problem:** Gündelik dildeki alıntılar dışarıya iyi görünmüyor; ayrıca "birebir alıntı repoya yazılmaz" kuralına
  aykırı. Eksik dosyalar da açık kaynak bir projede beklenen şeyler.
- **Çözüm:**
  - Görev dokümanları ve soru kartları için S12'de, eksikler için S13'te seçenekler sunuldu.
  - S08–S11 kartları S12'nin cevabına kadar commit'lenmedi.
  - Issue şablonları TaskTimerWidget'tan uyarlandı (T29): `.github/ISSUE_TEMPLATE/bug-report.yml`,
    `feature-request.yml`, `config.yml`. Hata raporunda sürüm, kurulum kaynağı, ekran ölçeği ve `logs\crash.log`
    soruluyor. "Questions & Discussions" bağlantısı için repoda Discussions'ın açılması gerekiyor (S13).
- **Yapılan (S12 → A, S13 → B):**
  - **Doküman dili:** `MEW-1`, `MEW-3` ve `MEW-4` görev dokümanlarındaki ve soru kartlarındaki birebir alıntılar
    resmî gereksinim cümlelerine çevrildi; anlam ve kapsam korundu. Kartlar (S08–S14) commit'lendi.
  - **Yeni dosyalar:** `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/pull_request_template.md`,
    `.github/workflows/ci.yml`.
  - **README:** İç iş numarası kaldırıldı; CI ve lisans rozetleri, "Contributing" bölümü eklendi.
  - **CI:** Windows'ta derleme ve unit testler. Komutlar yerelde denendi: 309 test geçti; UI testleri Sandbox
    dışında kendini atlıyor.
- **GitHub ayarları (S14 → A):** Açıklama, on etiket ve Discussions uygulandı.
- **Kalan:** Gizli güvenlik bildirimi yalnız herkese açık repolarda açılabiliyor. Repo halka açılınca
  **Settings → Code security → Private vulnerability reporting** ile ya da
  `gh api -X PUT repos/melihcelenk/MyEverythingWidget/private-vulnerability-reporting` ile açılmalı.
  `SECURITY.md` bu forma yönlendiriyor.
- **Durum:** 🟡 Kısmi (halka açıldıktan sonra tek ayar).

### Doğrulanmayan / dikkat edilmesi gereken

- **Test ölçüsü:** Testin ilk hali iletişim kutusunun dış çerçevesini ölçmek istiyordu. UIA'da kutu, bütün pencereyi
  kaplayan katmanla aynı dikdörtgeni veriyor; bu yüzden ölçüm kutunun içindeki öğelere (tema seçeneği, "Close")
  çevrildi. Dar pencerede 12 piksellik iç boşluk tasarım kararı olduğu için eşik 22 piksel; bu sayı yeşil fazda,
  iç boşluk kararıyla birlikte yazıldı.
- **"Off" denetimi:** İlk sürümdeki "anahtarda Off yazar" denetimi UIA'da bulunamadığı için ekran görüntüsüyle
  değiştirildi; görüntüde "Off" görünüyor.

### Referanslar

- `TALIMATLAR.md` → T10, T11 (aynı talimat; pano ve terminal kaydı)
- `questions/S08-tanitim-ekran-goruntuleri.md`
- `PHASE8.md` → 8.3, 8.4, 8.6
