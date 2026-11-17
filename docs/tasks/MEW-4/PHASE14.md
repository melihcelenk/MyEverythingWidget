# Faz 14 — İkon penceresinin geç açılması

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

İkon penceresi artık menüye tıklayınca gecikmeden açılıyor. Önce gecikmenin nerede olduğu ölçüldü: ilk açılışta renkli
emoji fontunun ilk kez çizilmesi, sonraki açılışlarda 56 düğmenin yerleşimiydi. Emoji ızgarası hafif hücrelerle
yeniden yapıldı, emojiler uygulama açıldıktan sonra fark edilmeden önceden çiziliyor ve pencere her açılışta yeniden
kullanılıyor. Sandbox'ta ilk açılış 3,6 s'den yaklaşık 0,4–0,6 s'ye, sonraki açılışlar yaklaşık 0,5 s'den 0,16–0,23
s'ye indi.

## Problem

- Kullanıcının isteği (birebir): "o tab'ler sayfa açıldıktan yarım saniye filan sora geliyor. Bu da kullanıcı
  açısından akıcılık için kötü bir deneyim. Bunun sebebini tespit et ve fixle."
- Ölçümde görüldü ki sekmeler sonradan gelmiyor; pencerenin kendisi menü tıklamasından sonra geç beliriyor.
- İlk açılış Sandbox'ta 3,3–3,6 s, sonraki açılışlar 0,5–0,8 s sürüyordu.

## Çözüm

- **Hafif hücreler (`EmojiCell`):** Emoji ızgarasında `Button` yerine yuvarlak zeminli tek bir metin öğesi; fare,
  Enter, Boşluk ve UI Automation (Invoke) ile seçim korunuyor.
- **Isınma (`EmojiFontWarmUp`):** Uygulama açıldıktan sonra emojiler görünmez bir katmanda 60 ms aralıklarla birer
  birer çiziliyor.
- **Yeniden kullanım:** Isınma bitince ikon penceresi bir kez kuruluyor ve sonraki her açılışta aynı nesne
  kullanılıyor; seçim, uyarı yazısı ve sekme her açılışta sıfırlanıyor.
- **Test altyapısı (`DpiAwareness`):** UI test süreci "per-monitor DPI aware" yapıldı.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 14.1 | Gecikmenin sebebi ölçülerek bulunur. | 🟢 Tamamlandı |
| 14.2 | İkon penceresinin ilk açılışı hızlanır. | 🟢 Tamamlandı |
| 14.3 | İkon penceresinin sonraki açılışları hızlanır. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| İkon penceresinin geç açılması: hangi çözüm? | A (hafif ızgara + fontu ısıtma) | 🟢 Verildi: A | S6 (`questions/S06-ikon-penceresi-gecikmesi.md`) |

## Nasıl kontrol edilir

- [ ] Widget'ı aç, birkaç saniye bekle, bir karta sağ tıkla → "Change icon…": pencere sekmeleriyle birlikte hemen
  açılmalı; sekmeler sonradan gelmemeli.
- [ ] Pencereyi kapatıp birkaç kez yeniden aç: her seferinde beklemeden açılmalı.
- [ ] Pencerede "Select image" sekmesine geçip kapat, yeniden aç: pencere yine "Select icon" sekmesiyle açılmalı.
- [ ] Emoji ızgarasında bir emojinin üzerine gel ve bas: zemin değişmeli; tıklayınca emoji uygulanmalı.

## Kalan

- Yok.

## Ayrıntılar

### 14.1 — Gecikmenin sebebi ölçülerek bulunur.

- **Mevcut durum:** Kullanıcı sekmelerin pencere açıldıktan yarım saniye kadar sonra geldiğini söyledi; sebebi
  bilinmiyordu.
- **Problem:** Sebebi bilinmeden yapılacak bir düzeltme yanlış yeri hedefleyebilirdi.
- **Çözüm:**
  - Ölçümler Sandbox'ta yapıldı (GPU yok, çizim yazılımla). Menüye tıklamakla pencerenin ekrana gelmesi arasındaki
    süre ekran kareleri karşılaştırılarak bulundu; uygulama içine geçici zaman damgaları da kondu.
  - Gecikme nerede: pencere sekmeleriyle birlikte tek seferde çiziliyor, sonradan değişen bir şey yok. Gecikme, menü
    tıklaması ile pencerenin belirmesi arasında. Ana penceredeki kategori sekmeleri ilk karede çiziliyor; sorun orada
    değil.
  - İlk açılış (3,3–3,6 s): çoğu, renkli emoji fontunun (Segoe UI Emoji) ilk kez çizilmesi. Emojiler arayüzde bir kez
    çizdirildiğinde arayüz iş parçacığı 2,6 s dondu. Font dosyasını önceden okumak ve DirectWrite ile önceden yerleşim
    yaptırmak denendi; ikisi de etkisizdi (çizim maliyeti kaldı).
  - Sonraki açılışlar (0,5–0,8 s): her açılışta yeni diyalog şablonu ve 56 tam `Button`'ın yerleşimi; ardından
    WinUI'nin açılış animasyonu.
- **Dosyalar:** `tests/MyEverythingWidget.UiTests/TabAppearanceTests.cs`
- **Testler:** `TabAppearanceTests.IconDialogTabs_AreDrawnWithTheDialog` (pencere sekmeleri pencereyle birlikte
  çiziliyor; göründükten sonra ≤ 150 ms içinde son hallerinde), `TabAppearanceTests.CategoryTabs_AreDrawnWithTheWindow`
  (kategori sekmeleri ana pencereyle birlikte çiziliyor)
- **Durum:** 🟢 Tamamlandı.

### 14.2 — İkon penceresinin ilk açılışı hızlanır.

- **Mevcut durum:** İlk açılış 3645 ms sürüyordu; çoğu emoji fontunun ilk kez çizilmesiydi.
- **Problem:** Fontun ilk çizimi arayüzü tek seferde 2,6 s donduruyordu.
- **Çözüm:**
  - Isınma (`EmojiFontWarmUp`): uygulama açıldıktan sonra emojiler görünmez bir katmanda, 60 ms aralıklarla birer
    birer çiziliyor.
  - Maliyet tek bir donma yerine küçük parçalara bölünüyor; açılışın ilk birkaç saniyesinde fark edilmiyor.
  - S6'da önerilen arka plan iş parçacığı yolu (font dosyasını okumak, DirectWrite ile önceden yerleşim) işe yaramadı;
    maliyet emojilerin çizilmesinde.
- **Dosyalar:** `src/MyEverythingWidget.App/EmojiFontWarmUp.cs`, `src/MyEverythingWidget.App/MainWindow.xaml`,
  `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/TabAppearanceTests.cs` → `IconDialog_OpensQuickly` (uygulama
  açıldıktan 4 s sonra ilk ikon penceresi tıklamadan sonra ≤ 1,2 s içinde ekranda)
- **Durum:** 🟢 Tamamlandı (ilk açılış 3645 ms → 382–625 ms).

### 14.3 — İkon penceresinin sonraki açılışları hızlanır.

- **Mevcut durum:** Sonraki açılışlar 491 / 563 / 778 ms sürüyordu.
- **Problem:** Her açılışta yeni diyalog şablonu ve 56 tam `Button` yerleşiyordu.
- **Çözüm:**
  - Hafif hücreler: emoji ızgarasında `Button` yerine `EmojiCell` kullanılıyor. Hücre yuvarlak zeminli tek bir metin
    öğesi; üzerine gelince ve basınca zemin değişiyor; tıklama, Enter ve Boşluk ile seçiliyor; UI Automation'da
    "Button" olarak görünüyor ve Invoke destekliyor.
  - Yeniden kullanım: ısınma bitince ikon penceresi bir kez kuruluyor ve sonraki her açılışta aynı nesne kullanılıyor;
    şablon ve ızgara hazır kalıyor. Her açılışta seçim, uyarı yazısı ve sekme ("Select icon") sıfırlanıyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/EmojiCell.cs`, `src/MyEverythingWidget.App/Views/IconPickerDialog.cs`
- **Testler:** `tests/MyEverythingWidget.UiTests/TabAppearanceTests.cs` → `IconDialog_OpensQuickly` (sonraki üç
  açılışın ortancası ≤ 0,4 s)
- **Durum:** 🟢 Tamamlandı (sonraki açılışlar 491 / 563 / 778 ms → 164 / 167 / 228 ms).

### Doğrulanmayan / dikkat edilmesi gereken

- **Ölçüm notu:** "Önce" değerleri, her karede tüm pencereyi piksel piksel karşılaştıran ilk ölçüm yöntemiyle alındı;
  o yöntem ölçüme kendi süresini de ekliyordu. "Sonra" değerleri her 6. pikseli örnekleyen hızlı yöntemle alındı. Aynı
  yeni ölçüm düzeltme öncesi koda uygulanamadı (eski pencere çok geç açıldığı için test zaman aşımına düştü). İlk
  açılıştaki farkın gerçek olduğu uygulama içi zaman damgalarıyla da görüldü (font çizimi 2,6 s).
- **Bellek:** Performans testinde private bellek ~90 MB'tan ~139 MB'a çıktı (sınır 250 MB). Kaynağı önceden çizilen
  emojiler ve hazır tutulan ikon penceresi.
- **Sınır:** Uygulama açıldıktan sonraki ~3,5 s içinde (ısınma sürerken) açılan ilk pencere biraz daha yavaş olabilir.
- **Ölçümler Sandbox'ta:** GPU yok, çizim yazılımla; gerçek bilgisayarda sayılar orantılı olarak daha küçüktür.
- **Test altyapısı:** UI test süreci artık "per-monitor DPI aware" (`DpiAwareness`,
  `tests/MyEverythingWidget.UiTests/Infrastructure/DpiAwareness.cs`). Sebep: Sandbox ekran ölçeği %100'den farklı
  olduğunda UI Automation koordinatları ile ekran görüntüsü koordinatları uyuşmuyordu; renk örnekleyen testler (kart
  rengi, sekme–zemin) hem eski hem yeni kodda düşüyordu.
- **Testler:** `TabAppearanceTests` 3/3. Tam UI suite'te 74 testten yalnız `IconDialog_OpensQuickly` düştü; ölçüm
  yöntemi düzeltilince geçti. Unit 293/293. Sonar bu turda çalıştırılamadı (IDE dosyaları tanımıyordu).
- **Dosya yolları:** Eski doküman dosya adı vermiyordu; Dosyalar satırları koddaki sınıf adlarından eklendi.

### Referanslar

- `questions/S06-ikon-penceresi-gecikmesi.md` → Cevap (A), Sonuç
- `PHASE13.md` (ikon penceresinin sekmeli düzeni)
- `MAIN_TODO.md` → 📊 Genel İlerleme → Faz 14

### Önceki doküman içeriği

> Önce: `PHASE13.md` · Karar: `questions/S06-ikon-penceresi-gecikmesi.md` (A)

---

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| A1 Sebebin ölçülmesi | 🟢 Tamamlandı | 14.2 |
| A2 İlk açılışın hızlanması | 🟢 Tamamlandı | 14.3 → Isınma |
| A3 Sonraki açılışların hızlanması | 🟢 Tamamlandı | 14.3 → Hafif hücreler, yeniden kullanım |

---

#### 14.1 İstek (birebir)

> o tab'ler sayfa açıldıktan yarım saniye filan sora geliyor. Bu da kullanıcı açısından akıcılık için kötü bir
> deneyim. Bunun sebebini tespit et ve fixle.

---

#### 14.2 Teşhis

Ölçümler Sandbox'ta yapıldı (GPU yok, çizim yazılımla). Ölçümde menüye tıklamakla pencerenin ekrana gelmesi
arasındaki süre ekran kareleri karşılaştırılarak bulundu; uygulama içine geçici zaman damgaları da kondu.

- **Gecikme nerede:**
  - Pencere sekmeleriyle birlikte tek seferde çiziliyor; sonradan değişen bir şey yok.
  - Gecikme, menü tıklaması ile pencerenin belirmesi arasında.
  - Ana penceredeki kategori sekmeleri ilk karede çiziliyor; sorun orada değil.
- **İlk açılış (3,3–3,6 s):**
  - Çoğu, renkli emoji fontunun (Segoe UI Emoji) ilk kez çizilmesi.
  - Emojiler arayüzde bir kez çizdirildiğinde arayüz iş parçacığı 2,6 s dondu.
  - Font dosyasını önceden okumak ve DirectWrite ile önceden yerleşim yaptırmak denendi; ikisi de etkisizdi (çizim
    maliyeti kaldı).
- **Sonraki açılışlar (0,5–0,8 s):**
  - Her açılışta yeni diyalog şablonu ve 56 tam `Button`'ın yerleşimi.
  - Ardından WinUI'nin açılış animasyonu.

---

#### 14.3 Çözüm

- **Hafif hücreler:** Emoji ızgarasında `Button` yerine `EmojiCell` kullanılıyor.
  - Hücre yuvarlak zeminli tek bir metin öğesi.
  - Üzerine gelince ve basınca zemin değişiyor.
  - Tıklama, Enter ve Boşluk ile seçiliyor; UI Automation'da "Button" olarak görünüyor ve Invoke destekliyor.
- **Isınma (`EmojiFontWarmUp`):**
  - Uygulama açıldıktan sonra emojiler görünmez bir katmanda, 60 ms aralıklarla birer birer çiziliyor.
  - Maliyet tek bir donma yerine küçük parçalara bölünüyor; açılışın ilk birkaç saniyesinde fark edilmiyor.
- **Yeniden kullanım:**
  - Isınma bitince ikon penceresi bir kez kuruluyor ve sonraki her açılışta aynı nesne kullanılıyor; şablon ve
    ızgara hazır kalıyor.
  - Her açılışta seçim, uyarı yazısı ve sekme ("Select icon") sıfırlanıyor.

---

#### 14.4 Kabul kriterleri ve testler

`TabAppearanceTests` (Sandbox).

| # | Kriter | Test |
|---|--------|------|
| A2 | Uygulama açıldıktan 4 s sonra ilk ikon penceresi tıklamadan sonra ≤ 1,2 s içinde ekranda | `IconDialog_OpensQuickly` |
| A3 | Sonraki üç açılışın ortancası ≤ 0,4 s | `IconDialog_OpensQuickly` |
| — | Pencere sekmeleri pencereyle birlikte çiziliyor (göründükten sonra ≤ 150 ms içinde son hallerinde) | `IconDialogTabs_AreDrawnWithTheDialog` |
| — | Kategori sekmeleri ana pencereyle birlikte çiziliyor | `CategoryTabs_AreDrawnWithTheWindow` |

---

#### 14.5 Sonuç

| Ölçüm (Sandbox) | Önce | Sonra |
|-----------------|------|-------|
| İlk açılış | 3645 ms | 382–625 ms |
| Sonraki açılışlar | 491 / 563 / 778 ms | 164 / 167 / 228 ms |

- **Ölçüm notu:** "Önce" sütunu, her karede tüm pencereyi piksel piksel karşılaştıran ilk ölçüm yöntemiyle alındı.
  - O yöntem ölçüme kendi süresini de ekliyordu.
  - "Sonra" sütunu, her 6. pikseli örnekleyen hızlı yöntemle alındı.
  - Aynı yeni ölçüm, düzeltme öncesi koda uygulanamadı: eski pencere çok geç açıldığı için test zaman aşımına düştü.
  - İlk açılıştaki farkın gerçek olduğu uygulama içi zaman damgalarıyla da görüldü (font çizimi 2,6 s).
- **Bellek:** Performans testinde private bellek ~90 MB'tan ~139 MB'a çıktı (sınır 250 MB). Bunun kaynağı
  önceden çizilen emojiler ve hazır tutulan ikon penceresi.
- **Sınır:** Uygulama açıldıktan sonraki ~3,5 s içinde (ısınma sürerken) açılan ilk pencere biraz daha yavaş olabilir.
- **Test altyapısı:**
  - UI test süreci artık "per-monitor DPI aware" (`DpiAwareness`).
  - Sebep: Sandbox ekran ölçeği %100'den farklı olduğunda, UI Automation koordinatları ile ekran görüntüsü
    koordinatları uyuşmuyordu. Renk örnekleyen testler (kart rengi, sekme–zemin) hem eski hem yeni kodda düşüyordu.
- **Testler:** `TabAppearanceTests` 3/3. Tam UI suite'te 74 testten yalnız `IconDialog_OpensQuickly` düştü; ölçüm
  yöntemi düzeltilince geçti. Unit 293/293. Sonar bu turda çalıştırılamadı (IDE dosyaları tanımıyordu).
