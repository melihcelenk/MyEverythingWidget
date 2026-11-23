# Faz 4 — Birlikte hareket: hub sürüklenince üyeler kayar, tam ekranda birlikte gizlenir

> **Durum:** ⏳ Bekliyor · **Tamamlanma:** 0% · **Efor:** tahmin yazılmadı · **Task:** MEW-5

Hub'ın yanına yerleşmiş widget'lar hub'la birlikte davranır. Hub sürüklenince onlar da kayar. Tam ekran bir video ya
da oyun açılınca hub'la birlikte gizlenir. Bu faz isteğe bağlıdır; Faz 3 bittikten sonra gerekip gerekmediğine
bakılır.

## Problem

- **Mevcut durum:** Faz 3'ten sonra üye hub'ın yanına yerleşir; ama hub taşınınca yerinde kalır.
- Tam ekranda hub gizleniyor (MEW-4, T132); yanındaki üye ise görünür kalabilir.

## Çözüm

- **Hareket:** Hub, konumu değişince yerleşik üyelere konum mesajı gönderir.
- **Tam ekran:** Hub gizlenince ve geri gelince üyelere gizle/göster mesajı gönderir.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 4.1 | Hub sürüklenince yanına yerleşmiş üyeler de kayar. | ⏳ Bekliyor (Faz 3) |
| 4.2 | Tam ekranda üyeler hub'la birlikte gizlenir ve geri gelir. | ⏳ Bekliyor (Faz 3) |

## Nasıl kontrol edilir

- [ ] Task Timer MEW simgesinin yanındayken simge sürüklenince Task Timer da kayıyor.
- [ ] Tam ekran video açılınca ikisi de gizleniyor, kapanınca ikisi de geri geliyor.

## Kalan

- **4.1, 4.2:** Faz 3'ü bekliyor; faz isteğe bağlı.

## Ayrıntılar

### 4.1 — Hub sürüklenince yanına yerleşmiş üyeler de kayar.

- **Mevcut durum:** —
- **Problem:** Üye hub'dan kopuk kalır.
- **Çözüm:** Hub'ın konum değişikliğinde yerleşik üyelere konum mesajı.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** Sandbox UI testi.
- **Durum:** ⏳ Bekliyor.

### 4.2 — Tam ekranda üyeler hub'la birlikte gizlenir ve geri gelir.

- **Mevcut durum:** Yalnız hub gizleniyor (`FullScreenWatcher`).
- **Problem:** Üye tam ekranın üstünde kalabilir.
- **Çözüm:** `OnFullScreenChanged` üyelere gizle/göster mesajı gönderir.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:** Sandbox UI testi.
- **Durum:** ⏳ Bekliyor.

### Doğrulanmayan / dikkat edilmesi gereken

- Yok.

### Referanslar

- `MAIN_TODO.md` → 🎯 Faz Özetleri → Faz 4
