# Faz 3 — Grid UI: sürükle-bırak ve boyutlandırma

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Bu fazda seçili kategorinin kartları pencerede sabit 5x5 grid üzerinde görünür oldu. Kart fareyle sürükleniyor;
bırakılacak hücreler izinliyse accent, izinsizse kırmızı vurgulanıyor ve bırakınca kart Faz 2'deki kurallarla yerine
kayıyor, yer değiştiren kartlar da animasyonla kayıyor. Kartın sağ alt köşesindeki tutamaçla boyut değişiyor, sağ tık
menüsünde "Delete" var; hatalar ve uyarılar pencerenin altındaki durum çubuğunda görünüyor.

## Problem

- Faz 2'deki grid kuralları ve durum yalnız Core'daydı; kullanıcı kartları göremiyor, taşıyamıyor ve
  boyutlandıramıyordu.
- Bozuk durum dosyası yedeği ve kaydetme hatası kullanıcıya gösterilmiyordu (Faz 2'den kalan).
- Gerçek fareyle sürükleme ilk kez bu fazda deneniyordu; UI testlerinin Sandbox'ta güvenilir koşması gerekiyordu.

## Çözüm

- **ViewModel (`BoardViewModel`, `GridItemViewModel`):** Kart listesi, bırakma ve boyutlandırma önizlemesi, silme ve
  durum mesajı; kart nesnesi yerinde güncellenir (animasyon için).
- **View (`WidgetGridView`, `GridCard`):** Kartları yerleştirir; pointer olaylarıyla sürükleme ve boyutlandırma;
  uygulama, not ve resim görünümü.
- **Etkileşim:** Kart imleçle yarı saydam taşınır, vurgu gösterilir, bırakınca 180 ms kayar; tutamaçla boyutlandırma;
  sağ tık "Delete".
- **Durum çubuğu (InfoBar):** Bozuk dosya, kaydetme hatası ve yer yok uyarıları.
- **Sandbox koşucusu:** Fare girdisi, art arda koşular ve takılan koşular için sağlamlaştırıldı.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 3.1 | `BoardViewModel` ve `GridItemViewModel` kartları ve grid işlemlerini yönetir. | 🟢 Tamamlandı |
| 3.2 | `WidgetGridView` ve `GridCard` kartları 5x5 grid üzerinde gösterir. | 🟢 Tamamlandı |
| 3.3 | Kart sürüklenir, vurgulanır, animasyonla yerleşir, boyutlandırılır ve silinir. | 🟢 Tamamlandı (G1-G8, G10) |
| 3.4 | Durum çubuğu hata ve uyarıları gösterir. | 🟢 Tamamlandı (bozuk dosya, kaydetme hatası, yer yok) |
| 3.5 | Sandbox koşucusu gerçek fare testleri için sağlamlaştırılır. | 🟢 Tamamlandı |

## Kararlar

<!-- Kullanıcı tasarım kararlarını ajana bıraktı (MAIN_TODO.md → Karar Panosu). -->

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Pencere boyutu ne olur? | Sabit 412x560 DIP iç alan | 🟢 Verildi (ajana bırakıldı) | Grid sabit 5x5; serbest boyut yalnız boşluk ya da kırpılma üretir |
| Sürüklenen kart nasıl görünür? | Kartın kendisi imleçle, yarı saydam | 🟢 Verildi (ajana bırakıldı) | G7: gerçek boyut, tutulan nokta korunur |
| Bırakılacak hücreler nasıl vurgulanır? | Accent (izinli) ya da kırmızı (izinsiz) | 🟢 Verildi (ajana bırakıldı) | G6, G8 |
| Bırakınca kart nasıl yerleşir? | 180 ms kayma; diğerleri de kayar | 🟢 Verildi (ajana bırakıldı) | Akıcılık |
| Kart stili ne olur? | Fluent kart: `CardBackgroundFillColorDefaultBrush`, 8 px köşe | 🟢 Verildi (ajana bırakıldı) | Tema ile uyumlu, elle renk yok |
| İkonu olmayan uygulama nasıl görünür? | Accent renkte baş harf rozeti | 🟢 Verildi (ajana bırakıldı) | Faz 5'te gerçek ikon gelir |
| Grid dışına bırakınca ne olur? | Mesaj yok, kart geri kayar | 🟢 Verildi (ajana bırakıldı) | Vurgu zaten kırmızıydı |

## Nasıl kontrol edilir

- [ ] Bir notu sürükle: not gerçek boyutunda, tutulduğu noktadan imleci izlemeli; bırakılacak iki hücre vurgulanmalı.
- [ ] Notu dolu bir hücreye bırak: oradaki kart animasyonla notun eski yerine kaymalı.
- [ ] Bir kartı grid'in kenarından dışarı sürükle: vurgu kırmızı olmalı; bırakınca kart eski yerine geri kaymalı.
- [ ] Notun sağ alt köşesindeki tutamacı bir hücre sağa sürükle: not bir sütun büyümeli.
- [ ] Bir karta sağ tıkla → "Delete": yalnız o kart silinmeli.
- [ ] Uygulama kapalıyken `state.json` dosyasını boz ve uygulamayı aç: altta durum çubuğunda uyarı görünmeli.

## Kalan

- Yok.

## Ayrıntılar

### 3.1 — `BoardViewModel` ve `GridItemViewModel` kartları ve grid işlemlerini yönetir.

- **Mevcut durum:** Grid işlemleri yalnız Core'daki `WidgetBoard`'daydı.
- **Problem:** View'ın bağlanacağı, WinUI'a bağımlı olmayan ve test edilebilen bir katman gerekiyordu.
- **Çözüm:**
  - `BoardViewModel` (Presentation): kart listesi, `PreviewDrop`/`Drop`, `PreviewResize`/`Resize`, `Delete`, durum
    mesajı.
  - `GridItemViewModel` (Presentation): kartın konumu ve içeriği; aynı nesne yerinde güncellenir (animasyon için).
- **Dosyalar:** `src/MyEverythingWidget.Presentation/BoardViewModel.cs`, `src/MyEverythingWidget.Presentation/GridItemViewModel.cs`
- **Testler:** `Presentation.Tests` → `BoardViewModelTests` (vurgu, bırakma, mesajlar; 15)
- **Durum:** 🟢 Tamamlandı.

### 3.2 — `WidgetGridView` ve `GridCard` kartları 5x5 grid üzerinde gösterir.

- **Mevcut durum:** Pencere boştu (Faz 1).
- **Problem:** Kartlar ekranda görünmeli ve UI Automation ile test edilebilmeliydi.
- **Çözüm:**
  - `WidgetGridView` kartları yerleştirir; `GridCard` uygulama, not ve resim görünümünü ve boyutlandırma tutamacını
    taşır.
  - `GridMetrics`: 80 DIP hücre, 3 DIP kart boşluğu, hücre ↔ nokta dönüşümleri.
  - `UserControl`'ler UI Automation ağacında görünmüyordu (testlerde bulunamıyor, ekran okuyuculara da
    görünmüyorlardı). `GridCard`, `WidgetGridView` ve `AutomationHost` kendi automation peer'larını oluşturuyor;
    `AutomationHost` görsel öğeleri (vurgu) UI Automation'a görünür yapıyor.
  - Grid 400 yerine 384 piksel genişliğindeydi, çünkü pencere boyutu kenarlıklar dahil veriliyordu; artık
    `AppWindow.ResizeClient` ile iç alan boyutu veriliyor.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/WidgetGridView.xaml`, `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`,
  `src/MyEverythingWidget.App/Views/GridCard.xaml`, `src/MyEverythingWidget.App/Views/GridCard.xaml.cs`,
  `src/MyEverythingWidget.App/Views/GridMetrics.cs`, `src/MyEverythingWidget.App/Views/AutomationHost.cs`
- **Testler:** `UiTests` → `ScreenshotTests` (görsel inceleme, `results\shots\*.png`)
- **Durum:** 🟢 Tamamlandı.

### 3.3 — Kart sürüklenir, vurgulanır, animasyonla yerleşir, boyutlandırılır ve silinir.

- **Mevcut durum:** Kartlarla etkileşim yoktu.
- **Problem:** G1-G8 ve G10 kabul kriterleri gerçek fareyle karşılanmalıydı.
- **Çözüm:**
  - Kart imleçle yarı saydam taşınır; bırakılınca `GridLayout` kurallarıyla yerleşir, diğer kartlar 180 ms kayar.
  - Vurgu: izinliyse accent, izinsizse kırmızı. Grid dışına bırakınca mesaj gösterilmez, kart geri kayar.
  - Sağ alt köşedeki tutamaçla boyut değişir; sağ tık menüsünde "Delete" vardır.
  - FlaUI faresi WinUI'da sürükleme üretmiyordu: `Mouse.MoveTo` imleci `SetCursorPos` ile ışınlıyordu (basış geliyor,
    sonraki hareketler eski konumu bildiriyor, yakalama kayboluyordu). Testler `SendInput` ile gerçek fare olayları
    üreten `RealMouse` kullanıyor; uygulamada hata yoktu.
  - 5x5 olan ve yalnız `Drag` içeren her `.dsl` dosyası otomatik olarak gerçek fareli UI testine de dahil olur.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/WidgetGridView.xaml.cs`, `src/MyEverythingWidget.App/Views/GridCard.xaml.cs`,
  `tests/MyEverythingWidget.UiTests/Infrastructure/RealMouse.cs`
- **Testler:**
  - `Core.Tests` → `GridDslTests` (G1-G6 mantık, 27 senaryo)
  - `UiTests` → `GridInteractionTests.Scenario_ReplayedWithRealMouse_ProducesExpectedGrid` (G1-G6 gerçek fare, 6 senaryo)
  - `UiTests` → `DraggedNote_KeepsItsSizeFollowsPointerAndHighlightsTwoCells` (G7, G8)
  - `UiTests` → `DraggingPastEdge_ShowsNotAllowedAndSnapsBack` (G6 görsel)
  - `UiTests` → `DraggingResizeHandle_GrowsNoteByOneColumn` (G10)
  - `UiTests` → `ContextMenuDelete_RemovesOnlyThatCard` (silme menüsü)
- **Durum:** 🟢 Tamamlandı (G1-G8, G10).

### 3.4 — Durum çubuğu hata ve uyarıları gösterir.

- **Mevcut durum:** `WidgetBoard.CorruptBackupPath` ve `WidgetBoard.SaveFailed` Faz 2'den hazırdı ama gösterilmiyordu.
- **Problem:** Kullanıcı bozuk dosya yedeğini, kaydetme hatasını ve yer olmadığını görmeliydi.
- **Çözüm:** Pencerenin altındaki durum çubuğu (InfoBar) bozuk dosya, kaydetme hatası ve yer yok uyarılarını gösterir.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml`, `src/MyEverythingWidget.Presentation/BoardViewModel.cs`
- **Testler:** `UiTests` → `CorruptState_ShowsWarningInStatusBar`; `Presentation.Tests` → `BoardViewModelTests` (mesajlar)
- **Durum:** 🟢 Tamamlandı.

### 3.5 — Sandbox koşucusu gerçek fare testleri için sağlamlaştırılır.

- **Mevcut durum:** Faz 1'deki koşucu fare kullanmayan testler içindi.
- **Problem:** Gerçek fare testleri ve art arda koşular Sandbox'ta takılıyordu.
- **Çözüm:**
  - Küçültülmüş Sandbox penceresi fare girdisini iletmiyor: pencere normal açılıp ekran dışına taşınıyor.
  - Önceki Sandbox kapanmadan yenisi başlarsa Sandbox "Uzak ortam oturumu kapatılıyor" hatasıyla açılamıyor ve
    kullanıcıdan "Kapat" bekliyor: her koşudan önce süreçlerin bitmesi + 15 sn bekleniyor.
  - Test 4 dakikada başlamazsa ya da Sandbox erken kapanırsa betik 15 dakika bekliyordu: `started.txt` işareti;
    gelmezse Sandbox kapatılıp bir kez yeniden deneniyor.
  - Kapatma sırası: önce pencere (`WindowsSandboxRemoteSession`), sonra sunucu.
  - Gecenin ilk koşularında kullanıcı ekranında bu hata kutusunu bir kez gördü; sebebi ve çözümü yukarıdadır.
- **Dosyalar:** `scripts/test-ui.ps1`
- **Testler:** UI (Sandbox) 20/20
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Kapsam:** Kart ekleme (uygulama, not, resim) Faz 5 ve Faz 6'da; bu fazın testleri durumu doğrudan dosyaya yazarak
  başlar.
- **Sonraki fazlara bırakılanlar:**
  - Karta tıklayınca uygulamayı açma (`ItemInvoked` olayı hazır) → Faz 5.
  - Not kartında Copy düğmesi ve düzenleme → Faz 6.
  - Klavye ile kart taşıma (erişilebilirlik) → Faz 8.
- **Sonuç:** Faz 3 tamamlandı (2026-10-30). Unit 99/99, UI (Sandbox) 20/20, Sonar 0 bulgu.

### Referanslar

- `MAIN_TODO.md` → Faz 3 — Grid UI: sürükle-bırak ve boyutlandırma
- `MAIN_TODO.md` → Karar Panosu (tasarım kararlarının ajana bırakılması)
- `PHASE2.md` → Faz 2 — Grid motoru (önceki faz) · `PHASE4.md` → Faz 4 — Kategoriler (sonraki faz)
- Önceki doküman içeriği aşağıdadır; oradaki bölüm numaraları (3.1 Kapsam … 3.5 Sonuç) eski numaralardır, yukarıdaki
  alt faz numaralarıyla aynı değildir.

### Önceki doküman içeriği

> Önce: `PHASE2.md` · Sonra: `PHASE4.md` (Kategoriler)

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `BoardViewModel`, `GridItemViewModel` | 🟢 Tamamlandı | |
| `WidgetGridView`, `GridCard` | 🟢 Tamamlandı | |
| Sürükleme, vurgu, animasyon, boyutlandırma, silme menüsü | 🟢 Tamamlandı | G1-G8, G10 |
| Durum çubuğu (InfoBar) | 🟢 Tamamlandı | Bozuk dosya, kaydetme hatası, yer yok |
| Sandbox koşucusunun sağlamlaştırılması | 🟢 Tamamlandı | 3.5.2 |

---

#### 3.1 Kapsam

- Seçili kategorinin kartları sabit 5x5 grid üzerinde gösterilir.
- Kart sürüklenir, bırakılınca `GridLayout` kurallarıyla yerleşir; diğer kartlar animasyonla kayar.
- Kartın sağ alt köşesindeki tutamaçla boyut değişir.
- Sağ tık menüsünde "Delete" vardır.
- Hatalar ve uyarılar pencerenin altındaki durum çubuğunda görünür.

Kart ekleme (uygulama, not, resim) Faz 5 ve Faz 6'dadır; bu fazın testleri durumu doğrudan dosyaya yazarak başlar.

---

#### 3.2 Yapı

| Tür | Katman | Görev |
|-----|--------|-------|
| `BoardViewModel` | Presentation | Kart listesi, `PreviewDrop`/`Drop`, `PreviewResize`/`Resize`, `Delete`, durum mesajı |
| `GridItemViewModel` | Presentation | Kartın konumu ve içeriği; aynı nesne yerinde güncellenir (animasyon için) |
| `WidgetGridView` | App | Kartları yerleştirir, pointer olaylarıyla sürükleme ve boyutlandırmayı yürütür |
| `GridCard` | App | Uygulama, not ve resim görünümü; boyutlandırma tutamacı |
| `GridMetrics` | App | 80 DIP hücre, 3 DIP kart boşluğu, hücre ↔ nokta dönüşümleri |
| `AutomationHost` | App | Görsel öğeleri (vurgu) UI Automation'a görünür yapar |

---

#### 3.3 Tasarım kararları

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

#### 3.4 Testler

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

#### 3.5 Sonuç

Faz 3 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`) | 99/99 |
| UI (Sandbox) | 20/20 |
| Sonar | 0 bulgu |

##### 3.5.1 Bulunan ve düzeltilen sorunlar

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

##### 3.5.2 Sandbox koşucusu

| Sorun | Çözüm |
|-------|-------|
| Küçültülmüş Sandbox penceresi fare girdisini iletmiyor | Pencere normal açılıp ekran dışına taşınıyor |
| Önceki sandbox kapanmadan yenisi başlarsa Sandbox "Uzak ortam oturumu kapatılıyor" hatasıyla açılamıyor ve kullanıcıdan "Kapat" bekliyor | Her koşudan önce süreçlerin bitmesi + 15 sn bekleniyor |
| Test 4 dakikada başlamazsa ya da sandbox erken kapanırsa betik 15 dakika bekliyordu | `started.txt` işareti; gelmezse sandbox kapatılıp bir kez yeniden deneniyor |
| Kapatma sırası | Önce pencere (`WindowsSandboxRemoteSession`), sonra sunucu |

Gecenin ilk koşularında kullanıcı ekranında bu hata kutusunu bir kez gördü; sebebi ve çözümü yukarıdadır.

##### 3.5.3 Sonraki fazlara bırakılanlar

| Konu | Faz |
|------|-----|
| Karta tıklayınca uygulamayı açma (`ItemInvoked` olayı hazır) | Faz 5 |
| Not kartında Copy düğmesi ve düzenleme | Faz 6 |
| Klavye ile kart taşıma (erişilebilirlik) | Faz 8 |

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 3 — Grid UI: sürükle-bırak ve boyutlandırma" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 99/99, UI 20/20 (Sandbox). Sonuç: `PHASE3.md` → 3.5 Sonuç.

**Özet:** Özel grid paneli ve kartlar; sürükleme görüntüsü, hücre vurgusu, animasyon, resize.

**Hedefler:**

- [x] `GridPanel` (K2) ve kart şablonları (uygulama, not, resim)
- [x] Sürükleme görüntüsü gerçek boyutta, imleç tutulan noktada (G7)
- [x] Hedef hücrelerin tamamı vurgulanıyor; geçersiz hedefte farklı vurgu (G8, G6)
- [x] Taşınan öğeler animasyonla kayıyor
- [x] Resize tutamacı, hücreye oturma (G10)
- [x] UI testi: `.dsl` senaryoları gerçek sürüklemeyle koşuyor (çalıştırma ortamı S2'ye bağlı)

**Detay:** `PHASE3.md`
