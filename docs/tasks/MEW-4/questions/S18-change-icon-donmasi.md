---
id: S18
status: resolved
decider:
priority: critical
asked: 2026-11-20
resolved: 2026-11-20
---
# S18 — "Change icon" ikinci kez açılınca uygulama donuyor: neyle devam edelim?

**Mevcut durum:** Store sürümü, web sitesi kartında "Change icon…" ikinci kez seçilince yanıt vermiyor; Sandbox'ta dört senaryoda yeniden üretilemedi.
**Soru:** İlk açılışta ne seçildiğini söyler misin, ve donmuş süreçten bellek dökümü (dump) almama izin verir misin?

## Bağlam

- Donan süreç hâlâ açık ve "Not responding" durumunda. Menü açık kalmış, "Change icon…" seçili görünüyor. Yani
  donma, menü öğesine tıklandıktan sonra ve pencere açılmadan önce oluyor.
- Kod incelemesinde UI iş parçacığını bekleten bir çağrı görünmüyor:
  - Pencere (`IconPickerDialog`) her pencere için bir kez kuruluyor ve tekrar kullanılıyor.
  - Kartın sitesi (`127.0.0.1:4178`) ikon isteğine hemen 404 dönüyor. Yani ağ beklemesi de yok.
- Sandbox testi `AppItemTests.IconDialog_OpensAgain_AfterItWasUsedOnce`, ilk seçimi "Reset to original", emoji ve
  "Browse… → vazgeç" yapıp pencereyi ikinci kez açtı. Üçünde de pencere açıldı ve uygulama yanıt verdi.
  - "Cancel" senaryosu ilk açılışta takıldı: menü hiç görünmedi. Bunun donmayla aynı şey olup olmadığı belli değil.
- Kesin sebebi en hızlı gösterecek kanıt, donmuş sürecin dökümü. Döküm, UI iş parçacığının nerede beklediğini
  gösterir. Bunun için `dotnet-dump` aracını kurup (`dotnet tool install -g dotnet-dump`) süreçten döküm almam
  gerekiyor; bu adım otomatik izin kontrolünde reddedildi.
- Döküm dosyası `tmp/hang/` altına yazılır (git'e girmez). Notların içeriği de dökümde bulunur; dosya
  bilgisayardan çıkmaz.

## Seçenekler

### A — Döküm al, ilk seçimi de söyle ⭐

Döküme izin verirsin (izin istemine onay ya da kurulum komutunu `!` ile kendin çalıştırırsın) ve ilk açılışta ne
yaptığını yazarsın: vazgeç, emoji, resim yapıştırma/sürükleme, Browse, Reset. Sebep kesin bulunur, test doğru
senaryoyla yazılır.

### B — Yalnız ilk seçimi söyle

Döküm alınmaz. O senaryoyu Sandbox testine ekleyip yeniden üretmeye çalışırım. Yeniden üretilemezse sebep tahmin
olarak kalır.

### C — Donmuş süreci kapat, sonra bakılsın

Süreç kapatılır, kanıt kaybolur. Soruşturma Sandbox denemeleriyle sürer.

## Öneri

A. Donma şu an elimizde. Döküm, tahmin yürütmeden sebebi gösterir. İlk seçim de testin hangi senaryoyu kuracağını
belirler.

## Cevap

## Sonuç

Döküm izni verildi (`/permissions`) ve donmuş süreçten döküm alındı (`tmp/hang/mew-hang.dmp`, git'e girmez).

- **Sebep:** UI iş parçacığı `IconPickerDialog.Reset()` içindeki `_iconTab.IsSelected = true` satırında, WinUI'nin
  `SelectorBarItem.IsSelected` ayarlayıcısının kendi kodunda dönüp duruyor. Süreç bir çekirdeği sürekli %100
  kullanıyor.
- **Tetikleyen:** Pencere bir kez açılıp "Select image" sekmesine geçildikten sonra Cancel ya da Esc ile kapatılıyor.
  Pencere tekrar kullanıldığı için, ikinci açılışta sekme, pencere ekranda değilken "Select icon"a geri alınmaya
  çalışılıyor ve WinUI burada takılıyor.
- **Kanıt:** Sandbox testi `AppItemTests.IconDialog_OpensAgain_AfterItWasUsedOnce`, `ImageTabThenCancel` ve
  `ImageTabThenEscape` senaryolarında ikinci açılışta uygulamayı aynı biçimde donduruyor. Diğer dört senaryo geçiyor.
- **Düzeltme önerisi:** S19.

Kontrol: uygulandı — döküm alındı, sebep dökümde ve Sandbox testinde görüldü; ilk seçimi sormaya gerek kalmadı.

