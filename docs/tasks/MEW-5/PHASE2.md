# Faz 2 — Task Timer: protokolle açılma, mesaj kanalı, hub varken görev çubuğundan çekilme

> **Durum:** ⏳ Bekliyor · **Tamamlanma:** 0% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

Task Timer aile üyesi olur. Hub onu bulabilir, açabilir ve ona mesaj gönderebilir. Hub çalışırken Task Timer görev
çubuğunda ayrı bir düğme olarak görünmez. Hub yokken bugünkü gibi kendi düğmesiyle çalışır. İş
TaskTimerWidget reposunda, `feature/MEW-5-widget-family` branch'inde yapılır.

## Problem

- **Gereksinim:** Görev çubuğu kalabalığı azalır; widget'lar ayrı ayrı düğme olarak görünmez.
- **Mevcut durum:** Task Timer her zaman kendi görev çubuğu düğmesiyle açılıyor; dışarıdan açılma adresi ya da mesaj
  kanalı yok.

## Çözüm

- **Manifest:** Aile uzantısı bloğu ve protokol tanımı eklenir.
- **Açılma:** Protokolle açılır; zaten açıksa yeni pencere açılmaz, mevcut pencere öne gelir.
- **Kanal:** Ortak kütüphanenin mesaj kanalı sunucusu çalışır.
- **Görev çubuğu:** Hub gelince görev çubuğundan çekilir. Hub kapanınca ya da çökünce (kanal kopar) Task Timer açık
  kalır, zamanlayıcı sayar ve görev çubuğu düğmesi geri gelir (S04 → A).

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 2.1 | Task Timer manifestine aile uzantısı ve protokol eklenir. | ⏳ Bekliyor (Faz 1) |
| 2.2 | Task Timer protokolle açılır; zaten açıksa mevcut pencere öne gelir. | ⏳ Bekliyor (Faz 1) |
| 2.3 | Task Timer mesaj kanalını dinler ve gelen mesajlara göre davranır. | ⏳ Bekliyor (Faz 1) |
| 2.4 | Hub çalışırken Task Timer görev çubuğundan çekilir, hub gidince açık kalıp görev çubuğuna döner. | ⏳ Bekliyor (Faz 1) |

## Kararlar

| Karar | Öneri | Durum | Detay |
|-------|-------|-------|-------|
| Hub kapanınca üyelere ne olacak? | A: açık kalır, görev çubuğuna döner | 🟢 Verildi (A) | S04 |

## Nasıl kontrol edilir

- [ ] Yalnız Task Timer açıkken görev çubuğunda onun düğmesi var.
- [ ] MEW de açılınca Task Timer'ın düğmesi kaybolur.

## Kalan

- **2.1–2.4:** Faz 1'in sözleşmesini bekliyor.

## Ayrıntılar

### 2.1 — Task Timer manifestine aile uzantısı ve protokol eklenir.

- **Mevcut durum:** Manifestte yalnız `runFullTrust` yetkisi var.
- **Problem:** Hub'ın Task Timer'ı bulması ve açması için manifest bildirimi gerekir.
- **Çözüm:** Faz 1'de yazılan uzantı bloğu ve protokol eklenir.
- **Dosyalar:** `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\Package.appxmanifest`
- **Testler:** —
- **Durum:** ⏳ Bekliyor.

### 2.2 — Task Timer protokolle açılır; zaten açıksa mevcut pencere öne gelir.

- **Mevcut durum:** Yalnız Başlat menüsünden açılıyor.
- **Problem:** Hub'dan açılınca ikinci bir pencere oluşmamalı.
- **Çözüm:** Tek örnek (single instance) ve aktivasyon yönlendirmesi; adresteki kenar bilgisi okunur.
- **Dosyalar:** `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\App.xaml.cs`
- **Testler:** Adres çözümleme birim testi; Sandbox'ta iki kez açma.
- **Durum:** ⏳ Bekliyor.

### 2.3 — Task Timer mesaj kanalını dinler ve gelen mesajlara göre davranır.

- **Mevcut durum:** Kanal yok.
- **Problem:** Hub, çalışan Task Timer'a göster, gizle ve konum mesajları gönderebilmeli.
- **Çözüm:** Ortak kütüphanenin kanal sunucusu açılışta başlar.
- **Dosyalar:** Task Timer servis katmanı
- **Testler:** Mesaj işleme birim testleri.
- **Durum:** ⏳ Bekliyor.

### 2.4 — Hub çalışırken Task Timer görev çubuğundan çekilir, hub gidince açık kalıp görev çubuğuna döner.

- **Mevcut durum:** Her zaman görev çubuğunda.
- **Problem:** Görev çubuğu kalabalığı.
- **Çözüm:** Hub geldi mesajında `AppWindow.IsShownInSwitchers = false`. Hub gitti mesajında ya da kanal koptuğunda
  (çökme) `IsShownInSwitchers = true`; pencere ve zamanlayıcı olduğu gibi kalır. Hub yeniden gelince tekrar çekilir.
- **Dosyalar:** `C:\Kodlar\TaskTimerWidget\src\TaskTimerWidget\Views\MainWindow.xaml.cs`
- **Testler:** Sandbox UI testi: MEW açıkken Task Timer düğmesi yok; MEW kapanınca ve MEW süreci öldürülünce düğme
  geri gelir, Task Timer açık ve zamanlayıcı sayıyor; MEW yeniden açılınca düğme yine kalkar.
- **Durum:** ⏳ Bekliyor.

### Doğrulanmayan / dikkat edilmesi gereken

- Task Timer'ın Windows App SDK 1.7'de kalması bu fazı engellemez; güncelleme bu task için zorunlu değil.

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 2
