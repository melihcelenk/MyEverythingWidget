# Faz 18 — Diller, kompakt Ayarlar penceresi ve başlık düğmeleri

> **Durum:** 🟡 Devam ediyor · **Tamamlanma:** 95% · **Efor:** tahmin yazılmadı · **Task:** MEW-4

Uygulama İngilizce dahil 15 dilde. Açılışta Windows'un görüntü dili kullanılıyor; bu dil listede yoksa uygulama
İngilizce açılıyor. Ayarlar'dan başka bir dil seçilebiliyor. Ayarlar penceresi kompakt bir başlık ve sağ üstte bir
✕ ile açılıyor; alttaki Close düğmesi kaldırıldı ve pencere dışına tıklanınca kapanıyor. Küçük simgenin etrafındaki
boşluk daraldı. Sabitleme düğmesi sola, küçültme düğmesi kapatmanın yanına taşındı.

## Problem

- **Gereksinim (T124):**
  - **Diller:** Uygulamaya Türkçe, Ukraynaca, Lehçe, Almanca, İspanyolca, Hintçe, Filipince, Fransızca, Portekizce,
    Endonezce, İtalyanca, Rusça, Korece ve İsveççe eklenir.
  - **Çeviri garantisi:** Yeni bir özellik eklendiğinde çevrilmemiş dil kalmayacağı garanti altına alınır.
  - **Dil seçimi:** Ayarlar'a dil seçimi eklenir. Listenin en üstünde sistem dili durur ve varsayılan seçim odur;
    sistem dili listede yoksa uygulama İngilizce gösterilir.
  - **Ayarlar penceresi:**
    - Dil seçimiyle birlikte sığması için düzen değiştirilir.
    - Başlık ve üstündeki boşluk küçültülür.
    - Alttaki Close düğmesi kaldırılır; yerine sağ üstte ✕ gelir.
    - Uygulamada pencerenin dışına tıklanınca Ayarlar kapanır.
  - **Küçük simge:** Simgenin etrafındaki kalın, koyu boşluk daraltılır.
  - **Başlık düğmeleri:** Sabitleme düğmesiyle küçültme düğmesinin yeri değiştirilir.
  - **Teslim:** Testler yapılır ve her şey hazır olur.
- **Mevcut durum:**
  - Bütün metinler İngilizce olarak XAML'e ve koda yazılmıştı.
  - Ayarlar penceresinin başlığı ve Close düğmesi yer kaplıyordu.
  - Küçük simge 80 piksellik bir pencerede 48 piksellik bir logoydu.

## Çözüm

- **Metinler:** Bütün metinler tek bir kaynakta (`Strings.resx`) ve 14 çeviri dosyasında duruyor. Kod ve XAML
  metinleri bu kaynaktan okuyor.
- **Garanti:** `LocalizationCoverageTests` şu durumlardan birinde `dotnet test`'i kırmızı yapıyor:
  - eksik ya da boş çeviri,
  - bozulmuş `{0}` yer tutucusu,
  - XAML'de veya kodda sabit yazılmış bir metin.
- **Dil seçimi:** Varsayılan Windows'un dili, o listede yoksa İngilizce. Ayarlar'dan seçilen dil kaydediliyor ve
  uygulama kendini o dilde yeniden başlatıyor.
- **Ayarlar penceresi:** Tek satırlık başlık ve sağ üstte ✕. Close düğmesi yok; ✕, Esc ya da pencere dışına tıklama
  kapatıyor. Dil seçimi tek satırda.
- **Küçük simge ve düğmeler:** Küçük simgenin penceresi 64 piksel. Sabitleme düğmesi solda, küçültme düğmesi
  kapatmanın yanında.

## Alt fazlar

| # | Ne yapılıyor | Durum |
|---|--------------|-------|
| 18.1 | 14 dil eklenir; çevrilmemiş ya da sabit yazılmış metin testlerle engellenir. | 🟢 Tamamlandı |
| 18.2 | Ayarlar'a dil seçimi gelir; varsayılan sistem dili, listede yoksa İngilizce. | 🟢 Tamamlandı |
| 18.3 | Ayarlar penceresi kompaktlaşır: küçük başlık, sağ üstte ✕, dışarı tıklayınca kapanma. | 🟢 Tamamlandı |
| 18.4 | Küçük simgenin çerçevesi daralır; sabitleme ve küçültme düğmelerinin yeri değişir. | 🟢 Tamamlandı |
| 18.5 | Kullanıcı yeni sürümü kendi bilgisayarında dener. | ⏳ Bekliyor (kullanıcı) |
| 18.6 | Ayarlar'daki dil listesi aşağı doğru, yeşil kartın alt kenarına kadar açılır. | 🟢 Tamamlandı |
| 18.7 | Küçük simge, tam ekran bir video, oyun ya da sunum açıkken gizlenir; masaüstüne dönünce geri gelir. | 🟢 Tamamlandı |

## Nasıl kontrol edilir

- **Varsayılan dil:** Uygulamayı açınca Türkçe Windows'ta metinler Türkçe gelir ("Ekle", "Her zaman üstte").
- **Dil değiştirme:**
  - Ayarlar → Dil listesinin ilk satırı "Sistem dili".
  - Başka bir dil seçilince uygulama birkaç saniye içinde o dilde yeniden açılır.
  - "Sistem dili"ne geri dönülebilir.
- **Ayarlar penceresi:**
  - Sağ üstteki ✕, Esc ya da widget'ın karartılmış kısmına tıklama pencereyi kapatır.
  - Alt kısımda düğme yoktur.
- **Küçük simge ve düğmeler:**
  - Küçültme düğmesi artık sağda, ✕'nin hemen solunda; sabitleme düğmesi en solda.
  - Küçük simgenin etrafındaki koyu çerçeve incelmiştir.
- **Otomatik kontrol:**
  - `dotnet test`, çeviri garantisini de çalıştırır.
  - `pwsh scripts/test-ui.ps1 -Filter "/*/*/LanguageAndSettingsTests/*"` yeni UI testlerini çalıştırır. Bu testler
    her dilde Ayarlar'ın ekran görüntüsünü `tmp/sandbox/results/shots/settings-<dil>.png` olarak kaydeder.

## Kalan

- **Store sayfası:** Listeleme metinleri (açıklama, özellikler, görseller) şimdilik yalnız İngilizce. Dillere
  çevrilmesi ayrı bir iş.
- **Çevirilerin kontrolü:** Çeviriler Windows terminolojisine göre yapıldı. Ana dili konuşan birinin bakması yine de
  önerilir.

## Ayrıntılar

### 18.1 — 14 dil eklenir; çevrilmemiş ya da sabit yazılmış metin testlerle engellenir.

- **Mevcut durum:** Metinler İngilizce olarak XAML'e ve C# koduna yazılmıştı. Durum mesajları `BoardViewModel`
  sabitlerindeydi.
- **Problem:** Dil eklemek her metni ayrı ayrı bulmayı gerektiriyordu. Yeni bir özellikte metnin çevrilmesinin
  unutulması fark edilmezdi.
- **Çözüm:**
  - **Kaynak:**
    - `Strings.resx` (İngilizce, çevirmen açıklamalarıyla) ve `Strings.<dil>.resx`.
    - Kod tipli erişim kullanıyor: `Strings.AddNote`, `Strings.AppNotFound(name)`.
    - XAML `{l:Str Key=AddNote}` kullanıyor (`App/Localization/Str.cs`).
  - **Garanti (`LocalizationCoverageTests`):**
    - Her dilde aynı anahtarlar var; boş çeviri yok.
    - Yer tutucular aynı.
    - Her dil dosyası uygulamaya derleniyor.
    - `Strings` erişimcileri anahtarlarla birebir eşleşiyor; XAML'deki her anahtar var.
    - XAML'de ve `App`/`Presentation` kodunda sabit metin yok. Dilden bağımsız "2026", "Melih Çelenk" ve
      "melihcelenk.com" muaf.
  - **Çeviriler:**
    - Windows'un o dildeki terimleri kullanıldı.
    - Sayıyla çekimlenen dillerde cümleler "İçe aktarılan öğeler: {0}" biçiminde kuruldu.
    - Tema seçenekleri en fazla 9 harf.
  - **İlk sekme:** Yeni kurulumda ilk sekmenin adı uygulamanın dilinde ("Genel").
  - **WinUI'nin kendi metinleri:** Metin kutusu menüsü gibi metinler aynı dili izliyor
    (`ApplicationLanguages.PrimaryLanguageOverride`).
  - **Store:** Paket manifesti 15 dili bildiriyor (`Package.appxmanifest` → `Resources`).
- **Dosyalar:**
  - `src/MyEverythingWidget.Presentation/Localization/` (`Strings.cs`, `Strings*.resx`, `AppLanguages.cs`)
  - `src/MyEverythingWidget.App/Localization/Str.cs` ve metin içeren bütün XAML ve kod dosyaları
  - `src/MyEverythingWidget.Core/State/WidgetBoard.cs`, `WidgetState.cs`
  - `src/MyEverythingWidget.App/Package.appxmanifest`
  - `docs/general/DEVELOPMENT.md` → Localization
- **Testler:**
  - `Presentation.Tests/LocalizationCoverageTests`
  - `Core.Tests/State/DefaultCategoryNameTests`
  - Mevcut birim testleri, makinenin dilinden bağımsız olarak İngilizce metinlerle karşılaştırıyor
    (`Presentation.Tests/EnglishTexts.cs`).
- **Durum:** 🟢 Tamamlandı.

### 18.2 — Ayarlar'a dil seçimi gelir; varsayılan sistem dili, listede yoksa İngilizce.

- **Mevcut durum:** Dil seçimi yoktu.
- **Problem:** Kullanıcı, Windows'unun dilinden farklı bir dil isteyebilir.
- **Çözüm:**
  - **Liste:** İlk satır "System language" (uygulamanın dilinde, ör. "Sistem dili"). Sonra her dil kendi adıyla
    geliyor: English, Bahasa Indonesia, Deutsch, Español, Filipino, Français, Italiano, Polski, Português, Svenska,
    Türkçe, Русский, Українська, हिन्दी, 한국어.
  - **Kayıt:** Seçim `settings.json` → `language` alanına yazılıyor; `null` sistem dili demek.
  - **Çözümleme sırası (`AppLanguages.Resolve`):**
    1. Seçilen dil.
    2. Windows görüntü dili ya da onun üst dili (pt-BR → pt, fil-PH → fil, de-CH → de).
    3. İngilizce.
  - **Yeniden başlatma:** Başka bir dil seçilince uygulama kendini yeniden başlatıyor (`AppInstance.Restart`):
    - Pencerenin yeri önceden kaydediliyor.
    - Test veri klasörü yeni sürece `--data-dir=` argümanıyla aktarılıyor.
- **Dosyalar:**
  - `src/MyEverythingWidget.Core/Settings/AppSettings.cs`
  - `src/MyEverythingWidget.Presentation/MainViewModel.cs`
  - `src/MyEverythingWidget.App/App.xaml.cs`, `AppDataLocation.cs`, `MainWindow.xaml.cs`
  - `src/MyEverythingWidget.App/Views/SettingsDialog.xaml`, `SettingsDialog.xaml.cs`
- **Testler:**
  - `Presentation.Tests/AppLanguagesTests`
  - `Core.Tests/Settings/LanguageSettingsTests`
  - `UiTests/LanguageAndSettingsTests`:
    - `LanguageList_StartsWithTheSystemLanguage_WhichIsTheDefault`
    - `ChoosingALanguage_RestartsTheAppInIt_AndKeepsTheChoice`: Türkçe seçilince "Add" düğmesi "Ekle" oluyor.
    - `Settings_FitsTheWidget_InEveryLanguage` (15 dil)
  - **Testlerin dili:** Sandbox bilgisayarın Türkçe görüntü dilini devralıyor. Bu yüzden `AppSession`, sistem dili
    yerine geçen `MEW_SYSTEM_LANGUAGE=en-US` değişkenini veriyor.
- **Durum:** 🟢 Tamamlandı.

### 18.3 — Ayarlar penceresi kompaktlaşır: küçük başlık, sağ üstte ✕, dışarı tıklayınca kapanma.

- **Mevcut durum:** İletişim kutusunun kendi başlığı ve 24 piksellik üst boşluğu vardı. Altta bir Close düğmesi
  vardı. Pencere dışına tıklamak hiçbir şey yapmıyordu.
- **Problem:** Başlık ve Close düğmesi, dil seçimine yer bırakmıyordu.
- **Çözüm:**
  - **Başlık:** İçerikte tek satır; solda "Settings", sağ üst köşede ✕ (`SettingsCloseButton`). Üst iç boşluk 8
    piksel. Sağ iç boşluk yalnız ✕'nin 4 piksellik payı kadar; ayarların sağ boşluğunu bir kenar boşluğu koruyor.
  - **Düzen:** Dil seçimi tek satırda. Tema düğmelerinin iç boşluğu, uzun dillerde de tek satıra sığsın diye 10
    piksel.
  - **Kapanma:**
    - ✕, Esc ya da pencerenin karartılmış kısmına tıklama kapatıyor.
    - Karartma katmanı ayrı bir popup olduğu için tıklamalar açık popup'ların hepsinden dinleniyor.
    - Tıklanan nokta kutunun görünür kısmının (`BackgroundElement`) dışındaysa pencere kapanıyor.
- **Dosyalar:**
  - `src/MyEverythingWidget.App/Views/SettingsDialog.xaml`, `SettingsDialog.xaml.cs`
  - `src/MyEverythingWidget.App/Views/DialogSizing.cs`
- **Testler:**
  - `UiTests/LanguageAndSettingsTests`:
    - `Settings_HasACrossAtTheTopRight_AndNoCloseButtonAtTheBottom`
    - `Settings_TitleTakesLittleRoom`
    - `Settings_ClosesWhenClickingTheAppOutsideIt`
  - **Güncellenen eski testler:**
    - `WindowLayoutTests.SettingsDialog_*`: Close düğmesi yerine About kartına ve kutunun görünür kenarına göre
      ölçüyor. Kenar ekrandan, piksel renginden bulunuyor (`Infrastructure/DialogBox.cs`), çünkü iletişim kutusunun
      UIA öğesi bütün pencereyi kaplıyor.
    - `SettingsAndMigrationTests` kapatmak için ✕'yi kullanıyor.
    - `ImageCopyTests.ViewerContextMenu_CopiesAndSaysSo` önce "Copied" yazısını, sonra panoyu kontrol ediyor. Yazı 1,5
      saniye görünüyor, pano kontrolü ise PowerShell başlattığı için Sandbox'ta daha uzun sürebiliyordu; test bu
      yüzden ara sıra kırmızı oluyordu.
- **Durum:** 🟢 Tamamlandı.

### 18.4 — Küçük simgenin çerçevesi daralır; sabitleme ve küçültme düğmelerinin yeri değişir.

- **Mevcut durum:**
  - Küçük simgenin penceresi 80 pikseldi; 48 piksellik logonun her yanında 16 piksel koyu boşluk kalıyordu.
  - Küçültme düğmesi solda, sabitleme düğmesi sağdaydı.
- **Problem:** Çerçeve gereğinden kalındı. Düğmelerin yerini kullanıcı değiştirmek istedi.
- **Çözüm:** Küçük simge penceresi 64 piksel, yani her yanda 8 piksel boşluk. Sabitleme düğmesi sekmelerin solunda;
  küçültme düğmesi kapatma düğmesinin yanında.
- **Dosyalar:** `src/MyEverythingWidget.App/MainWindow.xaml`, `MainWindow.xaml.cs`
- **Testler:** `UiTests/LanguageAndSettingsTests`:
  - `CompactIcon_HasOnlyAThinFrameAroundTheLogo`
  - `PinIsOnTheLeft_AndCompactButtonIsNextToClose`
- **Durum:** 🟢 Tamamlandı.

### 18.5 — Kullanıcı yeni sürümü kendi bilgisayarında dener.

- **Mevcut durum:** Değişiklikler Sandbox testlerinden geçti; geliştirme sürümü kullanıcının bilgisayarında açıldı
  (T129, `scripts/run.ps1`).
- **Problem:** Gerçek kullanımda görülecek eksikler henüz bilinmiyor.
- **Çözüm:** Kullanıcının geri bildirimleri bu alt faza işlenir.
- **Dosyalar:** -
- **Testler:** -
- **Durum:** ⏳ Bekliyor (kullanıcı).

### 18.6 — Ayarlar'daki dil listesi aşağı doğru, yeşil kartın alt kenarına kadar açılır.

- **Gereksinim (T130):** Dil kutusuna tıklanınca liste aşağı doğru açılır ve yeşil About kartının alt kenarına kadar
  uzanır.
- **Mevcut durum:** Liste yukarı doğru açılıp widget'ın dışına taşıyor.
- **Problem:** WinUI'nin `ComboBox`'ı listeyi, seçili satır kutunun üstüne gelecek biçimde konumluyor. Seçili satır
  ilk satır olduğu için 16 satırlık liste yukarı uzanıyor. Yön ve yükseklik ayarlanamıyor.
- **Çözüm (S20 → A):**
  - `ComboBox` yerine aynı görünen bir düğme (`LanguageChoice`) ve altından açılan bir liste (`LanguageList`)
    kullanılıyor.
  - Liste düğmeyle aynı genişlikte. Yüksekliği açılırken, düğmenin altından yeşil kartın alt kenarına kadar
    hesaplanıyor.
  - Sığmayan diller kaydırılıyor; seçili dil görünür.
- **Dosyalar:** `src/MyEverythingWidget.App/Views/SettingsDialog.xaml`, `SettingsDialog.xaml.cs`
- **Testler:** `UiTests/LanguageAndSettingsTests`:
  - `LanguageList_OpensDownwards_ToTheBottomOfTheAboutCard`
  - Dil listesi testleri yeni listeye göre güncellendi.
- **Durum:** 🟢 Tamamlandı.

### 18.7 — Küçük simge, tam ekran bir video, oyun ya da sunum açıkken gizlenir; masaüstüne dönünce geri gelir.

- **Gereksinim (T132):** Küçük simge her zaman üstte kalır, ama tam ekran bir video, oyun ya da benzeri açıkken
  görünmez. Masaüstüne dönülünce geri gelir.
- **Mevcut durum:** YouTube'da tam ekran video açıkken küçük simge videonun üstünde kalıyordu.
- **Problem:** "Her zaman üstte" penceresi, tam ekran uygulamaların da üstüne çıkıyor.
- **Çözüm:**
  - `FullScreenWatcher` küçük simge modundayken yarım saniyede bir öndeki pencereye bakıyor. Pencere simgenin
    bulunduğu monitörün tamamını kaplıyorsa simge gizleniyor (`FullScreen.Covers`). Kaplama görev çubuğu dahil
    sayılıyor; yalnız büyütülmüş bir pencere sayılmıyor.
  - Tam ekran pencere kapanınca, küçülünce ya da başka bir pencereye geçilince simge yeniden, yine en üstte görünüyor.
  - Masaüstü ve görev çubuğu tam ekran sayılmıyor. Başka monitördeki tam ekran pencere simgeyi gizlemiyor.
  - Açık widget sabitlenmiş olsa bile bu kurala dahil değil; istek küçük simge içindi.
- **Dosyalar:**
  - `src/MyEverythingWidget.Core/Geometry/FullScreen.cs`
  - `src/MyEverythingWidget.App/Interop/FullScreenWatcher.cs`, `NativeMethods.cs`
  - `src/MyEverythingWidget.App/MainWindow.xaml.cs`
- **Testler:**
  - `Core.Tests/Geometry/FullScreenTests`: monitörü kaplayan, taşan, büyütülmüş, başka monitörde ve küçük pencereler.
  - `UiTests/LanguageAndSettingsTests.CompactIcon_HidesWhileAWindowIsFullScreen_AndComesBackAfterwards`: Sandbox'ta
    kenarlıksız, ekranı kaplayan bir pencere açılınca simge gizleniyor. Pencere kapanınca simge yeniden en üstte
    görünüyor.
- **Durum:** 🟢 Tamamlandı.

## Referanslar

- `TALIMATLAR.md` → T124 (T125–T127 çeviri alt ajanlarının raporları)
- `docs/general/DEVELOPMENT.md` → Localization
