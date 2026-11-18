---
id: S14
status: open
decider:
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

## Sonuç
