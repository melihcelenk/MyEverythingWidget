---
id: S2
status: resolved
decider:
priority: critical
asked: 2026-10-30
resolved: 2026-11-17
---
# S2 — Gerçek fare kullanan UI testleri nerede koşsun?

**Mevcut durum:** Sürükle-bırak ve Ctrl+V'yi uçtan uca doğrulayan UI testleri, fareyi ve klavyeyi gerçekten kullanmak zorunda; bu testler koşarken bilgisayarı başka iş için kullanamazsın.

**Soru:** Bu testler senin masaüstünde mi, yoksa Windows Sandbox içinde mi koşsun?

## Bağlam

Testlerin çoğu fare kullanmaz:

| Test türü | Fare/klavye kullanır mı | Ne zaman koşar |
|-----------|-------------------------|----------------|
| Core `.dsl` testleri (grid kuralları) | Hayır | Her değişiklikte |
| ViewModel testleri | Hayır | Her değişiklikte |
| FlaUI tıklama/menü testleri (UI Automation ile) | Çoğunlukla hayır | Her faz sonunda |
| Gerçek sürükleme, Ctrl+V, ekran görüntüsü testleri | **Evet** | Her faz sonunda, toplam yaklaşık 1-3 dakika |

- Python sürümünde bu tür testlerin kullanıcıyı rahatsız ettiği ve bunun için ayrı bir "safety" mekanizması
  yazıldığı görülüyor (`tests/humanized/utils/safety.py`).
- O mekanizma da çalışmıyor; içinde "DISABLED: pynput listener causes hangs" notu var.
- Ne olur: seçim, işi sen yokken ne kadar ilerletebileceğimi belirler.

## Seçenekler

### A — Senin masaüstünde, uyarıyla

- Her koşudan önce bildirim gönderilir, test 10 saniye sonra başlar.
- Fare hareket ettirilirse test kendini durdurur.

- ✅ Ek kurulum yok.
- ❌ Sen bilgisayardayken her faz sonunda 1-3 dakika fareni kaptırırsın.
- ❌ Sen bilgisayardayken test yarıda kalırsa fazı kapatmak için tekrar koşmam gerekir.

### B — Windows Sandbox içinde ⭐ önerilen

- Uygulama paketi ve testler, Windows 11 Pro'nun yerleşik Windows Sandbox'ında açılan ayrı bir masaüstünde koşar.
- Sandbox her koşuda sıfırdan başlar.
- Sonuç ve ekran görüntüleri `tmp/` altına geri yazılır.

- ✅ Senin fare ve klavyene hiç dokunulmaz; sen çalışırken de testler koşabilir.
- ✅ Temiz bir Windows'ta test edilmiş olur. Bu, Store'a gönderimden önce kurulum sorunlarını da yakalar.
- ❌ "Windows Sandbox" özelliği kapalıysa bir kez açılması gerekir. Bu yönetici yetkisi ve yeniden başlatma
  ister; komutu ben veririm, sen çalıştırırsın.
- ❌ Bir koşu, sandbox açılışıyla birlikte yaklaşık 1-2 dakika uzar.
- ❌ Sandbox penceresi açılırken ekranda görünür ve odağı bir an alabilir.

Günlük işleyiş:

| Adım | Kim yapar | Ne sıklıkla |
|------|-----------|-------------|
| "Windows Sandbox" özelliğini açmak (yönetici + yeniden başlatma) | Sen | Bir kez |
| Sandbox'ı `.wsb` yapılandırmasıyla başlatmak, testleri koşturmak, sonucu okumak | Ajan | Her koşuda |
| Sandbox içine .NET runtime, Windows App SDK ve test sertifikasını kurmak | Ajan (`.wsb` içindeki betik) | Her koşuda, otomatik |

- Sandbox'ı başlatmak yönetici yetkisi istemez, bu yüzden her koşuyu ajan kendisi başlatır.
- Doğrulanacak risk: sandbox penceresi küçültülmüşken gerçek fare girdisi çalışmayabilir.
  - Faz 1'de ilk testle denenir.
  - Çalışmazsa pencere açık ama arka planda tutulur; o da olmazsa A'ya düşülür ve sana yazılır.

### C — Yalnız sen istediğinde

- Gerçek fare testleri otomatik koşmaz; yalnız sen UI testlerinin koşturulmasını istediğinde koşar.

- ✅ Hiç rahatsız edilmezsin.
- ❌ Sürükle-bırak gibi asıl riskli kısım, faz sonunda doğrulanmadan kalır. İşin kullanıcı olmadan yürütülmesi hedefine ters düşer.

## Öneri

**B** — Hem seni rahatsız etmiyor hem de fazları gerçek sürükleme testiyle kapatmamı sağlıyor. Sandbox
kullanılamazsa A'ya düşülür.

## Cevap

## Sonuç

Kullanıcı B'yi terminalde seçti (2026-10-30): testleri ajan çalıştıracağı için Windows Sandbox ile devam edilecek.
Beğenilmezse yeniden değerlendirilecek.

- Bir kerelik kurulum, yeniden başlatmadan önce kullanıcıda: "Windows Sandbox" özelliğinin açılması.
- Sandbox yapılandırması (`.wsb`) ve sandbox içi kurulum betiği Faz 1'de yazılır.
- Küçültülmüş pencerede fare girdisi riski Faz 1'in ilk UI testinde doğrulanır. Sonuç
  `PHASE1.md`'ye ve buraya yazılır.
