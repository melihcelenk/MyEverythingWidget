# MEW-4 Faz 2 — Grid motoru, durum ve kalıcılık (Core)

> Önce: `PHASE1.md` · Sonra: `PHASE3.md` (Grid UI: sürükle-bırak ve boyutlandırma)

## İçindekiler

- Durum Panosu
- 2.1 Kapsam
- 2.2 Grid modeli
- 2.3 Kurallar
- 2.4 DSL biçimi
- 2.5 Durum ve kalıcılık
- 2.6 Testler
- 2.7 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| 2.2 Grid modeli ve `GridLayout` | 🟢 Tamamlandı | |
| 2.4 C# DSL ayrıştırıcı ve `.dsl` testleri | 🟢 Tamamlandı | 22 senaryo |
| 2.5 `WidgetState`, `JsonWidgetStateStore`, `WidgetBoard` | 🟢 Tamamlandı | |

---

## 2.1 Kapsam

- Grid kurallarının tamamı UI'sız C# kodunda.
- Kategoriler, uygulamalar, notlar ve resimlerden oluşan uygulama durumu ve JSON kalıcılığı.
- Kategori işlemleri (ekle, yeniden adlandır, sil, sırala) Faz 4'te eklenir; bu fazda durum modelinde yerleri hazırdır.

---

## 2.2 Grid modeli

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

## 2.3 Kurallar

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

## 2.4 DSL biçimi

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

## 2.5 Durum ve kalıcılık

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

## 2.6 Testler

| Kabul kriteri | Test |
|---------------|------|
| G1-G6, G9, G10, K5 | `Core.Tests` → `GridDslTests` (her `.dsl` dosyası bir test) |
| `GridLayout` girdi doğrulaması | `Core.Tests` → `GridLayoutTests` |
| Durum kalıcılığı | `Core.Tests` → `JsonWidgetStateStoreTests` |
| `WidgetBoard` işlemleri ve kaydetme | `Core.Tests` → `WidgetBoardTests` |

---

## 2.7 Sonuç

Faz 2 tamamlandı (2026-10-30). Unit testler 79/79 geçiyor; Sonar bulgusu yok.

| Test grubu | Sayı |
|------------|------|
| `GridDslTests` (her `.dsl` bir test + klasör kontrolü) | 23 |
| `GridLayoutTests` | 9 |
| `GridScenarioParserTests` | 5 |
| `JsonWidgetStateStoreTests` | 5 |
| `WidgetBoardTests` | 18 |
| Faz 1 testleri (ayarlar, pencere konumu, ViewModel) | 19 |

### 2.7.1 Notlar

- Python'dan gelen üç senaryo (`2x1_note_right_edge`, `swap_note_and_app`, düzeltilmiş `create_app_and_note`) ilk
  denemede geçti.
- Ayar ve durum dosyaları artık ortak `AtomicJsonFile` kullanıyor; Faz 1'deki ayar testleri değişmeden geçti.
- Durum dosyasındaki bir kategorinin yerleşimi geçersizse (grid dışı, çakışma, span 1-3 dışı) dosya bozuk sayılır
  ve yedeklenir; uygulama boş durumla açılır ve yedeğin yolu `WidgetBoard.CorruptBackupPath`'te durur
  (kullanıcıya gösterimi Faz 3).
- Kaydetme hatası değişikliği geri almaz; `WidgetBoard.SaveFailed` olayı yükselir (kullanıcıya gösterimi Faz 3).
