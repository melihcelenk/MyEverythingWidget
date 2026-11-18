# Faz 10 — Kompakt ikon davranışı, tek ikon penceresi, sağ tık menüsü, tutamaç

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Faz 9'daki kompakt mod ve emoji özellikleri kullanıcı geri bildirimine göre düzeltildi. Kompakt ikon artık her zaman
üstte duruyor, widget'ın köşesinde çıkıyor, sürüklenince fareyi izleyip bırakınca duruyor; açılan widget ikonun
ekranına sığıyor. Emoji, kendi resmi ve sıfırlama tek bir "Change icon…" penceresinde toplandı; boş alana sağ tıkla
ekleme menüsü açılıyor ve kartın boyutlandırma tutamacı her resimde görünüyor.

## Problem

- Kompakt ikon üstte kalmıyordu. Kompakt mod her zaman üstte olmalı.
- Kompakt moda geçerken konum değişiyordu. Kompakt moda geçildiğinde konum değişmemeli; bu konuda TaskTimerWidget
  örnek alınmalı.
- Sürükleme bırakınca başlıyordu. Kompakt ikon sol tuş basılıyken hareket etmiyor; tuş bırakılınca imlecin konumuna
  gelip hareket etmeye başlıyor ve durması için yeniden tıklamak gerekiyor. Bu davranış olmamalı; TaskTimerWidget bu
  konuda doğru davranıyor.
- Açılan widget diğer ekrana taşıyordu. Çift ekranlı düzende ikon sağ üstteyken tıklanınca widget ikonun konumundan
  başlıyor. Widget bulunduğu ekrana sığmıyorsa sola kaymalı, tamamen o ekrana sığmalı ve diğer ekrana taşmamalı.
- İkon değiştirme dağınıktı. Emoji doğrudan bir menüden seçilmeli; Win + . paneline yönlendirilmemeli. Kendi resmini
  yükleme, emoji seçme ve ikonu sıfırlama aynı işi yaptığı için tek düğmenin açtığı aynı ekranda olmalı; ayrı ayrı
  düğmeler olmamalı.
- Boş alanda menü yoktu. Boş bir alana sağ tıklanınca menü açılmalı ve bu menüden ekleme (Add) yapılabilmeli.
- Tutamaç kötü görünüyordu. Kartın üzerine gelindiğinde sağ altta çıkan boyutlandırma ikonu kötü görünüyor ve koyu
  resimlerde görünmüyor; pencere boyutlandırmasında olduğu gibi çift oklu işaret görünmeli.

## Çözüm

- **Kompakt ikon:** Her zaman üstte; widget'ın görünen sol üst köşesinde çıkar; sürükleme imlecin ekran konumu
  izlenerek yapılır.
- **Açılış konumu (`WindowPlacement.FitInside`):** Widget ikonun köşesinden açılır, ekranın çalışma alanına sığmıyorsa
  yalnız gerektiği kadar kayar.
- **İkon penceresi:** Kart menüsünde tek "Change icon…"; pencerede 56 emojilik ızgara, "Image…" ve "Reset to original".
- **Sağ tık:** Izgaranın ve zeminin boş yerinde "Add app…", "Add note", "Add image…".
- **Tutamaç:** Kendi zemini ve kenarı olan yuvarlak rozet, içinde çapraz çift ok; imleç `SizeNorthwestSoutheast` olur.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 10.1 | Kompakt ikon her zaman üstte durur. | 🟢 Tamamlandı |
| 10.2 | Kompakt moda geçerken pencerenin konumu değişmez. | 🟢 Tamamlandı |
| 10.3 | Kompakt ikon sürüklenince fareyi izler ve bırakınca durur. | 🟢 Tamamlandı |
| 10.4 | İkondan açılan widget ikonun bulunduğu ekrana sığar. | 🟢 Tamamlandı (iki ekran yalnız unit testte) |
| 10.5 | Emoji, resim ve sıfırlama tek bir ikon penceresindedir. | 🟢 Tamamlandı |
| 10.6 | Boş alana sağ tıklayınca ekleme menüsü açılır. | 🟢 Tamamlandı |
| 10.7 | Boyutlandırma tutamacı her resimde görünür ve çift oklu imleç gösterir. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- [ ] Pin kapalıyken kompakt moda geç, başka bir pencereye tıkla: ikon üstte kalmalı. Widget'ı aç: artık üstte
  kalmamalı.
- [ ] Kompakt moda geç: ikon, widget'ın sol üst köşesinin tam yerinde çıkmalı.
- [ ] İkonu sol tıkla basılı tutup sürükle: ikon fareyle birlikte gitmeli; bırakınca durmalı, fare hareketi artık onu
  taşımamalı.
- [ ] İkonu ekranın sağ üst (ya da sağ alt) köşesine götürüp tıkla: widget aynı ekranda, kenara yaslanmış açılmalı;
  diğer ekrana taşmamalı.
- [ ] Bir kartta sağ tık → "Change icon…": emoji ızgarası, "Image…" ve "Reset to original" aynı pencerede olmalı; bir
  emojiye tıklayınca kartta görünmeli ve pencere kapanmalı.
- [ ] Izgaranın boş bir yerine sağ tıkla: "Add app…", "Add note", "Add image…" çıkmalı; "Add note" not eklemeli.
- [ ] Koyu bir resim kartının üzerine gel: sağ alttaki tutamaç görünmeli; üzerine gelince imleç çapraz çift ok olmalı.

## Kalan

- Yok.

## Ayrıntılar

### 10.1 — Kompakt ikon her zaman üstte durur.

- **Mevcut durum:** Kompakt ikon pin ayarına uyuyordu; pin kapalıysa diğer pencerelerin arkasında kalıyordu.
- **Problem:** Kompakt mod her zaman üstte olmalı.
- **Çözüm:**
  - Kompakt ikon pin ayarından bağımsız olarak her zaman üstte durur. Widget açılınca pin ayarına döner.
  - TaskTimerWidget da her zaman üstte duruyor (`IsAlwaysOnTop = true`).
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CompactAndMenuTests.cs` →
  `CompactIcon_StaysOnTop_AndWidgetReturnsToItsPinSetting` (kompakt ikon her zaman üstte; açılınca pin kapalıysa üstte
  kalmaz)
- **Durum:** 🟢 Tamamlandı.

### 10.2 — Kompakt moda geçerken pencerenin konumu değişmez.

- **Mevcut durum:** Kompakt moda geçince çerçeve kaldırıldığı için ikon widget'ın köşesinden kayıyordu.
- **Problem:** Kompakt moda geçildiğinde konum değişmemeli; bu konuda TaskTimerWidget örnek alınmalı.
- **Çözüm:**
  - İkon, widget'ın görünen sol üst köşesinde çıkar; çerçevenin kaldırılmasından doğan kayma düzeltilir.
  - TaskTimerWidget kompakt moda geçerken yalnız `AppWindow.Resize` çağırıyor; sol üst köşe yerinde kalıyor. Bizdeki
    davranış konum açısından aynı.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CompactAndMenuTests.cs` → `CompactIcon_AppearsExactlyAtTheWidgetCorner`
  (ikonun istemci köşesi widget'ın istemci köşesiyle aynı piksel)
- **Durum:** 🟢 Tamamlandı.

### 10.3 — Kompakt ikon sürüklenince fareyi izler ve bırakınca durur.

- **Mevcut durum:** Sürükleme `WM_NCLBUTTONDOWN` + `HTCAPTION` ile sistemin taşıma döngüsüne bırakılıyordu. WinUI'nin
  girdi penceresi fareyi tuttuğu için taşıma bırakmadan sonra başlıyordu ve durdurmak için tekrar tıklamak gerekiyordu.
- **Problem:** Kullanıcı basılıyken taşınmasını, bırakınca durmasını istiyor (TaskTimerWidget'taki gibi).
- **Çözüm:**
  - Sürükleme sistemin taşıma döngüsüyle değil, imlecin ekran konumunu izleyerek yapılır.
  - TaskTimerWidget sürüklemeyi `SetTitleBar` ile sistemin yerel sürüklemesine bırakıyor. Bizde imleç izleniyor;
    bırakınca durduğunu test doğruluyor.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CompactAndMenuTests.cs` →
  `DraggingCompactIcon_FollowsTheMouseAndStopsOnRelease` (basılıyken pencere fareyle birlikte gider; bırakınca fare
  hareketi pencereyi taşımaz)
- **Durum:** 🟢 Tamamlandı.

### 10.4 — İkondan açılan widget ikonun bulunduğu ekrana sığar.

- **Mevcut durum:** Widget ikonun konumundan açılıyor, sağ üstteki ikondan açılınca çift ekranda diğer ekrana
  taşıyordu.
- **Problem:** Widget bulunduğu ekrana sığmalı, sığmıyorsa sola kaymalı; diğer ekrana taşmamalı.
- **Çözüm:** Widget, ikonun sol üst köşesinden açılır. İkonun bulunduğu ekranın çalışma alanına sığmıyorsa yalnızca
  gerektiği kadar sola veya yukarı kayar (`WindowPlacement.FitInside`).
- **Dosyalar:** `src/MyEverythingWidget.Core/Geometry/WindowPlacement.cs`, `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CompactAndMenuTests.cs` →
  `OpeningIconNearScreenEdge_KeepsWidgetOnThatMonitor` (sağ alt köşedeki ikondan açılan widget çalışma alanına sığar ve
  kenarlara yaslanır); `tests/MyEverythingWidget.Core.Tests/Geometry/FitInsideTests.cs`
- **Durum:** 🟢 Tamamlandı (iki ekranlı kurulum Sandbox'ta yok; "diğer ekrana taşmaz" kısmı `FitInsideTests` ile ikinci
  ekran koordinatlarında sınanıyor).

### 10.5 — Emoji, resim ve sıfırlama tek bir ikon penceresindedir.

- **Mevcut durum:** Kart menüsünde ayrı "Change icon…", "Use emoji…" ve "Reset icon" öğeleri vardı; emoji Win + . ile
  seçiliyordu.
- **Problem:** Emoji doğrudan bir menüden seçilmeli; kendi resmi, emoji ve sıfırlama aynı işi yaptığı için tek
  düğmenin aynı ekranında olmalı.
- **Çözüm:**
  - Kart menüsünde tek bir "Change icon…" var.
  - Açılan pencerede 56 emojilik bir ızgara (tıklanınca uygulanır ve pencere kapanır), "Image…" ve "Reset to original"
    düğmeleri bulunur.
  - "Use emoji…" ve "Reset icon" menü öğeleri kaldırıldı.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/IconPickerDialog.cs`, `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`,
  `src/MyEverythingWidget.Core/Apps/IconEmoji.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/WindowLayoutTests.cs` → `EmojiPickedInIconDialog_ReplacesCardIcon`;
  `tests/MyEverythingWidget.UiTests/AppItemTests.cs` → `ResetIcon_GivesCardItsProgramIcon`;
  `tests/MyEverythingWidget.Core.Tests/Apps/IconEmojiTests.cs`
- **Durum:** 🟢 Tamamlandı (pencere Faz 13'te "Select icon / Select image" sekmelerine ayrıldı).

### 10.6 — Boş alana sağ tıklayınca ekleme menüsü açılır.

- **Mevcut durum:** Boş alana sağ tıklayınca bir şey olmuyordu; ekleme yalnız düğmelerden yapılıyordu.
- **Problem:** Boş bir alana sağ tıklanınca menü açılmalı ve bu menüden ekleme (Add) yapılabilmeli.
- **Çözüm:** Izgaranın ve altındaki zeminin boş yerine sağ tıklayınca "Add app…", "Add note", "Add image…" açılır.
  Kartların kendi menüsü değişmedi.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml`, `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/CompactAndMenuTests.cs` → `RightClickOnEmptyGrid_OffersAddMenu` (boş
  ızgaraya sağ tık → "Add note" ile not eklenir)
- **Durum:** 🟢 Tamamlandı.

### 10.7 — Boyutlandırma tutamacı her resimde görünür ve çift oklu imleç gösterir.

- **Mevcut durum:** Kartın sağ altındaki genişletme işareti kötü duruyordu ve koyu resimlerde görünmüyordu.
- **Problem:** Tutamaç her zeminde görünmeli ve pencere köşesindeki gibi çift oklu imleç göstermeli.
- **Çözüm:**
  - Kartın sağ altında, kendi zemini ve kenarı olan yuvarlak bir rozet var; koyu resimlerde de görünür.
  - Rozetin içinde çapraz çift ok çizili.
  - Üzerine gelince imleç, pencere köşesindeki çapraz çift oka (`SizeNorthwestSoutheast`) döner.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/ResizeGrip.cs`, `src/MyEverythingWidget.App/Views/GridCard.xaml`
- **Testler:** `tests/MyEverythingWidget.UiTests/CompactAndMenuTests.cs` → `ResizeGrip_ShowsTheDiagonalResizeCursor`
  (tutamacın üzerinde imleç çapraz çift ok)
- **Durum:** 🟢 Tamamlandı (okun yönü ve konumu Faz 11'de düzeltildi).

### Doğrulanmayan / dikkat edilmesi gereken

- **İki ekran:** İki ekranlı kurulum Sandbox'ta yok. 10.4'ün "diğer ekrana taşmaz" kısmı `FitInsideTests` ile (ikinci
  ekran koordinatlarında) sınanıyor.
- **Testler:** Unit 288/288; yeni UI testleri (`CompactAndMenuTests`, 6) hepsi geçti; tam UI suite 60/60 + 1 izole test.
  Açılış 3,6 s, private bellek 90 MB. Sonar: bulgu yok.
- **Test altyapısı:**
  - `AppSession.Launch` artık ızgara (ya da kompakt ikon) görünüp arayüz oturana kadar bekliyor. Sorun: soğuk açılışta
    pencere içeriği hazır olmadan yapılan ilk tıklama kayboluyordu; önceki commit'te de görülüyordu, `AppItemTests` tek
    başına koşunca düşüyordu.
  - `Wait`, açılan bir diyalog yüzünden zaman aşımına düşen UI Automation çağrısını "henüz yok" sayıyor.
- **Dosya yolları:** Dosyalar alanındaki yollar bugünkü koddan eşlendi; eski doküman dosya adı vermiyordu.

### Referanslar

- `PHASE9.md` (önceki faz)
- `PHASE11.md` (sonraki faz: tutamacın oku ve kart renkleri)
- TaskTimerWidget (`github.com/melihcelenk/TaskTimerWidget`, `master` @ `183bb2b`, `MainWindow.xaml.cs`)
- `MAIN_TODO.md` → 📊 Genel İlerleme → Faz 10

### Önceki doküman içeriği

Eski başlık: MEW-4 Faz 10 — Kompakt ikon davranışı, tek ikon penceresi, sağ tık menüsü, boyutlandırma tutamacı

> Önce: `PHASE9.md`

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| C1 Kompakt ikon her zaman üstte | 🟢 Tamamlandı | 10.2 → Kompakt ikon |
| C2 Kompakt moda geçerken konum değişmez | 🟢 Tamamlandı | 10.2 → Kompakt ikon |
| C3 Sürükleme fareyi izler, bırakınca durur | 🟢 Tamamlandı | 10.2 → Kompakt ikon |
| C4 Açılan widget ikonun ekranına sığar | 🟢 Tamamlandı | 10.2 → Kompakt ikon |
| C5 Emoji, resim ve sıfırlama tek pencerede | 🟢 Tamamlandı | 10.2 → İkon penceresi |
| C6 Boş alana sağ tık ile ekleme | 🟢 Tamamlandı | 10.2 → Sağ tık |
| C7 Boyutlandırma tutamacı görünür, çift oklu imleç | 🟢 Tamamlandı | 10.2 → Tutamaç |

---

#### 10.1 Gereksinimler

- Gereksinim: Kompakt mod her zaman üstte olmalı.
- Gereksinim: Kompakt moda geçildiğinde konum değişmemeli; bu konuda TaskTimerWidget örnek alınmalı.
- Gereksinim: Kompakt ikon sürüklenirken sol tuş basılıyken hareket etmiyor; tuş bırakılınca imlecin konumuna gelip
  hareket etmeye başlıyor ve durması için yeniden tıklamak gerekiyor. Bu davranış olmamalı; TaskTimerWidget bu
  konuda doğru davranıyor.
- Gereksinim: Çift ekranlı düzende ikon sağ üstteyken tıklanınca widget ikonun konumundan başlıyor. Widget bulunduğu
  ekrana sığmıyorsa sola kaymalı, tamamen o ekrana sığmalı ve diğer ekrana taşmamalı.
- Gereksinim: Emoji doğrudan bir menüden seçilmeli; Win + . paneline yönlendirilmemeli. Kendi resmini yükleme, emoji
  seçme ve ikonu sıfırlama aynı işi yaptığı için tek düğmenin açtığı aynı ekranda olmalı; ayrı ayrı düğmeler
  olmamalı.
- Gereksinim: Boş bir alana sağ tıklanınca menü açılmalı ve bu menüden ekleme (Add) yapılabilmeli.
- Gereksinim: Kartın üzerine gelindiğinde sağ altta çıkan boyutlandırma ikonu kötü görünüyor ve koyu resimlerde
  görünmüyor; pencere boyutlandırmasında olduğu gibi çift oklu işaret görünmeli.

---

#### 10.2 Kararlar

- **Kompakt ikon:**
  - Pin ayarından bağımsız olarak her zaman üstte durur. Widget açılınca pin ayarına döner.
  - İkon, widget'ın görünen sol üst köşesinde çıkar; çerçevenin kaldırılmasından doğan kayma düzeltilir.
  - Sürükleme sistemin taşıma döngüsüyle değil, imlecin ekran konumunu izleyerek yapılır. Önceki yöntem
    (`WM_NCLBUTTONDOWN` + `HTCAPTION`) WinUI'nin girdi penceresi fareyi tuttuğu için bırakmadan sonra başlıyordu.
  - Widget, ikonun sol üst köşesinden açılır. İkonun bulunduğu ekranın çalışma alanına sığmıyorsa yalnızca gerektiği
    kadar sola veya yukarı kayar (`WindowPlacement.FitInside`).
  - TaskTimerWidget (`github.com/melihcelenk/TaskTimerWidget`, `master` @ `183bb2b`, `MainWindow.xaml.cs`) ile
    karşılaştırıldı.
    - O da her zaman üstte duruyor (`IsAlwaysOnTop = true`).
    - Kompakt moda geçerken yalnız `AppWindow.Resize` çağırıyor; sol üst köşe yerinde kalıyor.
    - Sürüklemeyi `SetTitleBar` ile sistemin yerel sürüklemesine bırakıyor.
    - Bizdeki davranış konum ve üstte kalma açısından aynı. Sürükleme imleç izlenerek yapılıyor; bırakınca durduğunu
      test doğruluyor.
- **İkon penceresi:** Kart menüsünde tek bir "Change icon…" var. Açılan pencerede 56 emojilik bir ızgara (tıklanınca
  uygulanır ve pencere kapanır), "Image…" ve "Reset to original" düğmeleri bulunur. "Use emoji…" ve "Reset icon" menü
  öğeleri kaldırıldı.
- **Sağ tık:** Izgaranın ve altındaki zeminin boş yerine sağ tıklayınca "Add app…", "Add note", "Add image…" açılır.
  Kartların kendi menüsü değişmedi.
- **Tutamaç:**
  - Kartın sağ altında, kendi zemini ve kenarı olan yuvarlak bir rozet var; koyu resimlerde de görünür.
  - Rozetin içinde çapraz çift ok çizili.
  - Üzerine gelince imleç, pencere köşesindeki çapraz çift oka (`SizeNorthwestSoutheast`) döner.

---

#### 10.3 Kabul kriterleri ve testler

| # | Kriter | Test |
|---|--------|------|
| C1 | Kompakt ikon her zaman üstte; açılınca pin kapalıysa üstte kalmaz | `CompactAndMenuTests.CompactIcon_StaysOnTop_AndWidgetReturnsToItsPinSetting` |
| C2 | İkonun istemci köşesi widget'ın istemci köşesiyle aynı piksel | `CompactAndMenuTests.CompactIcon_AppearsExactlyAtTheWidgetCorner` |
| C3 | Basılıyken pencere fareyle birlikte gider; bırakınca fare hareketi pencereyi taşımaz | `CompactAndMenuTests.DraggingCompactIcon_FollowsTheMouseAndStopsOnRelease` |
| C4 | Sağ alt köşedeki ikondan açılan widget çalışma alanına sığar ve kenarlara yaslanır | `CompactAndMenuTests.OpeningIconNearScreenEdge_KeepsWidgetOnThatMonitor`, `FitInsideTests` |
| C5 | Menüde yalnız "Change icon…"; pencerede emoji tıklanınca kartta görünür; Image ve Reset düğmeleri var | `WindowLayoutTests.EmojiPickedInIconDialog_ReplacesCardIcon`, `AppItemTests.ResetIcon_GivesCardItsProgramIcon`, `IconEmojiTests` |
| C6 | Boş ızgaraya sağ tık → "Add note" ile not eklenir | `CompactAndMenuTests.RightClickOnEmptyGrid_OffersAddMenu` |
| C7 | Tutamacın üzerinde imleç çapraz çift ok | `CompactAndMenuTests.ResizeGrip_ShowsTheDiagonalResizeCursor` |

İki ekranlı kurulum Sandbox'ta yok. C4'ün "diğer ekrana taşmaz" kısmı `FitInsideTests` ile (ikinci ekran koordinatlarında)
sınanıyor.

---

#### 10.4 Sonuç

- **Testler:**
  - Unit: 288/288.
  - Yeni UI testleri (`CompactAndMenuTests`, 6): hepsi geçti.
  - Tam UI suite: 60/60 + 1 izole test. Açılış 3,6 s, private bellek 90 MB.
  - Sonar: bulgu yok.
- **Test altyapısı:**
  - `AppSession.Launch` artık ızgara (ya da kompakt ikon) görünüp arayüz oturana kadar bekliyor.
    - Sorun: soğuk açılışta pencere içeriği hazır olmadan yapılan ilk tıklama kayboluyordu.
    - Önceki commit'te de görülüyordu; `AppItemTests` tek başına koşunca düşüyordu.
  - `Wait`, açılan bir diyalog yüzünden zaman aşımına düşen UI Automation çağrısını "henüz yok" sayıyor.
