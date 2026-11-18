---
id: S13
status: answered
decider: user
priority: major
asked: 2026-11-18
---
# S13 — Repoyu halka açmadan önce hangi eksikleri tamamlayayım?

**Mevcut durum:** Repo gizli. README ve MIT lisansı var ama açık kaynak bir projede beklenen bazı dosya ve ayarlar eksik.

**Soru:** Aşağıdaki eksiklerden hangilerini yapayım?

## Bağlam

### Hazır olanlar

- **LICENSE (MIT):** Var. Yalnız bu branch'te var, `master`'da yok. Bu yüzden GitHub lisansı henüz tanımıyor; PR #1
  birleşince görünür.
- **README:** Özellikler, ekran görüntüleri, geliştirme komutları ve gizlilik politikası bağlantısı var.
- **Gizli bilgi:** Dosyalarda ve git geçmişinde yok. `.gitignore` gizli dosyaları, `tmp/`, `data/`, `.idea/` ve
  `TestResults/` klasörlerini dışarıda tutuyor.
- **Kişisel bilgi:** Commit'lerde yazar e-postası görünüyor (normal). Store manifestinde yayıncı adı olarak senin
  adın var; bu Store'da da herkese açık.

### Eksikler

| # | Eksik | Neden |
|---|-------|-------|
| 1 | README'de "(MEW-4)" gibi iç iş numarası | Dışarıdaki okur için anlamsız |
| 2 | `SECURITY.md` | Güvenlik açığının nereye bildirileceği; GitHub "Security policy" olarak gösterir |
| 3 | `CONTRIBUTING.md` | Nasıl derlenir, test edilir, PR açılır (eskisi yalnız `legacy/` altında) |
| 4 | GitHub Actions: derleme + unit testler | Her PR'da otomatik kontrol; README'ye durum rozeti |
| 5 | Repo açıklaması ve konu etiketleri (topics) | GitHub'da bulunabilirlik; şu an boş |
| 6 | `CODE_OF_CONDUCT.md` | Topluluk kuralı; GitHub "community standards" listesinde |
| 7 | Issue ve PR şablonları (`.github/`) | Gelen hata raporlarının düzenli olması |

**7 yapıldı (T29):** TaskTimerWidget'taki şablonlar uyarlandı (`.github/ISSUE_TEMPLATE/`): Bug Report, Feature
Request, boş issue kapalı ve "Questions & Discussions" bağlantısı. Bu bağlantının çalışması için repoda
**Discussions açılmalı**; şu an kapalı. Açmayı A ya da B'yi seçersen benim yapmamı (`gh` ile) ya da senin yapmanı
cevaba yazabilirsin; açılmayacaksa bağlantıyı kaldırırım.

UI testleri Windows Sandbox istediği için GitHub Actions'ta çalıştırılamaz; CI yalnız derleme ve unit testleri
(Core, Presentation, Infrastructure) çalıştırır.

## Seçenekler

### A — 1–5 ⭐

- README temizliği, `SECURITY.md`, `CONTRIBUTING.md`, CI (derleme + unit test, README rozeti), repo açıklaması ve
  etiketleri.
- Repo açıklaması ve etiketleri `gh` ile GitHub'a yazılır. Bu dışarıya giden bir değişiklik olduğu için metni
  önce sana gösteririm.

### B — Hepsi (1–7)

- A'ya ek olarak `CODE_OF_CONDUCT.md` (Contributor Covenant) ve PR şablonu (issue şablonları zaten eklendi).

### C — Yalnız 1–3

- Yalnız dosya düzenlemeleri; CI ve GitHub ayarları yok.

## Öneri

**A** — dışarıdan gelen ilk izlenimi ve katkıyı en çok etkileyenler bunlar. 6 ve 7 ilk katkılar gelince eklenebilir.
Repoyu halka açma (visibility) işini sen yaparsın; ben yapmam.

## Cevap

**B — Hepsi (1–7)**

## Sonuç

B uygulandı: dosyadaki eksiklerin hepsi eklendi. GitHub ayarları S14'te onayını bekliyor.

| # | Eksik | Yapılan |
|---|-------|---------|
| 1 | README | İç iş numarası kaldırıldı; CI ve lisans rozetleri, "Contributing" bölümü eklendi |
| 2 | `SECURITY.md` | Gizli bildirim formu, yanıt süresi, desteklenen sürüm, verinin nerede kaldığı |
| 3 | `CONTRIBUTING.md` | Derleme, testler (Sandbox dahil), kod kuralları, PR adımları |
| 4 | CI | `.github/workflows/ci.yml`: Windows'ta derleme ve unit testler; komutlar yerelde denendi (309 test geçti, UI testleri kendini atlıyor) |
| 5 | Açıklama ve etiketler | Metin S14'te; onaydan sonra uygulanacak |
| 6 | `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1, resmî metin; bildirim yolu gizli bildirim formu ve GitHub |
| 7 | Şablonlar | Issue şablonları (T29) ve `.github/pull_request_template.md` |

- **GitHub ayarları:** Discussions ve gizli güvenlik bildirimi (`SECURITY.md` bunu kullanıyor) S14'te soruldu.
- **Ayrıntı:** `PHASE17.md` → 17.8.
