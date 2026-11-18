# MEW-3: Bug Fixes - Swap Positioning & Test DSL

## Bug 1: 2x1 Note Swap Positioning Error (DEVAM EDİYOR)

**Problem:**

- 2x1 notu en sağ tarafa taşırken yanlış pozisyona gidiyor
- Beklenen yerin bir soluna yerleşiyor

**Durum:** Testler geçiyor ama gerçek uygulamada sorun devam ediyor.

---

## Yeni Gereksinim: Test DSL (Domain Specific Language)

**Amaç:** Grid testlerini okunabilir ve anlaşılır formatta yazmak.

### Önerilen Format

```
# Test: 2x1 Note swap with 1x1 App at right edge

Rows: 5
Columns: 5

InitialPosition:
A1 A2 A3 .  .
.  N1 N1 .  A4
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action: Drag(N1) from R2C2-R2C3 to R2C4-R2C5

ExpectedPosition:
A1 A2 A3 .  .
.  A4 .  N1 N1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
```

### Notasyon

| Sembol        | Anlamı           |
|---------------|------------------|
| `A1, A2, ...` | App shortcuts    |
| `N1, N2, ...` | Notes (text)     |
| `I1, I2, ...` | Images           |
| `.` veya `x`  | Boş hücre        |
| `N1 N1`       | 2x1 span (yatay) |
| `N1` üst üste | 1x2 span (dikey) |

### Action Formatları

```
Drag(ITEM) from R{row}C{col} to R{row}C{col}
Drag(N1) from R2C2 to R2C4
Move(A1) to R3C3
Delete(N1)
Resize(I1) to 2x2
```

### Implementasyon Planı

| # | Görev                                   | Durum |
|---|-----------------------------------------|-------|
| 1 | `GridTestDSL` parser sınıfı oluştur     | ⏳     |
| 2 | Grid state'i parse et (InitialPosition) | ⏳     |
| 3 | Action'ları parse et                    | ⏳     |
| 4 | ExpectedPosition ile karşılaştırma      | ⏳     |
| 5 | Mevcut testleri DSL formatına çevir     | ⏳     |
| 6 | Yeni swap bug testini DSL ile yaz       | ⏳     |

---

## Örnek Test Case'ler (DSL ile)

### Test 1: Simple Move

```
Rows: 3
Columns: 3

Initial:
A1 .  .
.  .  .
.  .  .

Action: Drag(A1) from R1C1 to R2C2

Expected:
.  .  .
.  A1 .
.  .  .
```

### Test 2: Swap 1x1 with 1x1

```
Rows: 3
Columns: 3

Initial:
A1 .  A2
.  .  .
.  .  .

Action: Drag(A1) from R1C1 to R1C3

Expected:
A2 .  A1
.  .  .
.  .  .
```

### Test 3: 2x1 Note to Right Edge (BUG CASE)

```
Rows: 5
Columns: 5

Initial:
.  .  .  .  .
N1 N1 .  .  A1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .

Action: Drag(N1) from R2C1-R2C2 to R2C4-R2C5

Expected:
.  .  .  .  .
A1 .  .  N1 N1
.  .  .  .  .
.  .  .  .  .
.  .  .  .  .
```

