---
id: S1
status: open
decider:
priority: blocker
asked: 2026-10-30
---
# S1 — WinUI kodu hangi repoda duracak?

**Mevcut durum:** Bu repo (`MyEverythingWidget`) yalnız Python/PySide6 sürümünü içeriyor; WinUI sürümü için henüz bir yer yok.

**Soru:** WinUI sürümü yeni bir repoda mı, yoksa bu repoda mı yazılsın?

## Bağlam

- Faz 1'in ilk adımı solution yapısını oluşturmak, bu yüzden repo yeri baştan belli olmalı.
- TaskTimerWidget'ta eski sürüm aynı reponun `legacy/` klasöründe duruyor.
- Python sürümünün testleri ve `.dsl` dosyaları davranış şartnamesi olarak okunacak. Hangi seçenek olursa olsun
  bu dosyalar yeni test klasörüne kopyalanır.
- Ne olur: seçime göre kodun yolu, branch'i ve Store listelemesinde gösterilecek GitHub bağlantısı belirlenir.

## Seçenekler

### A — Bu repo, Python sürümü `legacy/` altına

```
MyEverythingWidget/
  legacy/        Python sürümü (models, services, widgets, window, tests)
  src/           WinUI sürümü
  tests/
  docs/
```

- ✅ Git geçmişi, MEW-1..MEW-3 dokümanları ve issue'lar tek yerde kalır.
- ✅ TaskTimerWidget ile aynı düzen.
- ❌ Python dosyalarının taşınması büyük bir diff üretir. Python sürümünün `.venv`, `pytest` yolları ve
  `CLAUDE.md` kuralları da güncellenmeli.

### B — Yeni repo ⭐ önerilen

- Yol örneği: `C:\Kodlar\MyEverythingWidget-WinUI`; GitHub adını sen belirlersin.
- Bu repo olduğu gibi kalır, sonradan arşivlenebilir.

- ✅ Temiz başlangıç: Python'a özgü `CLAUDE.md` kuralları, `.gitignore` ve yapı yeni projeyi karıştırmaz.
- ✅ Bu repoda hiçbir dosya taşınmaz.
- ❌ Git geçmişi ikiye ayrılır; eski dokümanlara bağlantıyla erişilir.
- ❌ GitHub'da yeni repoyu senin açman gerekir (ya da benim `gh repo create` ile açmama onay vermen).

## Öneri

**B** — Yeni yığının kendi kuralları ve yapısı olacak; Python repo düzeni ve kuralları ona yük olur.
Store'da yayınlanan TaskTimerWidget'tan bağımsız bir uygulama olduğu için ayrı repo daha temiz.

B seçilirse cevapta yolu ve repo adını yazman yeterli. Yazmazsan `C:\Kodlar\MyEverythingWidget-WinUI` kullanılır,
GitHub reposu açılmaz, yalnız yerel `git init` yapılır.

## Cevap

## Sonuç

Kullanıcı A'yı terminalde seçti; yeni branch açılması ve Python sürümünün `legacy/` altına konması istendi.
A uygulandı (2026-10-30).

- **Branch:** `feature/MEW-4-winui-rewrite` açıldı.
  - Taban `feature/MEW-3-drag-drop-grid-refactor`, master değil.
  - Sebep: MEW-3'te master'a girmemiş 78 commit var. `legacy/` en güncel Python kodunu içermeli.
- **Taşınanlar (`git mv`, commit yok):**

| Taşınan | Yeni yer |
|---------|----------|
| `main.py`, `requirements.txt`, `README.md` | `legacy/` |
| `models/`, `services/`, `widgets/`, `window/` | `legacy/` |
| `tests/` | `legacy/tests/` |

- **Yerinde kalanlar:** `docs/`, `LICENSE`, `.gitignore`, `CLAUDE.md`.
  - Kök `CLAUDE.md` Faz 1'de WinUI için yeniden yazılır.
- **Doğrulama:** Python unit testleri `legacy/` içinden çalıştırıldı.
  - Sonuç taşımadan önceki ile aynı: 170 geçti, 10 başarısız.
  - Başarısız 10 test taşımadan önce de başarısızdı.
- **Açık iş:** `legacy/tests/*.bat` dosyaları hâlâ `..\.venv` yolunu arıyor. Faz 1'de düzeltilecek
  (MAIN_TODO → Faz 1).
