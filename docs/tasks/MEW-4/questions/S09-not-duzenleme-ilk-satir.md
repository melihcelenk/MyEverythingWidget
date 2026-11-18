---
id: S9
status: answered
decider: user
priority: major
asked: 2026-11-18
---
# S9 — Not düzenleme penceresi yalnız ilk satırı gösteriyor: düzelteyim mi?

**Mevcut durum:** Çok satırlı bir notu "Edit" ile açınca metin kutusunda yalnız ilk satır var; "Save"e basılırsa diğer satırlar silinir.

**Soru:** Aşağıdaki düzeltmeyi (A) uygulayayım mı?

## Bağlam

- **Neden:** `TextEditorDialog` metin kutusunu kurarken önce metni (`Text`), sonra çok satır iznini
  (`AcceptsReturn`) veriyor. WinUI'de tek satırlık bir metin kutusuna verilen metin ilk satır sonunda kesilir; izin
  ardından açıldığında kesilen satırlar geri gelmez.
- **Kanıt:** Ekran görüntüsündeki notun kayıtlı metni dört satırdan oluşuyor. Düzenleme penceresinde yalnız ilk satır
  (kutuda iki satıra kaydırılmış hali) görünüyor.
- **Risk:** Düzeltilene kadar çok satırlı bir notta "Save"e basmak notun ilk satırdan sonrasını siler. "Cancel" ya da
  Esc güvenli; kartın kendisi ve kayıtlı veri şu an sağlam.
- **Etki alanı:** Aynı pencere uygulama kartının adını değiştirmek için de kullanılıyor; orada tek satır olduğu için
  sorun yok.

## Seçenekler

### A — Sırayı düzelt ve testle koru ⭐

- `AcceptsReturn` ve `TextWrapping` metinden önce verilir.
- Önce bir UI testi yazılır: dört satırlık notu açınca metin kutusunda dört satırın hepsi olmalı ve hiçbir şey
  değiştirmeden "Save"e basınca not aynı kalmalı. Test önce kırmızı, düzeltmeden sonra yeşil olmalı.
- Süre: düzeltme küçük. Test için yalnız ilgili test sınıfı çalışır (~2 dk). Tam UI setinin (~12 dk) sonda
  çalıştırılıp çalıştırılmayacağına sen karar ver.

### B — Şimdilik dokunma

- Release'e kadar bekler; o zamana kadar çok satırlı notlarda "Save" kullanılmamalı.

## Öneri

**A** — veri kaybına yol açabilen bir hata, düzeltmesi tek satırlık bir sıra değişikliği.

## Cevap

**A — Sırayı düzelt ve testle koru**

## Sonuç

A uygulandı.

- **Düzeltme:** `TextEditorDialog` artık çok satır iznini (`AcceptsReturn`) metinden önce veriyor; not düzenleme
  penceresinde bütün satırlar görünüyor.
- **Test:** `NoteImagePasteTests.EditNoteFromMenu_ShowsEveryLine_AndSavingUnchangedKeepsThem`.
  - Düzeltmeden önce kırmızıydı: pencerede yalnız ilk satır vardı.
  - Düzeltmeden sonra geçiyor; sınıfın 9 testi de geçiyor.
- **Tam UI seti:** Çalıştırılmadı (~12 dk). Değişiklik yalnız bu pencereyi etkiliyor.
- **Ayrıntı:** `PHASE17.md` → 17.5.
