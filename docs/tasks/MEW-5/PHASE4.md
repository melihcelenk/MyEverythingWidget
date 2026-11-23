# Faz 4 — Birlikte hareket: hub sürüklenince üyeler kayar, tam ekranda birlikte gizlenir

> **Durum:** 🟢 Tamamlandı · **Tamamlanma:** 100% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

Simgeden açılan widget'lar simgeyle birlikte davranıyor. Simge sürüklenince onlar da aynı kenarda kalacak şekilde
kayıyor. Tam ekran bir video ya da oyun açılınca simgeyle birlikte gizleniyor, kapanınca birlikte geri geliyor.

## Problem

- **Gereksinim (T6):** İş bitene kadar sürdürülür ve testleri yapılır.
- **Mevcut durum:** Faz 3'ten sonra üye simgenin yanına yerleşiyordu; simge taşınınca yerinde kalıyordu. Tam ekranda
  simge gizleniyor (MEW-4, T132), yanındaki üye görünür kalıyordu.

## Çözüm

- **Hareket:** `FamilyMenuViewModel` simgeden açılan üyeleri ve kenarlarını hatırlar. Sürükleme bitince
  `FollowAsync` her birine yeni konumla `place` mesajı gönderir.
- **Tam ekran:** Simge gizlenince ve geri gelince `SetHiddenAsync` aynı üyelere `hide` / `show` gönderir.
- **Kapsam:** Yalnız simgeden açılan üyeler izlenir; kaldırılan ya da kenarını kaybeden üye bir sonraki menü
  açılışında listeden çıkar.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 4.1 | Hub sürüklenince yanına yerleşmiş üyeler de kayar. | 🟢 Tamamlandı |
| 4.2 | Tam ekranda üyeler hub'la birlikte gizlenir ve geri gelir. | 🟢 Tamamlandı (birim testleriyle) |

## Nasıl kontrol edilir

- [ ] Task Timer MEW simgesinin yanındayken simge sürüklenince Task Timer da kayıyor.
- [ ] Tam ekran video açılınca ikisi de gizleniyor, kapanınca ikisi de geri geliyor.

## Kalan

- Yok.

## Ayrıntılar

### 4.1 — Hub sürüklenince yanına yerleşmiş üyeler de kayar.

- **Mevcut durum:** Üye simgeden kopuk kalıyordu.
- **Problem:** Simge taşınınca üyenin de yanında kalması.
- **Çözüm:** Sürükleme bırakılınca (`OnCompactPointerReleased`) `MoveFamilyMembersAlong` → `FollowAsync`; mesajı
  `FamilyHubAdapter` hub üzerinden gönderir.
- **Dosyalar:** `src/MyEverythingWidget.Presentation/FamilyMenuViewModel.cs`, `src/MyEverythingWidget.Core/Family/FamilyServices.cs`
  (`IFamilyHub`), `src/MyEverythingWidget.App/FamilyHubAdapter.cs`, `MainWindow.Family.cs`, `MainWindow.xaml.cs`
- **Testler:** `MovingTheIcon_MovesTheOpenedMemberWithIt`, `MovingTheIcon_LeavesMembersThatWereNotOpenedFromIt`,
  `UninstalledMember_IsNoLongerFollowed`; Sandbox: `WidgetFamilyTests` (sürükleme adımı) yeşil.
- **Durum:** 🟢 Tamamlandı.

### 4.2 — Tam ekranda üyeler hub'la birlikte gizlenir ve geri gelir.

- **Mevcut durum:** Yalnız simge gizleniyordu (`FullScreenWatcher`).
- **Problem:** Üye tam ekranın üstünde kalabilirdi.
- **Çözüm:** `OnFullScreenChanged` → `HideFamilyMembers` → `SetHiddenAsync`.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`, `MainWindow.Family.cs`
- **Testler:** `HidingAndShowingTheIcon_HidesAndShowsTheOpenedMembers` (MEW), `HideAndShowMessages_HideAndShowTheWindow`
  ve `HubLeavingWhileTheWindowWasHiddenByIt_ShowsTheWindowAgain` (Task Timer).
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- 4.2 gerçek bir tam ekran uygulamasıyla iki paket birlikte denenmedi; zincirin iki ucu ayrı testlerde doğrulandı.
- Üye kullanıcı tarafından elle başka yere taşındıysa da simge sürüklenince yanına döner (üye konumunu hub'a
  bildirmiyor).

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 4
