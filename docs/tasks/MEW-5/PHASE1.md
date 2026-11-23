# Faz 1 — Ortak sözleşme: uzantı adı, protokol adresleri, mesajlar

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

Widget ailesinin ortak dili bu fazda belirlenir. Hub ile üyelerin birbirini nasıl bulduğu, birbirini nasıl açtığı ve
çalışırken hangi mesajları gönderdiği yazılır. Bunlar iki uygulamanın da kullanacağı küçük bir kütüphanede kodlanır.
Faz bitince ekranda bir şey değişmez; sonraki iki faz bu sözleşmenin üstüne kurulur.

## Problem

- **Gereksinim:** MEW ile Task Timer birlikte çalışabilir; ileride yazılacak başka widget'lar da aynı yapıya
  bağlanabilir.
- **Mevcut durum:** İki uygulama birbirinden habersiz. Ortak bir adres, mesaj ya da keşif yolu yok.

## Çözüm

- **Keşif:** Üye, kendi manifestinde bir uygulama uzantısı (App Extension) bloğu taşır. Blokta adı, simgesi, açılış
  protokolü ve önerdiği kenar (üst, sağ, alt, sol) yazar.
- **Açma:** Hub, üyeyi protokol aktivasyonuyla açar ve hangi kenara yerleşeceğini adreste bildirir.
- **Mesajlar:** Çalışan uygulamalar adlandırılmış kanal (named pipe) üzerinden sürümlü JSON mesajları gönderir:
  göster, gizle, konum, hub geldi, hub gitti.
- **Kod:** Ortak kütüphane .NET 8 hedefler; iki uygulama da kullanabilir. Yeni `WidgetFamily` reposunda durur ve
  iki uygulamaya `external/WidgetFamily` submodule'ü olarak eklenir (S02 → B; düzen: `MAIN_TODO.md` → Branch Bilgisi).

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 1.1 | Widget ailesiyle ilgili soru kartları MEW-5 altında toplanır. | 🟢 Tamamlandı |
| 1.2 | Task dokümanı ve faz dokümanları şablona getirilir. | 🟢 Tamamlandı |
| 1.3 | Hub rolü ve ortak kodun paylaşım yolu kararlaştırılır. | 🟢 Tamamlandı |
| 1.4 | Uzantı bloğu, protokol adresleri ve mesajlar sözleşme dokümanına yazılır. | 🟢 Tamamlandı |
| 1.5 | Ortak kütüphane yazılır ve birim testleriyle doğrulanır. | 🟢 Tamamlandı |
| 1.6 | `WidgetFamily` reposu açılır ve iki uygulamaya submodule olarak eklenir. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Ortak çatı yaklaşımı nasıl olacak? | A: ayrı uygulamalar, MEW hub | 🟢 Verildi (A) | S05 |
| Hub kim olacak? | A: MEW'in kompakt simgesi | 🟢 Verildi (A) | S01 |
| Ortak kod iki repoda nasıl paylaşılacak? | B: ayrı repo, git submodule | 🟢 Verildi (B) | S02 |

## Nasıl kontrol edilir

- [ ] `C:\Kodlar\WidgetFamily\docs\CONTRACT.md`'de uzantı bloğu, protokol adresi ve her mesajın örneği var.
- [ ] `C:\Kodlar\WidgetFamily`'de `dotnet test --solution WidgetFamily.slnx` 52 testle yeşil.

## Kalan

- Yok. WidgetFamily CI'ı yeşil.

## Ayrıntılar

### 1.1 — Widget ailesiyle ilgili soru kartları MEW-5 altında toplanır.

- **Mevcut durum:** Yaklaşım kartı MEW-4'te S24 olarak açılmıştı.
- **Problem:** Gereksinim (T1): Bu işle ilgili soru kartları MEW-5 altında toplanır.
- **Çözüm:** Kart `questions/S05-widget-ailesi-yaklasimi.md` olarak taşındı; ona giden bağlantılar güncellendi.
- **Dosyalar:** `questions/S05-widget-ailesi-yaklasimi.md`, `MAIN_TODO.md`, `WIDGET_FAMILY.md`, `questions/S01-hub-kim.md`
- **Testler:** —
- **Durum:** 🟢 Tamamlandı.

### 1.2 — Task dokümanı ve faz dokümanları şablona getirilir.

- **Mevcut durum:** Genel İlerleme tablosundaki fazların dokümanı yoktu.
- **Problem:** Gereksinim (T2): Faz tablosu şablona getirilir ve her fazın dokümanı yazılır.
- **Çözüm:** `PHASE1.md`–`PHASE4.md`, `MAIN_TODO.md`'deki faz özetlerinden yazıldı.
- **Dosyalar:** `PHASE1.md`, `PHASE2.md`, `PHASE3.md`, `PHASE4.md`
- **Testler:** `progress_table_check.py --check` (Lima bulgusu bu projede geçerli değil).
- **Durum:** 🟢 Tamamlandı.

### 1.3 — Hub rolü ve ortak kodun paylaşım yolu kararlaştırılır.

- **Mevcut durum:** S05 → A ile yaklaşım seçildi; hub'ın kim olacağı ve kodun nasıl paylaşılacağı açık.
- **Problem:** Sözleşme ve kütüphanenin yeri bu iki karara bağlı.
- **Çözüm:** S01 ve S02 kartları açıldı. S02 → B: ortak kod `WidgetFamily` reposunda, iki uygulamaya submodule.
  S01 → A: hub MEW'in kompakt simgesidir; ayrı bir başlatıcı uygulaması
  yapılmaz. Sözleşmede hub tarafı MEW, üye tarafı Task Timer ve sonraki widget'lardır.
- **Dosyalar:** `questions/S01-hub-kim.md`, `questions/S02-ortak-kod-paylasimi.md`
- **Testler:** —
- **Durum:** 🟢 Tamamlandı.

### 1.4 — Uzantı bloğu, protokol adresleri ve mesajlar sözleşme dokümanına yazılır.

- **Mevcut durum:** Mekanizmalar `WIDGET_FAMILY.md` → 3. bölümde seçilmişti, ayrıntı yoktu.
- **Problem:** Gereksinim (T3): Faz 1'e başlanır. İki uygulamanın aynı adları ve mesajları kullanması gerekir.
- **Çözüm:** Sözleşme sürüm 1 yazıldı:
  - **Keşif:** Uygulama uzantısı `com.melihcelenk.widgetfamily`; özellikler `Protocol` (zorunlu) ve `PreferredEdge`
    (yoksa `Right`). Kenar kuralı S03 → A.
  - **Açma:** `<protokol>:open?edge=right&anchor=sol,üst,genişlik,yükseklik` (fiziksel piksel).
  - **Kanal:** `WidgetFamily.Hub.v1.<oturum>` adlı pipe, yalnız aynı Windows kullanıcısı. Satır başına bir JSON;
    `hello`, `welcome`, `place`, `show`, `hide`. Başka sürüm, bilinmeyen tür ya da eksik alan yok sayılır.
  - **Hub gidince:** Bağlantı kopar, üye açık kalır ve görev çubuğuna döner (S04 → A).
  - **Değişiklik kuralı:** İsteğe bağlı alan aynı sürümde eklenir; başka her değişiklik sürümü yükseltir. Pipe adında
    sürüm olduğu için farklı sürümler birbirine bağlanmaz.
- **Dosyalar:** `C:\Kodlar\WidgetFamily\docs\CONTRACT.md`
- **Testler:** —
- **Durum:** 🟢 Tamamlandı.

### 1.5 — Ortak kütüphane yazılır ve birim testleriyle doğrulanır.

- **Mevcut durum:** Kod yoktu.
- **Problem:** Sözleşme iki tarafta tek kaynaktan gelmeli.
- **Çözüm:** .NET 8 hedefli, bağımlılıksız kütüphane:
  - `FamilyContract`: adlar ve pipe adı.
  - `FamilyMember`: manifest bildirimini okur.
  - `ActivationUri`: açma adresini kurar ve okur.
  - `Placement`: üyenin hub'ın yanındaki yerini hesaplar. Yer yoksa karşı kenara geçer, ekranın içine kaydırılır;
    ikinci monitör (negatif koordinat) desteklenir. Üye kendi boyutunu bildiği için hesap ortak kütüphanede; Faz 3'te
    MEW de aynısını kullanır.
  - `MessageCodec`: tek satır JSON, sürüm denetimiyle.
  - `HubServer` / `HubClient`: pipe'ın iki ucu. Üye hub'ı sürekli arar; hub gelince `HubArrived`, kapanınca ya da
    çökünce `HubLeft`. Aynı üye yeniden bağlanırsa yeni bağlantı geçerli olur.
- **Dosyalar:** `C:\Kodlar\WidgetFamily\src\WidgetFamily\` (`FamilyContract.cs`, `FamilyMember.cs`,
  `ActivationUri.cs`, `Placement.cs`, `Geometry.cs`, `FamilyMessage.cs`, `MessageCodec.cs`, `LineConnection.cs`,
  `HubServer.cs`, `HubClient.cs`, `EdgeText.cs`)
- **Testler:** `C:\Kodlar\WidgetFamily\tests\WidgetFamily.Tests\` — 52 test: mesaj gidiş-dönüş, başka sürüm,
  bilinmeyen tür, eksik alan, adres gidiş-dönüş ve bozuk adresler, dört kenarda yerleşim, ekran kenarında karşı kenara
  geçme, ikinci monitör, manifest okuma, gerçek pipe üzerinden: hub sonra açılınca bulunma, mesaj ulaşması, hub
  kapanınca `HubLeft`, hub geri gelince yeniden bulunma, üye ayrılınca hub'dan düşme, iki üyeye ayrı mesaj. Önce
  derleme hatasıyla kırmızı, sonra yeşil; üç ardışık koşuda 52/52.
- **Durum:** 🟢 Tamamlandı.

### 1.6 — `WidgetFamily` reposu açılır ve iki uygulamaya submodule olarak eklenir.

- **Mevcut durum:** Ortak repo yoktu.
- **Problem:** Gereksinim (S02 → B): Ortak kod ayrı repoda durur ve iki tarafa submodule olarak eklenir. GitHub'daki
  yapı, çok repolu projelerdeki anlaşılır düzenle kurulur.
- **Çözüm:** `C:\Kodlar\WidgetFamily` yerelde oluşturuldu (`git init`, branch `main`):
  - README'de aile tablosu, submodule ekleme ve `--recurse-submodules` ile klonlama.
  - `CHANGELOG.md` (`0.1.0`), MIT `LICENSE`, CI (`.github/workflows/ci.yml`).
  - Kendi `Directory.Build.props`, `Directory.Packages.props`, `global.json`, `.editorconfig`.

  Onaydan (T4) sonra yapılanlar:
  1. İlk commit `28af937`.
  2. `https://github.com/melihcelenk/WidgetFamily` açık repo olarak açıldı ve push edildi.
  3. MEW ve Task Timer'ın `feature/MEW-5-widget-family` branch'lerine `external/WidgetFamily` submodule'ü eklendi
     (`28af937`).
  4. İki uygulamanın README'sine "Widget family" bölümü ve `--recurse-submodules` komutu, MEW CI'ına
     `submodules: true` eklendi (Task Timer'da CI yok). Üç repoya `melihcelenk-widget-family` topic'i eklendi.

  5. `v0.1.0` etiketi `28af937`'ye atılıp push edildi (kullanıcı). Submodule'ler bu commit'te.

  6. MEW `39e5843` ve Task Timer `7ce1977` commit'leri `feature/MEW-5-widget-family` branch'lerine push edildi
     (kullanıcı). WidgetFamily CI'ı yeşil.
- **Dosyalar:** `C:\Kodlar\WidgetFamily\` (README, CHANGELOG, LICENSE, CI, props)
- **Testler:** İki uygulama submodule ile temiz klondan derlenir; CI yeşil.
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- Yok.

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 1
- `WIDGET_FAMILY.md` → 3. Kullanılabilecek Windows mekanizmaları
