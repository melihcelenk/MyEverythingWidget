# Faz 2 — Task Timer: protokolle açılma, mesaj kanalı, hub varken görev çubuğundan çekilme

> **Durum:** 🟡 Kısmi (2.4'ün Sandbox UI testi Faz 3'te) · **Tamamlanma:** 90% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

Task Timer aile üyesi oldu. Hub onu bulabilir, açabilir ve ona mesaj gönderebilir. Hub çalışırken Task Timer görev
çubuğunda ayrı bir düğme olarak görünmez; hub kapanınca ya da çökünce açık kalır ve düğmesi geri gelir. Hub yokken
bugünkü gibi kendi düğmesiyle çalışır. İş TaskTimerWidget reposunda, `feature/MEW-5-widget-family` branch'inde.

## Problem

- **Gereksinim:** Görev çubuğu kalabalığı azalır; widget'lar ayrı ayrı düğme olarak görünmez.
- **Mevcut durum:** Task Timer her zaman kendi görev çubuğu düğmesiyle açılıyordu; dışarıdan açılma adresi, mesaj
  kanalı ve tek örnek kuralı yoktu (ikinci başlatma ikinci pencere açıyordu).

## Çözüm

- **Manifest:** Aile uzantısı (`tasktimer`, önerilen kenar sağ) ve `tasktimer-widget` protokolü.
- **Tek örnek:** `Program.cs` giriş noktası; ikinci başlatma çalışan örneğe yönlendirilir. Hub'dan gelen açma isteği
  pencereyi hub'ın yanına koyup öne getirir; Başlat menüsünden ikinci başlatma pencereyi öne getirir.
- **Kanal:** Ortak kütüphanenin `HubClient`'ı açılışta başlar ve hub'ı 2 saniyede bir arar.
- **Görev çubuğu:** Hub gelince görev çubuğundan çekilir. Hub kapanınca ya da çökünce (kanal kopar) Task Timer açık
  kalır, zamanlayıcı sayar ve görev çubuğu düğmesi geri gelir (S04 → A).
- **Yapı:** Aile davranışı WinUI'den bağımsız `Family/` klasöründe (`FamilyMembership`, `FamilyConnection`,
  `IFamilyWindow`); pencere tarafı `MainWindow.Family.cs`'te yalnız pencere işlemleri. Aile bağlantısı kurulamazsa
  Task Timer tek başına çalışmaya devam eder (hata loglanır).

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 2.1 | Task Timer manifestine aile uzantısı ve protokol eklenir. | 🟢 Tamamlandı |
| 2.2 | Task Timer protokolle açılır; zaten açıksa mevcut pencere öne gelir. | 🟢 Tamamlandı |
| 2.3 | Task Timer mesaj kanalını dinler ve gelen mesajlara göre davranır. | 🟢 Tamamlandı |
| 2.4 | Hub çalışırken Task Timer görev çubuğundan çekilir, hub gidince açık kalıp görev çubuğuna döner. | 🟡 Kısmi (davranış ve pipe testi tamam; iki paketli Sandbox UI testi Faz 3'te) |
| 2.5 | Faz 2'nin değişiklikleri ajan tarafından commit'lenip push edilir. | 🟢 Tamamlandı |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Hub kapanınca üyelere ne olacak? | A: açık kalır, görev çubuğuna döner | 🟢 Verildi (A) | S04 |

## Nasıl kontrol edilir

- [ ] `C:\Kodlar\TaskTimerWidget`'ta `dotnet test tests/TaskTimerWidget.Tests/TaskTimerWidget.Tests.csproj` 10 testle yeşil.
- [ ] Yalnız Task Timer açıkken görev çubuğunda onun düğmesi var (Faz 3'teki Sandbox testinde).
- [ ] MEW de açılınca Task Timer'ın düğmesi kaybolur; MEW kapanınca geri gelir (Faz 3'teki Sandbox testinde).

## Kalan

- **2.4:** Gerçek görev çubuğunda doğrulama hub gerektiriyor; MEW hub olunca (Faz 3) iki paket birlikte Windows
  Sandbox'ta test edilir. Task Timer'ın Store sürümü kullanıcının bilgisayarında kurulu olduğu için geliştirme paketi
  bu bilgisayara kurulmadı (aynı paket kimliği, kullanıcının verisi).

## Ayrıntılar

### 2.1 — Task Timer manifestine aile uzantısı ve protokol eklenir.

- **Mevcut durum:** Manifestte yalnız `runFullTrust` yetkisi vardı.
- **Problem:** Hub'ın Task Timer'ı bulması ve açması için manifest bildirimi gerekir.
- **Çözüm:** `windows.protocol` (`tasktimer-widget`) ve `windows.appExtension` (`com.melihcelenk.widgetfamily`, Id
  `tasktimer`, `Protocol`, `PreferredEdge=Right`). Uzantının `Public` klasörü pakete girer.
- **Dosyalar:** `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\Package.appxmanifest`,
  `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\Public\README.txt`, `TaskTimerWidget.csproj`
- **Testler:** `FamilyMembershipTests.ProtocolAndMemberId_MatchTheManifest` — koddaki protokol ve üye kimliği
  manifestle aynı.
- **Durum:** 🟢 Tamamlandı.

### 2.2 — Task Timer protokolle açılır; zaten açıksa mevcut pencere öne gelir.

- **Mevcut durum:** Yalnız Başlat menüsünden açılıyordu; ikinci başlatma ikinci pencere açıyordu.
- **Problem:** Hub'dan açılınca ikinci bir pencere oluşmamalı.
- **Çözüm:** `Program.cs` (`DISABLE_XAML_GENERATED_MAIN`): `AppInstance.FindOrRegisterForKey` ile tek örnek; ikinci
  başlatma `RedirectActivationToAsync` ile çalışan örneğe gider. Çalışan örnek `Activated` olayında açma isteğini
  `FamilyMembership.OnActivated`'a verir; açma isteği değilse pencereyi öne getirir. İlk açılış da protokolle olduysa
  aynı yoldan işlenir.
- **Dosyalar:** `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\Program.cs`, `App.xaml.cs`
- **Testler:** `OpenRequest_PlacesTheWindowAndBringsItToTheFront`, `OtherActivation_LeavesTheWindowWhereItIs`.
- **Durum:** 🟢 Tamamlandı.

### 2.3 — Task Timer mesaj kanalını dinler ve gelen mesajlara göre davranır.

- **Mevcut durum:** Kanal yoktu.
- **Problem:** Hub, çalışan Task Timer'a göster, gizle ve konum mesajları gönderebilmeli.
- **Çözüm:** `FamilyConnection`, ortak kütüphanenin `HubClient`'ını açılışta başlatır; olayları UI iş parçacığına
  taşıyıp `FamilyMembership`'e verir: `place` → hub'ın yanına taşı, `hide` / `show` → gizle / göster.
- **Dosyalar:** `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\Family\FamilyConnection.cs`, `FamilyMembership.cs`,
  `IFamilyWindow.cs`, `Views\MainWindow.Family.cs`
- **Testler:** `PlaceMessage_MovesTheWindowNextToTheHub`, `HideAndShowMessages_HideAndShowTheWindow`,
  `HubConnectionTests.HubPlaceMessage_ReachesTheWindow` (gerçek pipe).
- **Durum:** 🟢 Tamamlandı.

### 2.4 — Hub çalışırken Task Timer görev çubuğundan çekilir, hub gidince açık kalıp görev çubuğuna döner.

- **Mevcut durum:** Her zaman görev çubuğundaydı.
- **Problem:** Görev çubuğu kalabalığı.
- **Çözüm:** Hub gelince `AppWindow.IsShownInSwitchers = false`. Kanal kopunca (kapanma ya da çökme)
  `IsShownInSwitchers = true`; hub pencereyi gizlemişse yeniden gösterilir; zamanlayıcıya dokunulmaz. Hub yeniden
  gelince tekrar çekilir.
- **Dosyalar:** `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\Family\FamilyMembership.cs`,
  `Views\MainWindow.Family.cs`
- **Testler:**
  - Birim: `HubArriving_TakesTheWindowOffTheTaskbar`, `HubLeaving_BringsTheWindowBackToTheTaskbar_AndKeepsItOpen`,
    `HubLeavingWhileTheWindowWasHiddenByIt_ShowsTheWindowAgain`.
  - Gerçek pipe: `HubConnectionTests.Window_LeavesTheTaskbarWhileTheHubRuns_AndComesBackWhenItCloses`.
  - Bekleyen: Sandbox UI testi (MEW açıkken Task Timer düğmesi yok; MEW kapanınca ve süreci öldürülünce düğme geri
    gelir, zamanlayıcı sayıyor; MEW yeniden açılınca düğme yine kalkar). Hub gerektirdiği için Faz 3'te.
- **Durum:** 🟡 Kısmi.

### 2.5 — Faz 2'nin değişiklikleri ajan tarafından commit'lenip push edilir.

- **Mevcut durum:** Commit komutları kullanıcıya verilmişti.
- **Problem:** Gereksinim (T5): Ajanın commit ve push yetkisi var; komutlar kullanıcıya verilmez, ajan kendisi
  commit'leyip push eder.
- **Çözüm:** Task Timer `ff0f8de` ve MEW doküman commit'i ajan tarafından atılıp push edildi.
- **Dosyalar:** —
- **Testler:** —
- **Durum:** 🟢 Tamamlandı.

### Doğrulanmayan / dikkat edilmesi gereken

- Görev çubuğu ve Alt+Tab'dan gerçekten çekilme ve tek örnek yönlendirmesi henüz gerçek pakette denenmedi (Faz 3
  Sandbox testi).
- Task Timer'ın Windows App SDK 1.7'de kalması bu fazı engellemedi.
- Sonar bu repoyu tanımadığı için çalışmadı; derleme 0 uyarı, 0 hata.

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 2
- `C:\Kodlar\WidgetFamily\docs\CONTRACT.md`
