# MEW-4 Faz 10 — Kompakt ikon davranışı, tek ikon penceresi, sağ tık menüsü, boyutlandırma tutamacı

> Önce: `PHASE9.md`

## İçindekiler

- Durum Panosu
- 10.1 İstekler (birebir)
- 10.2 Kararlar
- 10.3 Kabul kriterleri ve testler
- 10.4 Sonuç

---

## Durum Panosu

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

## 10.1 İstekler (birebir)

> 1- Compact mod her zaman üstte olmalı.
> 2- Compact moda geçtiğinde lokasyon değişmemeli, TaskTimerWidget bu konuda iyiydi örnek alabilirsin.
> 3- Compact modu sürüklemeye başlıyorum, sol tıkı basmayı bırakana kadar hareket etmiyor. Sol tıkı bırakınca
>    bulunduğum konuma gelip hareket etmeye başlıyor. Oysa zaten bırakmıştım. Tekrar tıklamam gerekiyor konumu
>    durdurmak için. Bu olmamalı. TaskTimerWidget bu konuda iyiydi.
> 4- Sağ üstteyken tıklayınca çift ekrandayım, ikonun konumundan başlıyor. Oysa bulunduğum ekrana sığmıyorsa sola
>    kaymalı. Tam ekrana sığacak şekilde olmalı. Diğer ekrana taşmamalı.
> 5- Emoji seçme direkt bir menü üstünden olmalı öyle win . gibi bir saçmalığa gidilmemeli. Ayrıca kendi resmimizi
>    yükleme ve emoji ve reset ikon bu tek butonun aynı ekranında olmalı hepsi aynı işi yapıyor. Ayrı ayrı butonlar
>    olmamalı.
> 6- Boş bir yere sağ tık yapıp menü açılmalı, add yapabilmeliyim.
> 7- Şu her ikone geldiğimde sağ alttaki genişletme vs ikonu kötü duruyor ve koyu resimlerde görünmüyor. Yine aynı
>    pencereyi genişlettiğimiz gibi onda da aynı çift oklu işaret görünmeli.

---

## 10.2 Kararlar

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

## 10.3 Kabul kriterleri ve testler

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

## 10.4 Sonuç

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
