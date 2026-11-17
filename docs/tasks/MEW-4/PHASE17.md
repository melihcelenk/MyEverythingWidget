# Faz 17 — Ayarlar penceresinin kenar boşluğu ve yayın hazırlığı

> **Durum:** 🟡 Devam ediyor · **Tamamlanma:** 25% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Ayarlar penceresi artık widget'ın iki yanından boşluk bırakıyor; aynı düzen bütün iletişim kutularına uygulandı. Widget
2 sütuna kadar küçültülse de içerik kırpılmıyor. Bu fazın kalan işi yayına hazırlık: `master`'a birleştirme, GitHub
README'si için kullanım senaryolarını anlatan ekran görüntüleri ve Store gönderimi.

## Problem

- Ayarlar penceresi widget'ın bütün genişliğini kaplıyordu; iki yanda hiç boşluk yoktu (T10).
- README'de ekran görüntüsü yok; UI testlerinin görüntüleri rastgele veriyle çekilmiş. Görüntüler kullanıcının "bunu
  bunun için kullanabilirim" diyeceği senaryoları göstermeli (T10).

## Çözüm

- **İletişim kutuları (`DialogSizing.FitToWindow`):**
  - Bütün iletişim kutuları pencereden iki yanda 12 piksel boşluk bırakıyor. En geniş hali penceredeki yer kadar
    oluyor; WinUI'nin 320 piksellik en küçük genişliği dar pencerede bu genişliğe iniyor.
  - Pencere 320 pikselden darsa iç boşluk 24 yerine 12 piksel oluyor.
- **Ayarlar içeriği:** Sabit 300 piksel genişlik kaldırıldı. RadioButton ve ToggleSwitch'in en küçük genişliği
  sıfırlandı, böylece metinler kırpılmak yerine alt satıra geçiyor. Anahtarın yazısı da "On/Off" oldu; önceden
  sistem dilinde ("Kapalı") görünüyordu.
- **Ekran görüntüleri:** Senaryolar ve çekim yolu S8'de soruldu.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 17.1 | Ayarlar ve diğer iletişim kutuları pencerenin iki yanından boşluk bırakır; dar pencerede içerik kırpılmaz. | 🟢 Tamamlandı |
| 17.2 | GitHub README'si kullanım senaryolarını gösteren ekran görüntüleriyle güncellenir. | ⏳ Bekliyor (S8) |
| 17.3 | Branch `master`'a birleştirilir (PR #1). | ⏳ Bekliyor (kullanıcı) |
| 17.4 | Store gönderimi için ekran görüntüleri ve paket hazırlanır. | ⏳ Bekliyor (S8, `PHASE8.md` → 8.6) |

## Nasıl kontrol edilir

- [ ] Widget'ı normal boyutta açıp ayarlara gir: pencerenin sağında ve solunda boşluk görünmeli.
- [ ] Widget'ı 2 sütuna küçültüp ayarlara gir: "Use Windows setting" alt satıra geçmeli, "Close" düğmesi tam görünmeli.
- [ ] "Add", not düzenleme ve ikon değiştirme pencerelerinde de iki yanda boşluk olmalı.

## Kalan

- **17.2, 17.4:** S8'in cevabını bekliyor.
- **17.3:** PR #1'i kullanıcı birleştirecek.

## Ayrıntılar

### 17.1 — Ayarlar ve diğer iletişim kutuları pencerenin iki yanından boşluk bırakır; dar pencerede içerik kırpılmaz.

- **Mevcut durum:** Ayarlar penceresi widget'ın kenarından kenarına uzanıyordu. WinUI iletişim kutuları en az 320
  piksel genişliğinde; widget ondan dar olunca kutu pencereye yapışıyordu.
- **Problem:** "Settings'te yanlarda boşluk yok."
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
- **Çözüm:** Senaryo listesi ve çekim yolu S8'de soruldu; cevaba göre yazılacak.
- **Durum:** ⏳ Bekliyor (S8).

### 17.3 — Branch `master`'a birleştirilir (PR #1).

- **Mevcut durum:** PR #1 açık.
- **Çözüm:** Kullanıcı inceleyip birleştirir.
- **Durum:** ⏳ Bekliyor (kullanıcı).

### 17.4 — Store gönderimi için ekran görüntüleri ve paket hazırlanır.

- **Mevcut durum:** Paket ve listeleme metni Faz 8'de hazırlandı; Store görüntüleri test verisiyle çekilmişti.
- **Çözüm:** 17.2'deki senaryolarla Store görüntüleri, son build'den paket; gönderim `PHASE8.md` → 8.6.
- **Durum:** ⏳ Bekliyor (S8).

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
