# MEW-4 Faz 3 — Grid UI: sürükle-bırak ve boyutlandırma

> Önce: `PHASE2.md` · Sonra: `PHASE4.md` (Kategoriler)

## İçindekiler

- Durum Panosu
- 3.1 Kapsam
- 3.2 Yapı
- 3.3 Tasarım kararları
- 3.4 Testler
- 3.5 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `BoardViewModel`, `GridItemViewModel` | 🟢 Tamamlandı | |
| `WidgetGridView`, `GridCard` | 🟢 Tamamlandı | |
| Sürükleme, vurgu, animasyon, boyutlandırma, silme menüsü | 🟢 Tamamlandı | G1-G8, G10 |
| Durum çubuğu (InfoBar) | 🟢 Tamamlandı | Bozuk dosya, kaydetme hatası, yer yok |
| Sandbox koşucusunun sağlamlaştırılması | 🟢 Tamamlandı | 3.5.2 |

---

## 3.1 Kapsam

- Seçili kategorinin kartları sabit 5x5 grid üzerinde gösterilir.
- Kart sürüklenir, bırakılınca `GridLayout` kurallarıyla yerleşir; diğer kartlar animasyonla kayar.
- Kartın sağ alt köşesindeki tutamaçla boyut değişir.
- Sağ tık menüsünde "Delete" vardır.
- Hatalar ve uyarılar pencerenin altındaki durum çubuğunda görünür.

Kart ekleme (uygulama, not, resim) Faz 5 ve Faz 6'dadır; bu fazın testleri durumu doğrudan dosyaya yazarak başlar.

---

## 3.2 Yapı

| Tür | Katman | Görev |
|-----|--------|-------|
| `BoardViewModel` | Presentation | Kart listesi, `PreviewDrop`/`Drop`, `PreviewResize`/`Resize`, `Delete`, durum mesajı |
| `GridItemViewModel` | Presentation | Kartın konumu ve içeriği; aynı nesne yerinde güncellenir (animasyon için) |
| `WidgetGridView` | App | Kartları yerleştirir, pointer olaylarıyla sürükleme ve boyutlandırmayı yürütür |
| `GridCard` | App | Uygulama, not ve resim görünümü; boyutlandırma tutamacı |
| `GridMetrics` | App | 80 DIP hücre, 3 DIP kart boşluğu, hücre ↔ nokta dönüşümleri |
| `AutomationHost` | App | Görsel öğeleri (vurgu) UI Automation'a görünür yapar |

---

## 3.3 Tasarım kararları

Kullanıcı tasarım kararlarını ajana bıraktı (`MAIN_TODO.md` → Karar Panosu).

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Pencere boyutu | Sabit 412x560 DIP iç alan | Grid sabit 5x5; serbest boyut yalnız boşluk ya da kırpılma üretir |
| Sürükleme | Kartın kendisi imleçle taşınır, yarı saydam | G7: gerçek boyut, tutulan nokta korunur |
| Vurgu | Bırakılacak hücreler accent (izinli) ya da kırmızı (izinsiz) | G6, G8 |
| Bırakma | Kart bulunduğu yerden yeni hücresine 180 ms kayar; diğerleri de kayar | Akıcılık |
| Kart stili | Fluent kart: `CardBackgroundFillColorDefaultBrush`, 8 px köşe | Tema ile uyumlu, elle renk yok |
| İkonu olmayan uygulama | Accent renkte baş harf rozeti | Faz 5'te gerçek ikon gelir |
| Grid dışına bırakma | Mesaj gösterilmez, kart geri kayar | Vurgu zaten kırmızıydı |

---

## 3.4 Testler

| Kabul kriteri | Test |
|---------------|------|
| G1-G6 (mantık) | `Core.Tests` → `GridDslTests` (27 senaryo) |
| Vurgu, bırakma, mesajlar (mantık) | `Presentation.Tests` → `BoardViewModelTests` (15) |
| G1-G6 (gerçek fare) | `UiTests` → `GridInteractionTests.Scenario_ReplayedWithRealMouse_ProducesExpectedGrid` (6 senaryo) |
| G7, G8 | `UiTests` → `DraggedNote_KeepsItsSizeFollowsPointerAndHighlightsTwoCells` |
| G6 (görsel) | `UiTests` → `DraggingPastEdge_ShowsNotAllowedAndSnapsBack` |
| G10 | `UiTests` → `DraggingResizeHandle_GrowsNoteByOneColumn` |
| Silme menüsü | `UiTests` → `ContextMenuDelete_RemovesOnlyThatCard` |
| Bozuk dosya uyarısı | `UiTests` → `CorruptState_ShowsWarningInStatusBar` |
| Görsel inceleme | `UiTests` → `ScreenshotTests` (`results\shots\*.png`) |

Gerçek fareyle koşan senaryolar elle seçilmez: 5x5 olan ve yalnız `Drag` içeren her `.dsl` dosyası otomatik
olarak UI testine de dahil olur.

---

## 3.5 Sonuç

Faz 3 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`) | 99/99 |
| UI (Sandbox) | 20/20 |
| Sonar | 0 bulgu |

### 3.5.1 Bulunan ve düzeltilen sorunlar

- **`UserControl`'ler UI Automation ağacında görünmüyordu:**
  - Belirti: grid ve kartlar testlerde bulunamadı; ekran okuyucular için de görünmezlerdi.
  - Çözüm: `GridCard`, `WidgetGridView` ve `AutomationHost` kendi automation peer'larını oluşturuyor.
- **FlaUI faresi WinUI'da sürükleme üretmiyordu:**
  - Teşhis (sandbox içinde girdi günlüğü): basış geliyor, sonraki hareketler eski konumu bildiriyor, yakalama
    kayboluyordu.
  - Sebep: `Mouse.MoveTo` imleci `SetCursorPos` ile ışınlıyor.
  - Çözüm: testler `SendInput` ile gerçek fare olayları üreten `RealMouse` kullanıyor.
  - Uygulamada hata yoktu.
- **Grid 400 yerine 384 piksel genişliğindeydi:**
  - Sebep: pencere boyutu kenarlıklar dahil veriliyordu.
  - Çözüm: `AppWindow.ResizeClient` ile iç alan boyutu veriliyor.

### 3.5.2 Sandbox koşucusu

| Sorun | Çözüm |
|-------|-------|
| Küçültülmüş Sandbox penceresi fare girdisini iletmiyor | Pencere normal açılıp ekran dışına taşınıyor |
| Önceki sandbox kapanmadan yenisi başlarsa Sandbox "Uzak ortam oturumu kapatılıyor" hatasıyla açılamıyor ve kullanıcıdan "Kapat" bekliyor | Her koşudan önce süreçlerin bitmesi + 15 sn bekleniyor |
| Test 4 dakikada başlamazsa ya da sandbox erken kapanırsa betik 15 dakika bekliyordu | `started.txt` işareti; gelmezse sandbox kapatılıp bir kez yeniden deneniyor |
| Kapatma sırası | Önce pencere (`WindowsSandboxRemoteSession`), sonra sunucu |

Gecenin ilk koşularında kullanıcı ekranında bu hata kutusunu bir kez gördü; sebebi ve çözümü yukarıdadır.

### 3.5.3 Sonraki fazlara bırakılanlar

| Konu | Faz |
|------|-----|
| Karta tıklayınca uygulamayı açma (`ItemInvoked` olayı hazır) | Faz 5 |
| Not kartında Copy düğmesi ve düzenleme | Faz 6 |
| Klavye ile kart taşıma (erişilebilirlik) | Faz 8 |
