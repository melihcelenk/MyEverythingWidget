---
id: S14
status: answered
decider: user
priority: major
asked: 2026-11-18
---
# S14 — GitHub ayarları: aşağıdaki metin ve ayarlarla uygulayayım mı?

**Mevcut durum:** S13 → B dosyaları eklendi; repo açıklaması, etiketler, Discussions ve gizli güvenlik bildirimi GitHub'da henüz ayarlı değil.

**Soru:** Aşağıdaki dört ayarı bu haliyle `gh` ile uygulayayım mı?

## Bağlam

Bu ayarlar dosya değil, GitHub'daki repo ayarları; o yüzden uygulamadan önce onayını istiyorum. Repo şu an gizli,
yani halka açılana kadar kimse görmez.

| # | Ayar | Değer | Neden |
|---|------|-------|-------|
| 1 | Açıklama | A small Windows widget that keeps your apps, websites, notes and pictures one click away. | Repo sayfasının üstünde ve aramalarda görünür |
| 2 | Etiketler (topics) | `windows`, `widget`, `desktop-widget`, `winui3`, `windows-app-sdk`, `dotnet`, `csharp`, `launcher`, `productivity`, `microsoft-store` | GitHub'da bulunabilirlik |
| 3 | Discussions | Açık | Issue şablonundaki "Questions & Discussions" bağlantısı buraya gidiyor |
| 4 | Gizli güvenlik bildirimi (private vulnerability reporting) | Açık | `SECURITY.md` ve `CODE_OF_CONDUCT.md` bildirimi bu forma yönlendiriyor |

## Seçenekler

### A — Dördünü de bu haliyle uygula ⭐

- `gh repo edit` ile açıklama, etiketler ve Discussions; `gh api` ile gizli güvenlik bildirimi açılır.

### B — Değiştirerek uygula

- Cevaba neyi değiştireceğimi yaz (açıklama metni, etiket listesi, hangi ayarların açılmayacağı).

## Öneri

**A** — dördü de yeni eklenen dosyaların (issue şablonu, `SECURITY.md`, `CODE_OF_CONDUCT.md`) çalışması için
gerekli; açıklama ve etiketler repoyu bulunabilir yapıyor.

## Cevap

**A — Dördünü de bu haliyle uygula**

## Sonuç

A uygulandı; dört ayarın üçü yapıldı, biri repo halka açılınca yapılabiliyor.

| # | Ayar | Durum |
|---|------|-------|
| 1 | Açıklama | Uygulandı (`gh repo edit`) |
| 2 | Etiketler | Uygulandı: on etiketin hepsi |
| 3 | Discussions | Açıldı |
| 4 | Gizli güvenlik bildirimi | Yapılamadı: GitHub bu özelliği yalnız herkese açık repolarda sunuyor, repo şu an gizli (`gh api` 404 döndü) |

- **4 için:** Repo halka açıldıktan sonra açılmalı. İki yol var:
  - GitHub'da **Settings → Code security → Private vulnerability reporting → Enable**.
  - Ya da şu komut: `gh api -X PUT repos/melihcelenk/MyEverythingWidget/private-vulnerability-reporting`.
- **Etkisi:** O zamana kadar `SECURITY.md` ve `CODE_OF_CONDUCT.md`'deki form bağlantısı çalışmaz. Repo gizli olduğu
  için şu an kimse görmüyor.
- **Ayrıntı:** `PHASE17.md` → 17.8.

Kontrol: uygulanmadı — 4. ayar (gizli güvenlik bildirimi) uygulanamıyor: GitHub bu özelliği yalnız herkese açık repolarda sunuyor, repo gizli (`gh api …/private-vulnerability-reporting` 404); diğer üçü uygulandı (`gh repo view`: açıklama, 10 etiket, Discussions açık). Repo halka açılınca açılmalı (PHASE17 17.8).

Repo halka açıldıktan sonra (2026-11-18) 4. ayar da açıldı: `gh api -X PUT …/private-vulnerability-reporting` →
`{"enabled":true}`. Aynı anda GitHub Pages da `master` / kök dizinden açıldı (17.12, Website bağlantısı).

Kontrol: uygulandı — dört ayarın dördü de açık: açıklama, 10 etiket, Discussions (`gh repo view`) ve gizli güvenlik bildirimi (`gh api …/private-vulnerability-reporting` → `{"enabled":true}`).
