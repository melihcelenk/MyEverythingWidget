---
id: S3
status: resolved
decider: user
priority: blocker
asked: 2026-10-30
resolved: 2026-11-18
---
# S3 — Canlıya alma ne anlama geliyor: master'a birleştirme mi?

**Mevcut durum:** Bütün iş `feature/MEW-4-winui-rewrite` dalında commit'li ve push'lu (`ed2fd84`); `master` hâlâ ilk sürümde (`ef9eed8`, MEW-1).

**Soru:** Canlıya alma talebiyle bu dalın `master`'a birleştirilmesini mi kastediyorsun, birleştirme nasıl olsun?

## Bağlam

- Canlıyı etkileyen işleri her zaman onaylatıyorum; ayrıca "canlı"nın bu repoda neye karşılık geldiği net değil.
- Dalın durumu:

| Konu | Durum |
|------|-------|
| `master`'da olmayan commit | 92: 78'i MEW-3 (Python sürümü, drag-drop/grid), 14'ü MEW-4 (WinUI) |
| Açık PR | Yok (ne MEW-3 ne MEW-4 için) |
| Testler | Unit 293/293, UI (Sandbox) 67/67 + 1, Sonar bulgu yok |
| Microsoft Store | Henüz gönderilmedi; Partner Center hesabı gerekiyor (`docs/general/STORE_SUBMISSION.md`) |

- MEW-4, MEW-3'ün üstüne açıldı. Bu yüzden MEW-4'ü `master`'a almak MEW-3'ün 78 commit'ini de getirir.
- Store'a gönderme bu oturumdan yapılamaz; kendi Partner Center hesabınla yapılır. Talepte sürüm (release) çıkarılması olarak
  anılan adım büyük olasılıkla bu.

## Seçenekler

### A — GitHub'da PR aç, sen birleştir ⭐

- `feature/MEW-4-winui-rewrite` → `master` PR'ı açılır; açıklamada fazlar ve test sonuçları olur.
- Birleştirmeyi sen GitHub'dan yaparsın (merge commit; 92 commit'in geçmişi korunur).

- ✅ Birleştirmeden önce değişikliklerin hepsini tek yerde görürsün.
- ✅ Geri dönülmesi zor adımı (master'ı değiştirmek) sen atarsın.
- ❌ Bir tık daha senin işin.

### B — PR aç ve ben birleştireyim

- PR açılır ve hemen `master`'a merge commit ile birleştirilir; dal silinmez.

- ✅ Senin bir şey yapman gerekmez.
- ❌ `master` gözden geçirilmeden değişir.

### C — "Canlı" başka bir şey (ör. Store'a gönderim, bir paket yayımlama)

- Neyi kastettiğini Cevap'a yaz; ona göre ilerlerim.

## Öneri

A: PR'ı açayım, birleştirmeyi sen yap. `master`'a 92 commit birden giriyor ve bunun geri dönüşü zahmetli. Release
için son kontroller ve Store paketi (`scripts/publish-msix.ps1`, `STORE_SUBMISSION.md`) PR'dan bağımsız ilerleyebilir.

## Cevap

**A — GitHub'da PR aç, sen birleştir**

## Sonuç

A uygulandı (2026-10-30):

- **PR açıldı:** https://github.com/melihcelenk/MyEverythingWidget/pull/1
  - Başlık: `[MEW-4] WinUI rewrite for the Microsoft Store`, `feature/MEW-4-winui-rewrite` → `master`.
  - Açıklamada özellikler, proje yapısı ve test planı var.
- **Birleştirmedim;** kararın gereği birleştirmeyi sen GitHub'dan yapacaksın.
- **Önerilen yöntem:** merge commit (92 commit'in geçmişi korunur).
- **Test planında açık iki madde:** iki ekranlı elle kontrol ve Partner Center gönderimi.

Kontrol: uygulandı — PR #1 açık (`feature/MEW-4-winui-rewrite` → `master`, OPEN, birleştirilmedi; birleştirme kullanıcıda).
