# MEW-4 Faz 14 — İkon penceresinin geç açılması

> Önce: `PHASE13.md` · Karar: `questions/S06-ikon-penceresi-gecikmesi.md` (A)

## İçindekiler

- Durum Panosu
- 14.1 İstek (birebir)
- 14.2 Teşhis
- 14.3 Çözüm
- 14.4 Kabul kriterleri ve testler
- 14.5 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| A1 Sebebin ölçülmesi | 🟢 Tamamlandı | 14.2 |
| A2 İlk açılışın hızlanması | 🟢 Tamamlandı | 14.3 → Isınma |
| A3 Sonraki açılışların hızlanması | 🟢 Tamamlandı | 14.3 → Hafif hücreler, yeniden kullanım |

---

## 14.1 İstek (birebir)

> o tab'ler sayfa açıldıktan yarım saniye filan sora geliyor. Bu da kullanıcı açısından akıcılık için kötü bir
> deneyim. Bunun sebebini tespit et ve fixle.

---

## 14.2 Teşhis

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

## 14.3 Çözüm

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

## 14.4 Kabul kriterleri ve testler

`TabAppearanceTests` (Sandbox).

| # | Kriter | Test |
|---|--------|------|
| A2 | Uygulama açıldıktan 4 s sonra ilk ikon penceresi tıklamadan sonra ≤ 1,2 s içinde ekranda | `IconDialog_OpensQuickly` |
| A3 | Sonraki üç açılışın ortancası ≤ 0,4 s | `IconDialog_OpensQuickly` |
| — | Pencere sekmeleri pencereyle birlikte çiziliyor (göründükten sonra ≤ 150 ms içinde son hallerinde) | `IconDialogTabs_AreDrawnWithTheDialog` |
| — | Kategori sekmeleri ana pencereyle birlikte çiziliyor | `CategoryTabs_AreDrawnWithTheWindow` |

---

## 14.5 Sonuç

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
