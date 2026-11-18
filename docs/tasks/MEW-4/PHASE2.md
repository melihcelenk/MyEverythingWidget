# Faz 2 — Grid motoru, durum ve kalıcılık (Core)

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Bu fazda grid kurallarının tamamı UI'sız C# koduna (Core) yazıldı: öğe ekleme, taşıma, çarpışan öğelerin yer
değiştirmesi, boyutlandırma ve silme. Kategoriler, uygulamalar, notlar ve resimlerden oluşan uygulama durumu JSON
dosyasına güvenle kaydediliyor; dosya bozuksa yedekleniyor ve uygulama boş durumla açılıyor. Kullanıcı ekranda henüz
bir şey görmüyor; grid'in ekrana gelmesi Faz 3'te.

## Problem

- WinUI sürümünde grid kuralları ve uygulama durumu yoktu; Python sürümündeki davranışın aynısı UI'dan bağımsız,
  test edilebilir bir yerde gerekiyordu.
- Grid davranışının tek doğruluk kaynağı Python sürümündeki `.dsl` senaryolarıydı
  (`legacy/tests/humanized/drag/*.dsl`); C# tarafında bunları okuyup koşturan bir yol yoktu.
- Durum dosyası yazılırken kesilirse ya da elle bozulursa uygulamanın çökmemesi ve verinin kaybolmaması gerekiyordu.

## Çözüm

- **Grid modeli (`GridLayout`):** Değişmez yerleşim; her işlem yeni bir `GridLayout` döndürür, reddedilirse eski
  yerleşim aynen döner.
- **Kurallar:** Taşıma, çarpışma (atomik), ekleme, boyutlandırma ve silme `MEW-3` kuralları ve K5 kararıyla aynı.
- **DSL:** C# ayrıştırıcı Python sürümündeki `.dsl` biçimini okur; her `.dsl` dosyası bir test olarak koşar.
- **Durum (`WidgetState`, `JsonWidgetStateStore`):** `state.json`; atomik yazma ve bozuk dosya yedeği, ayarlarla
  ortak `AtomicJsonFile` ile.
- **`WidgetBoard`:** Durumu tutar, işlemleri `GridLayout` ile yapar, başarılıysa kaydeder.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 2.1 | Grid modeli ve `GridLayout` kuralları Core'da yazılır. | 🟢 Tamamlandı |
| 2.2 | C# DSL ayrıştırıcı `.dsl` senaryolarını test olarak koşturur. | 🟢 Tamamlandı (22 senaryo) |
| 2.3 | Uygulama durumu JSON dosyasına atomik olarak kaydedilir. | 🟢 Tamamlandı |
| 2.4 | `WidgetBoard` grid işlemlerini yapar ve başarılıysa durumu kaydeder. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- [ ] `dotnet test` çalıştır: Core ve Presentation testlerinin hepsi (79/79) geçmeli.
- [ ] `tests/Grid/` altına yeni bir `.dsl` senaryosu ekle ve `dotnet test` çalıştır: senaryo kendiliğinden yeni bir
  test olarak koşmalı.
- [ ] Uygulama kapalıyken veri klasöründeki `state.json` dosyasını boz ve uygulamayı aç: uygulama boş durumla açılmalı,
  bozuk dosyanın yedeği klasörde durmalı.

## Kalan

- Yok.

## Ayrıntılar

### 2.1 — Grid modeli ve `GridLayout` kuralları Core'da yazılır.

- **Mevcut durum:** Grid kuralları yalnız Python sürümündeydi.
- **Problem:** Kurallar UI'dan bağımsız ve test edilebilir olmalıydı.
- **Çözüm:**
  - Türler: `GridCell` (0 tabanlı satır ve sütun; `(1, 2)` = DSL'de `R2C3`), `GridSpan` (sütun ve satır, her biri
    1-3; `2x1` varsayılan not), `GridPlacement` (sol üst hücre + span), `GridSize` (uygulamada 5x5), `GridLayout`
    (öğe kimliği → yerleşim, değişmez), `GridOutcome` (`Success`, `OutOfBounds`, `NoRoom`, `GridFull`, `InvalidSpan`,
    `UnknownItem`).
  - `Move`: hedef grid dışına taşıyorsa `OutOfBounds`; hedef boşsa yalnız öğe taşınır; çarpışan her öğe (okuma
    sırasıyla) önce kaynağın sol üst hücresine, sığmıyorsa ilk boş uygun hücreye gider; biri hiçbir yere sığmıyorsa
    `NoRoom` ve hiçbir öğe değişmez (atomik).
  - "Boş" hesabında taşınan öğenin hedef hücreleri dolu, çarpışan öğelerin eski hücreleri boş sayılır; önce
    yerleştirilen çarpışan öğenin yeni hücreleri sonrakiler için doludur.
  - `Add`: ilk boş uygun hücre; yer yoksa `GridFull`. `Resize`: sol üst hücre sabit; span 1-3 değilse `InvalidSpan`,
    grid dışına taşarsa `OutOfBounds`, çakışırsa `NoRoom`. `Remove`: yalnız o öğe kalkar, boşluk dolmaz.
  - Kaynak: `docs/tasks/MEW-3/TODO.md` → "Temel Kurallar"; çoklu çarpışma için `MAIN_TODO.md` → Kararlar → K5.
- **Dosyalar:** `src/MyEverythingWidget.Core/Grid/GridTypes.cs`, `src/MyEverythingWidget.Core/Grid/GridLayout.cs`
- **Testler:** `Core.Tests` → `GridLayoutTests` (girdi doğrulaması, 9); kurallar `GridDslTests` ile (2.2).
- **Durum:** 🟢 Tamamlandı.

### 2.2 — C# DSL ayrıştırıcı `.dsl` senaryolarını test olarak koşturur.

- **Mevcut durum:** `.dsl` senaryoları yalnız Python testlerinde koşuyordu.
- **Problem:** Grid davranışının kaynağı `.dsl` dosyalarıydı; C# kodu aynı senaryolarla doğrulanmalıydı.
- **Çözüm:**
  - Biçim Python sürümündekiyle aynı (`Rows`, `Columns`, `Initial`, `Action`, `Expected`, isteğe bağlı `Outcome`);
    konumlar 1 tabanlı.
  - Eylemler: `Create(NOTE, "metin", N1)`, `Create(APP, "ad", A1)`, `Drag(N1, R2C4)`, `Resize(N1, 3x1)`, `Delete(N1)`.
  - Aynı kimlik dikdörtgen bir alanı dolduramazsa dosya hatalı sayılır.
  - Python'dan gelen üç senaryo (`2x1_note_right_edge`, `swap_note_and_app`, düzeltilmiş `create_app_and_note`) ilk
    denemede geçti.
- **Dosyalar:** `tests/Shared/GridDsl/GridScenario.cs`, `tests/Grid/*.dsl`
- **Testler:** `Core.Tests` → `GridDslTests` (her `.dsl` bir test + klasör kontrolü, 23; G1-G6, G9, G10, K5),
  `GridScenarioParserTests` (5).
- **Durum:** 🟢 Tamamlandı (22 senaryo).

### 2.3 — Uygulama durumu JSON dosyasına atomik olarak kaydedilir.

- **Mevcut durum:** Yalnız pencere ayarları kaydediliyordu (Faz 1).
- **Problem:** Kategoriler, uygulamalar, notlar ve resimler kalıcı olmalı; dosya bozulursa veri kaybolmamalı.
- **Çözüm:**
  - `Category` (`Id`, `Name`; sıra listedeki sıradır), `AppItem` (`Name`, `Target`, `LaunchKind`: `Executable`, `Url`,
    `Folder`; isteğe bağlı `IconPath`), `NoteItem` (`Text`), `ImageItem` (`ImagePath`, `PixelWidth`, `PixelHeight`),
    `WidgetState` (`SchemaVersion`, `Categories`, `Items`).
  - `JsonWidgetStateStore`: `state.json`; atomik yazma ve bozuk dosya yedeği. Ayar ve durum dosyaları ortak
    `AtomicJsonFile` kullanıyor; Faz 1'deki ayar testleri değişmeden geçti.
  - Bir kategorinin yerleşimi geçersizse (grid dışı, çakışma, span 1-3 dışı) dosya bozuk sayılır ve yedeklenir.
  - İlk açılışta tek kategori vardır: "General".
- **Dosyalar:** `src/MyEverythingWidget.Core/State/WidgetState.cs`, `src/MyEverythingWidget.Core/State/IWidgetStateStore.cs`,
  `src/MyEverythingWidget.Core/State/JsonWidgetStateStore.cs`, `src/MyEverythingWidget.Core/Storage/AtomicJsonFile.cs`
- **Testler:** `Core.Tests` → `JsonWidgetStateStoreTests` (5)
- **Durum:** 🟢 Tamamlandı.

### 2.4 — `WidgetBoard` grid işlemlerini yapar ve başarılıysa durumu kaydeder.

- **Mevcut durum:** Durum ile grid kurallarını birleştiren bir nesne yoktu.
- **Problem:** Ekle, taşı, boyutlandır ve sil işlemleri tek yerden yapılmalı ve kalıcı olmalıydı.
- **Çözüm:**
  - `WidgetBoard` durumu tutar; işlemleri `GridLayout` ile yapar, başarılıysa kaydeder.
  - Durum dosyası bozuksa uygulama boş durumla açılır; yedeğin yolu `WidgetBoard.CorruptBackupPath`'te durur.
  - Kaydetme hatası değişikliği geri almaz; `WidgetBoard.SaveFailed` olayı yükselir.
  - Kategori işlemleri (ekle, yeniden adlandır, sil, sırala) Faz 4'te; bu fazda durum modelinde yerleri hazır.
- **Dosyalar:** `src/MyEverythingWidget.Core/State/WidgetBoard.cs`
- **Testler:** `Core.Tests` → `WidgetBoardTests` (18)
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- **Kullanıcıya gösterim:** Bozuk dosya yedeği (`WidgetBoard.CorruptBackupPath`) ve kaydetme hatası
  (`WidgetBoard.SaveFailed`) bu fazda kullanıcıya gösterilmiyor; gösterimi Faz 3'te.
- **Sonuç:** Faz 2 tamamlandı (2026-10-30). Unit testler 79/79 (Faz 1'in 19 testi dahil) geçiyor; Sonar bulgusu yok.

### Referanslar

- `MAIN_TODO.md` → Faz 2 — Grid motoru, durum ve kalıcılık (Core)
- `MAIN_TODO.md` → 4. Kararlar → K5 (çoklu çarpışma)
- `docs/tasks/MEW-3/TODO.md` → Temel Kurallar
- `PHASE1.md` → Faz 1 — İskelet, pencere ve MSIX (önceki faz) · `PHASE3.md` → Faz 3 — Grid UI (sonraki faz)
- Önceki doküman içeriği aşağıdadır; oradaki bölüm numaraları (2.1 Kapsam … 2.7 Sonuç) eski numaralardır, yukarıdaki
  alt faz numaralarıyla aynı değildir.

### Önceki doküman içeriği

> Önce: `PHASE1.md` · Sonra: `PHASE3.md` (Grid UI: sürükle-bırak ve boyutlandırma)

#### Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| 2.2 Grid modeli ve `GridLayout` | 🟢 Tamamlandı | |
| 2.4 C# DSL ayrıştırıcı ve `.dsl` testleri | 🟢 Tamamlandı | 22 senaryo |
| 2.5 `WidgetState`, `JsonWidgetStateStore`, `WidgetBoard` | 🟢 Tamamlandı | |

---

#### 2.1 Kapsam

- Grid kurallarının tamamı UI'sız C# kodunda.
- Kategoriler, uygulamalar, notlar ve resimlerden oluşan uygulama durumu ve JSON kalıcılığı.
- Kategori işlemleri (ekle, yeniden adlandır, sil, sırala) Faz 4'te eklenir; bu fazda durum modelinde yerleri hazırdır.

---

#### 2.2 Grid modeli

| Tür | Anlamı | Örnek |
|-----|--------|-------|
| `GridCell` | Bir hücre; satır ve sütun 0 tabanlı | `(1, 2)` = DSL'de `R2C3` |
| `GridSpan` | Kaç sütun ve satır kapladığı, her biri 1-3 | `2x1` = 2 sütun, 1 satır (varsayılan not) |
| `GridPlacement` | Sol üst hücre + span | `(1,2) 2x1` → `(1,2)` ve `(1,3)` |
| `GridSize` | Grid boyutu | Uygulamada 5x5 |
| `GridLayout` | Bir kategorinin öğe kimliği → yerleşim eşlemesi; değişmez (immutable) | |
| `GridOutcome` | İşlem sonucu | `Success`, `OutOfBounds`, `NoRoom`, `GridFull`, `InvalidSpan`, `UnknownItem` |

Her işlem yeni bir `GridLayout` döndürür; işlem reddedilirse eski yerleşim aynen döner.

---

#### 2.3 Kurallar

Kaynak: `docs/tasks/MEW-3/TODO.md` → "Temel Kurallar"; çoklu çarpışma için `MAIN_TODO.md` → Kararlar → K5.

```
Move(öğe, hedef)
  hedef grid dışına taşıyor ──────────────> OutOfBounds, değişiklik yok
  hedefte başka öğe yok ──────────────────> yalnız öğe taşınır
  hedefte öğe(ler) var
     her çarpışan öğe için (okuma sırasıyla: satır, sonra sütun)
        kaynağın sol üst hücresine sığıyor mu? ──> oraya
        sığmıyorsa ilk boş uygun hücre ─────────> oraya
        hiçbir yere sığmıyor ───────────────────> NoRoom, HİÇBİR öğe değişmez (atomik)
```

- "Boş" hesaplanırken taşınan öğenin hedef hücreleri dolu sayılır.
- Çarpışan öğelerin eski hücreleri boş sayılır; çünkü onlar da taşınıyor.
- Önce yerleştirilen çarpışan öğenin yeni hücreleri sonrakiler için doludur.
- `Add`: ilk boş uygun hücre; yer yoksa `GridFull`.
- `Resize`: sol üst hücre sabit kalır. Span 1-3 değilse `InvalidSpan`, grid dışına taşarsa `OutOfBounds`, başka
  öğeyle çakışırsa `NoRoom`.
- `Remove`: yalnız o öğe kalkar; diğerleri yerinde kalır (boşluk dolmaz).

---

#### 2.4 DSL biçimi

Python sürümündeki biçimle aynıdır (`legacy/tests/humanized/drag/*.dsl`); konumlar 1 tabanlıdır.

```
Rows: 5
Columns: 5

Initial:
.  .  .  .  .
N1 N1 .  .  A1

Action:
# comment
Drag(N1, R2C4)

Expected:
.  .  .  .  .
A1 .  .  N1 N1

Outcome: Success
```

| Eylem | Anlamı |
|-------|--------|
| `Create(NOTE, "metin", N1)` | 2x1 not ekler |
| `Create(APP, "ad", A1)` | 1x1 uygulama ekler |
| `Drag(N1, R2C4)` | Öğeyi sol üst hücresi R2C4 olacak şekilde bırakır |
| `Resize(N1, 3x1)` | Span'i değiştirir (sütun x satır) |
| `Delete(N1)` | Öğeyi kaldırır |

- `Outcome:` isteğe bağlıdır; verilirse son eylemin sonucunu doğrular.
- Aynı kimlik dikdörtgen bir alanı doldurmalıdır; dolduramazsa dosya hatalı sayılır.

---

#### 2.5 Durum ve kalıcılık

| Tür | İçerik |
|-----|--------|
| `Category` | `Id`, `Name` (sıra listedeki sıradır) |
| `AppItem` | `Name`, `Target`, `LaunchKind` (`Executable`, `Url`, `Folder`), `IconPath` (isteğe bağlı) |
| `NoteItem` | `Text` |
| `ImageItem` | `ImagePath`, `PixelWidth`, `PixelHeight` |
| `WidgetState` | `SchemaVersion`, `Categories`, `Items` |
| `JsonWidgetStateStore` | `state.json`; atomik yazma, bozuk dosya yedeği (`AtomicJsonFile` ile ayarlarla ortak) |
| `WidgetBoard` | Durumu tutar; ekle/taşı/boyutlandır/sil işlemlerini `GridLayout` ile yapar, başarılıysa kaydeder |

İlk açılışta tek kategori vardır: "General".

---

#### 2.6 Testler

| Kabul kriteri | Test |
|---------------|------|
| G1-G6, G9, G10, K5 | `Core.Tests` → `GridDslTests` (her `.dsl` dosyası bir test) |
| `GridLayout` girdi doğrulaması | `Core.Tests` → `GridLayoutTests` |
| Durum kalıcılığı | `Core.Tests` → `JsonWidgetStateStoreTests` |
| `WidgetBoard` işlemleri ve kaydetme | `Core.Tests` → `WidgetBoardTests` |

---

#### 2.7 Sonuç

Faz 2 tamamlandı (2026-10-30). Unit testler 79/79 geçiyor; Sonar bulgusu yok.

| Test grubu | Sayı |
|------------|------|
| `GridDslTests` (her `.dsl` bir test + klasör kontrolü) | 23 |
| `GridLayoutTests` | 9 |
| `GridScenarioParserTests` | 5 |
| `JsonWidgetStateStoreTests` | 5 |
| `WidgetBoardTests` | 18 |
| Faz 1 testleri (ayarlar, pencere konumu, ViewModel) | 19 |

##### 2.7.1 Notlar

- Python'dan gelen üç senaryo (`2x1_note_right_edge`, `swap_note_and_app`, düzeltilmiş `create_app_and_note`) ilk
  denemede geçti.
- Ayar ve durum dosyaları artık ortak `AtomicJsonFile` kullanıyor; Faz 1'deki ayar testleri değişmeden geçti.
- Durum dosyasındaki bir kategorinin yerleşimi geçersizse (grid dışı, çakışma, span 1-3 dışı) dosya bozuk sayılır
  ve yedeklenir; uygulama boş durumla açılır ve yedeğin yolu `WidgetBoard.CorruptBackupPath`'te durur
  (kullanıcıya gösterimi Faz 3).
- Kaydetme hatası değişikliği geri almaz; `WidgetBoard.SaveFailed` olayı yükselir (kullanıcıya gösterimi Faz 3).

### MAIN_TODO'dan taşınan notlar

> Bu fazın `MAIN_TODO.md` → "Faz 2 — Grid motoru, durum ve kalıcılık (Core)" bölümünde duran özet ve hedef listesi, olduğu gibi buraya taşındı.

**Durum:** 🟢 Tamamlandı (2026-10-30). Unit 79/79. Sonuç: `PHASE2.md` → 2.7 Sonuç.

**Özet:** Sürükle-bırak kurallarının tamamı UI'sız C# kodunda, `.dsl` testleriyle.

**Hedefler:**

- [x] Modeller: Category, AppItem, NoteItem, ImageItem; ortak `GridPlacement` (satır, sütun, span)
- [x] C# DSL ayrıştırıcı ve test üreteci (Python biçimiyle birebir uyumlu, 1 tabanlı konum)
- [x] `GridEngine`: G1-G6, G9, G10 ve K5
- [x] Mevcut üç `.dsl` + her kriter için yeni senaryolar geçiyor (K4'teki düzeltmeyle)
- [x] `StateStore`: versiyonlu JSON şeması, atomik yazma, bozuk dosya davranışı

**Detay:** `PHASE2.md`
