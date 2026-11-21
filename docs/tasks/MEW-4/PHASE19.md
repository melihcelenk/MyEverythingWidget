# Faz 19 — Store gönderiminin otomatikleştirilmesi

> **Durum:** ⏸️ Ertelendi · **Tamamlanma:** 0% · **Efor:** kullanıcı için yaklaşık 20 dakika · **Task:** MEW-4

Güncellemeleri Store'a Claude'un tek komutla gönderebilmesi için senin bir kez yapman gereken adımlar. Önce Partner
Center'da bir "Entra uygulaması" ve onun anahtarı oluşturulur, sonra anahtar bilgisayarına kaydedilir.

> ⚠️ **Hesap riski (T141):** Partner Center hesabı kişisel Microsoft hesabıyla (Gmail) açık. Kullanıcı yönetimine girmek
> için "Sign in with Microsoft Entra ID" istiyor; bu, Partner Center hesabını bir Entra kiracısına bağlıyor. Bağlantı
> Microsoft'un tarafında kaydedildiği için tarayıcı değiştirmek ya da InPrivate pencere kullanmak bu riski kaldırmıyor.
> Daha önce tarayıcı değiştirince bile kişisel hesaba geçilememesi bununla uyumlu. Bu adım, Microsoft destekten
> (Partner Center → Help + support) kişisel hesabın etkilenmeyeceği teyit edilmeden atılmamalı.

## Problem

- **Gereksinim (T135, T140):** Store'a gönderim otomatikleşir. Kullanıcının bir kez yapacağı adımlar Türkçe, adım adım
  ve alt fazlara bölünmüş olarak yazılır.
- **Gereksinim (T137):** Daha önce Entra'ya girişte kişisel hesaba aylarca geçilemediği için bu riske girilmez; adımlar
  riski azaltacak biçimde yazılır ve iş şimdilik ertelenir.
- **Mevcut durum:** Her güncellemede paketleri Partner Center'a sen yüklüyorsun.

## Çözüm

- **Kurulum:** Aşağıdaki 19.1–19.5'i sen bir kez yaparsın.
- **Sonrası:** Her güncellemede sürümü yükseltmek, paketleri oluşturmak, Store'a gönderip sertifikasyona vermek ve
  GitHub release'ini yayınlamak Claude'da (19.6).
- **Anahtar:** Yalnız senin bilgisayarında, Windows Kimlik Bilgisi Yöneticisi'nde durur; sohbete ve repoya girmez.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 19.1 | Hazırlık: Microsoft destekten kişisel hesabın etkilenmeyeceği teyit edilir; adımlar InPrivate pencerede yapılır. | ⏸️ Ertelendi |
| 19.2 | Partner Center'da Entra uygulaması "Manager" rolüyle oluşturulur. | ⏸️ Ertelendi |
| 19.3 | Uygulamaya anahtar eklenir; Client ID, Tenant ID ve anahtar not edilir. | ⏸️ Ertelendi |
| 19.4 | Seller ID alınır. | ⏸️ Ertelendi |
| 19.5 | Store aracı kurulur ve bilgiler ona verilir. | ⏸️ Ertelendi |
| 19.6 | İlk güncelleme otomatik gönderilir (Claude). | ⏸️ Ertelendi |

## Nasıl kontrol edilir

- `msstore apps list` komutu My Everything Widget'ı listeler.
- İlk otomatik gönderimden sonra Partner Center'da yeni gönderim "In certification" görünür.
- Normal tarayıcında kişisel hesabınla Partner Center'a ve Outlook'a girebiliyorsun.

## Kalan

- Kurulum, kullanıcının kararıyla ertelendi (T137). Uygulama sayısı ve güncellemeler artınca yeniden ele alınacak.
- Anahtarın bir bitiş tarihi var. O tarihten önce 19.3 ve 19.5 tekrarlanır.

## Ayrıntılar

### 19.1 — Hazırlık: Microsoft destekten kişisel hesabın etkilenmeyeceği teyit edilir; adımlar InPrivate pencerede yapılır.

- **Mevcut durum:** Kişisel hesap (Gmail adresi) normal tarayıcıda açık.
- **Problem:** Kişisel e-posta bir Entra kiracısına eklenirse `ad_gmail.com#EXT#@<kiracı>.onmicrosoft.com` gibi ikinci
  bir kimlik oluşur. Giriş ekranı o kimliği seçmeye devam edebilir.
- **Çözüm:**
  1. **Önce destekten teyit al:** Partner Center → **Help + support** üzerinden şunu sor: "Kişisel Microsoft hesabıyla
     açılmış bireysel geliştirici hesabıma Store gönderim API'si için bir Microsoft Entra kiracısı bağlamak, kişisel
     hesabımla girişimi etkiler mi; güvenli yol hangisi?" Cevap gelmeden 19.2'ye geçme.
  2. Teyit gelirse adımları Edge'de **Ctrl+Shift+N** ile açılan InPrivate pencerede yap. Bu tek başına riski
     kaldırmaz, yalnız tarayıcıdaki oturumların karışmasını önler.
  3. Kişisel e-postanı hiçbir zaman kiracıya davet etme ya da "iş veya okul hesabı" olarak seçme.
  4. Bir ekran kişisel e-postanı iş/okul hesabı olarak göstermeye başlarsa dur ve ekran görüntüsünü gönder.
- **Dosyalar:** -
- **Testler:** -
- **Durum:** ⏸️ Ertelendi.

### 19.2 — Partner Center'da Entra uygulaması "Manager" rolüyle oluşturulur.

- **Mevcut durum:** Partner Center hesabında Entra uygulaması yok.
- **Problem:** Store'a programla gönderim, Partner Center'da yetkili bir uygulama ister.
- **Çözüm:**
  1. InPrivate pencerede https://partner.microsoft.com adresine kişisel hesabınla gir.
  2. Sağ üstteki **dişli** → **Account settings** → **User management** → **Microsoft Entra applications**.
  3. Hesap bir Entra kiracısına bağlı değilse Partner Center önce bunu ister. **"Create a new Microsoft Entra tenant"**
     seçeneğini seç; yeni kiracı kendi yönetici hesabıyla (`admin@<yeni-ad>.onmicrosoft.com`) oluşur. Mevcut bir
     kiracıya kişisel e-postanla bağlanma seçeneğini seçme. Bu yönetici hesabının şifresini kaydet.
  4. **Create Microsoft Entra application** → ad: `MEW Store publishing` → rol: **Manager** → **Save**.
- **Dosyalar:** -
- **Testler:** Uygulama listede "Manager" rolüyle görünür.
- **Durum:** ⏸️ Ertelendi.

### 19.3 — Uygulamaya anahtar eklenir; Client ID, Tenant ID ve anahtar not edilir.

- **Mevcut durum:** Uygulamanın anahtarı yok.
- **Problem:** Araç, Store'a bu anahtarla bağlanıyor.
- **Çözüm:**
  1. Listeden `MEW Store publishing`'i aç → **Keys** → **Add new key**.
  2. Ekranda çıkan **Client ID**, **Tenant ID** ve **Key** değerlerini hemen bir parola yöneticisine kaydet. Anahtar
     bir daha gösterilmiyor.
  3. Anahtarın **bitiş tarihini** de not et.
- **Dosyalar:** -
- **Testler:** -
- **Durum:** ⏸️ Ertelendi.

### 19.4 — Seller ID alınır.

- **Mevcut durum:** -
- **Problem:** Araç, hangi Partner Center hesabına bağlanacağını Seller ID'den biliyor.
- **Çözüm:** **Dişli** → **Account settings** → **Legal info** (bazen **Developer settings**) → **Seller ID**'yi
  kaydet. Bundan sonra InPrivate pencereyi kapatabilirsin.
- **Dosyalar:** -
- **Testler:** -
- **Durum:** ⏸️ Ertelendi.

### 19.5 — Store aracı kurulur ve bilgiler ona verilir.

- **Mevcut durum:** Bilgisayarda `msstore` yok.
- **Problem:** Bilgiler bir dosyaya ya da sohbete yazılırsa sızabilir.
- **Çözüm:** Ayrı bir PowerShell penceresinde (bu sohbette `!` ile değil) sırayla çalıştır:
  ```
  winget install "Microsoft Store Developer CLI"
  msstore reconfigure --tenantId <Tenant ID> --sellerId <Seller ID> --clientId <Client ID> --clientSecret <Key>
  msstore apps list
  ```
  Son komut My Everything Widget'ı listelerse kurulum tamamdır. Bana yalnız "tamam" yaz.
- **Dosyalar:** -
- **Testler:** `msstore apps list` uygulamayı listeler.
- **Durum:** ⏸️ Ertelendi.

### 19.6 — İlk güncelleme otomatik gönderilir (Claude).

- **Mevcut durum:** Gönderimi Partner Center'da sen yapıyorsun.
- **Problem:** -
- **Çözüm:** Claude sürümü yükseltir, iki paketi oluşturur ve `msstore publish <paket> --appId 9NRSQN57C9FH` ile gönderir.
  Gönderimin durumunu izler ve GitHub release'ini yayınlar.
- **Dosyalar:** `docs/general/STORE_SUBMISSION.md` → Automated submission
- **Testler:** Partner Center'da gönderim "In certification" görünür.
- **Durum:** ⏸️ Ertelendi.

## Referanslar

- `TALIMATLAR.md` → T135, T136, T137, T140
- `PHASE18.md` → 18.8 (bu faza taşındı)
- `docs/general/STORE_SUBMISSION.md` → Automated submission
