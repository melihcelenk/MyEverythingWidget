# MEW-4 Faz 4 — Kategoriler

> Önce: `PHASE3.md` · Sonra: `PHASE5.md` (Uygulama ekleme ve otomatik ikon)

## İçindekiler

- Durum Panosu
- 4.1 Kapsam
- 4.2 Kurallar
- 4.3 Tasarım kararları
- 4.4 Testler
- 4.5 Sonuç

---

## Durum Panosu

| İş | Durum | Not |
|----|-------|-----|
| `WidgetBoard` kategori işlemleri | 🟢 Tamamlandı | Ekle, adlandır, sil, sırala, seç, öğe taşı |
| `BoardViewModel` sekmeleri, `CategoryViewModel` | 🟢 Tamamlandı | |
| `CategoryTabsView` (TabView) ve kart menüsünde "Move to" | 🟢 Tamamlandı | |

---

## 4.1 Kapsam

- Sekmeler: seçme, "+" ile ekleme (ad hemen düzenlenir), sağ tık "Rename" ya da çift tık ile yeniden adlandırma.
- Silme: sağ tık "Delete". Kategoride öğe varsa onay sorar; son kategori silinemez.
- Sekmeleri sürükleyerek sıralama.
- Kartın sağ tık menüsünde "Move to" → diğer kategoriler.
- Açık sekme kaydedilir; uygulama yeniden açılınca aynı sekmeyle açılır.

---

## 4.2 Kurallar

| Durum | Davranış |
|-------|----------|
| Kategori adı boş ya da yalnız boşluk | Ad değişmez (yeni kategoride "New category" kalır) |
| Ad 30 karakterden uzun | 30 karaktere kısaltılır |
| Son kategori silinmek istenir | Menüde "Delete" pasiftir; Core da reddeder |
| Açık sekme silinir | Solundaki sekme açılır (ilk sekmeyse yeni ilk sekme) |
| "Move to" hedef kategoride yer yok | Kart yerinde kalır; "There is no room in {ad}." uyarısı |
| Kayıtlı açık sekme artık yok (örnek: elle düzenlenmiş dosya) | İlk sekme açılır |

---

## 4.3 Tasarım kararları

| Karar | Seçim | Gerekçe |
|-------|-------|---------|
| Sekme kontrolü | WinUI `TabView`, kapat düğmesi yok | Sürükleyerek sıralama hazır; kapatma = silme olmamalı |
| Görünüm | Şerit Mica üzerinde; açık sekme ve grid ortak katman renginde (`LayerFillColorDefaultBrush`) | Windows 11 sekmeli uygulamalarıyla aynı dil |
| Ekleme | "+" sekme şeridinin sonunda; yeni sekme açılır ve ad kutusu seçili metinle gelir | Tek tıkla ekle, hemen adlandır |
| Silme onayı | Yalnız öğe varsa; varsayılan düğme "Cancel" | Boş kategoride gereksiz soru yok, dolu kategoride kazara silme yok |

---

## 4.4 Testler

| Kabul kriteri | Test |
|---------------|------|
| Kategori kuralları (Core) | `Core.Tests` → `WidgetBoardCategoryTests` (17) |
| Sekme senkronizasyonu, uyarılar | `Presentation.Tests` → `BoardViewModelCategoryTests` (12) |
| "+" ile ekleme ve adlandırma | `UiTests` → `CategoryTests.PlusButton_CreatesNamedCategoryAndOpensIt` |
| Sekme seçimi | `UiTests` → `SelectingTab_ShowsOnlyItsCards` |
| Açık sekmenin hatırlanması | `UiTests` → `OpenTab_IsRestoredAfterRestart` |
| Yeniden adlandırma | `UiTests` → `RenameFromContextMenu_ChangesTabName` |
| Onaylı silme / vazgeçme | `UiTests` → `DeleteCategoryWithItems_AsksAndThenDeletesItAndItsItems`, `DeleteCategory_Cancelled_KeepsEverything` |
| "Move to" | `UiTests` → `MoveToFromCardMenu_MovesCardToOtherCategory` |
| Sürükleyerek sıralama (gerçek fare) | `UiTests` → `DraggingTab_ReordersCategories` |

---

## 4.5 Sonuç

Faz 4 tamamlandı (2026-10-30).

| Test grubu | Sonuç |
|------------|-------|
| Unit (`dotnet test`) | 128/128 |
| UI (Sandbox) | 28/28 |
| Sonar | 0 bulgu |

### 4.5.1 Notlar

- Core ve Presentation kodu testlerden hemen sonra yazıldı; kırmızı aşama ayrıca koşturulmadı. UI testlerinin ilk
  koşusunda iki test kırmızıydı (aşağıda), yani testler davranışı gerçekten ölçüyor.
- **"+" sonrası ad kutusu açılmıyordu:** kutu, yeni sekme görsel ağaca girmeden açılmaya çalışılıyordu. Artık sekmenin
  `Loaded` olayı bekleniyor.
- **"Move to" testinin beklentisi yanlıştı:** hedef kategoride iki not ilk iki satırın sol yarısını doldurduğu için ilk
  boş hücre R1C3'tür; uygulama doğruydu, testteki elle hesap düzeltildi.
- Silme onayının "Cancel" düğmesinin otomasyon kimliği (`CloseButton`) pencerenin kapat düğmesiyle aynıdır; testler
  dialog düğmelerini `DeleteCategoryDialog` içinde arar.
