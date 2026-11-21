---
id: S20
status: answered
decider: user
priority: major
asked: 2026-11-21
---
# S20 — Dil listesi aşağı doğru, yeşil kartın altına kadar açılsın: nasıl yapalım?

**Mevcut durum:** Ayarlar'daki dil listesi yukarı doğru açılıp widget'ın dışına taşıyor.
**Soru:** Listeyi, aşağı açılan ve yeşil kartın alt kenarında biten kendi açılır listemizle değiştireyim mi?

## Bağlam

- **İstenen (T130):** Dil kutusuna tıklayınca liste aşağı açılmalı ve yeşil About kartının alt kenarına kadar
  uzanmalı.
- **Neden yukarı açılıyor:**
  - WinUI'nin `ComboBox`'ı listeyi, seçili satır kutunun tam üstüne gelecek biçimde konumluyor.
  - Seçili satır listenin ilk satırı ("Sistem dili") ve listede 16 satır var. Bu yüzden liste kutunun hizasından
    aşağı doğru başlamak yerine ekranda yer bulduğu yöne, yani yukarı uzanıyor.
  - Bu davranışın yönü ve yüksekliği `ComboBox`'ta ayarlanamıyor.
- **Etkilenen:** Yalnız Ayarlar'daki dil kutusu (`SettingsDialog.xaml` → `LanguageChoice`). Görünüşü aynı kalır; yalnız
  açılan listenin yeri ve boyu değişir.

## Seçenekler

### A — Kendi açılır listemiz: kutunun altından başlar, yeşil kartın altında biter ⭐

Kutu aynı görünür. Tıklayınca hemen altında, kutuyla aynı genişlikte bir liste açılır. Listenin boyu, kutunun altından
yeşil kartın alt kenarına kadar olan mesafe kadardır; sığmayan diller kaydırılarak görülür. Seçili dil işaretli ve
görünür olur. Test: listenin üst kenarı kutunun altında, alt kenarı kartın alt kenarında; widget küçültülse de
pencerenin dışına taşmaz.

### B — Menü olarak açılan düğme (`DropDownButton` + menü)

Aşağı açılır ama boyu Windows'un menü kuralına göre ekranın altına kadar uzar; yeşil kartın hizasında bitmez ve
seçili dil işaretli görünmez.

### C — ComboBox kalsın, listenin boyu kısaltılsın

`MaxDropDownHeight` ile liste kısalır ama yine seçili satıra göre konumlanır; yukarı açılma sorunu kalır.

## Öneri

A. İstenen davranışı birebir veren tek seçenek bu; görünüş değişmez.

## Cevap

**A — Kendi açılır listemiz: kutunun altından başlar, yeşil kartın altında biter**

## Sonuç

A uygulandı:

- **Liste:** `ComboBox` yerine aynı görünen bir düğme (`LanguageChoice`) ve onun altından açılan bir liste
  (`LanguageList`) var.
  - Liste düğmeyle aynı genişlikte. Yüksekliği, düğmenin altından yeşil kartın alt kenarına kadar hesaplanıyor.
  - Sığmayan diller kaydırılarak görülüyor; seçili dil işaretli ve görünür.
- **Test:** `LanguageAndSettingsTests.LanguageList_OpensDownwards_ToTheBottomOfTheAboutCard`. Listenin üstü düğmenin en
  fazla 8 piksel altında, altı kartın alt kenarına 8 piksel yakın, sol kenarı düğmeyle hizalı.
- **Sonuç:** Önce kırmızı (liste yoktu), sonra 18/18. İlk denemede düğme ile liste arası 9 pikseldi; listenin iç
  boşluğu 4'ten 2 piksele indi.

Kontrol: uygulandı — `SettingsDialog.xaml`'de `LanguageChoice` bir düğme ve altında `Placement="BottomEdgeAlignedLeft"`
bir liste; yükseklik `OnLanguageListOpening`'de kartın alt kenarına göre hesaplanıyor.

