const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, ShadingType, BorderStyle, PageBreak, VerticalAlign,
} = require('docx');

// A4 = 11906 x 16838 DXA. Margins 1080 (0.75") -> usable 9746
const W = 9746;
const BOX = '☐'; // ☐
const GREY = 'E8E8E8';
const DARK = 'C9C9C9';

const P = (text, opts = {}) => new Paragraph({
  spacing: { before: opts.before ?? 40, after: opts.after ?? 40 },
  alignment: opts.align,
  children: [new TextRun({
    text: text ?? '',
    bold: opts.bold,
    italics: opts.italics,
    size: opts.size ?? 19,
    color: opts.color,
    font: 'Calibri',
  })],
  shading: opts.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: opts.fill } : undefined,
  border: opts.rule ? { bottom: { style: BorderStyle.SINGLE, size: 6, color: '888888' } } : undefined,
});

// Paragraph made of mixed runs
const PR = (runs, opts = {}) => new Paragraph({
  spacing: { before: opts.before ?? 40, after: opts.after ?? 40 },
  alignment: opts.align,
  shading: opts.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: opts.fill } : undefined,
  children: runs.map(r => new TextRun({
    text: r.t, bold: r.b, italics: r.i, size: r.s ?? 19, color: r.c, font: 'Calibri',
  })),
});

const cell = (text, width, opts = {}) => new TableCell({
  width: { size: width, type: WidthType.DXA },
  shading: opts.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: opts.fill } : undefined,
  verticalAlign: VerticalAlign.CENTER,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [P(text, { bold: opts.bold, size: opts.size ?? 19, align: opts.align, before: 20, after: 20 })],
});

const table = (widths, rows) => new Table({
  columnWidths: widths,
  width: { size: W, type: WidthType.DXA },
  rows,
});

// Section heading bar
const SEC = (text) => new Paragraph({
  spacing: { before: 260, after: 100 },
  shading: { type: ShadingType.CLEAR, color: 'auto', fill: DARK },
  children: [new TextRun({ text: `  ${text}`, bold: true, size: 22, font: 'Calibri' })],
});

// 2-column label/value table
const fieldTable = (rows) => table([5900, 3846], [
  new TableRow({ children: [cell('Alan', 5900, { bold: true, fill: GREY }), cell('Yanıt', 3846, { bold: true, fill: GREY })] }),
  ...rows.map(([l, v]) => new TableRow({ children: [cell(l, 5900), cell(v, 3846)] })),
]);

// grid: first col label + N option columns
const gridTable = (labelHead, opts, rows, labelW = 4946) => {
  const oW = Math.floor((W - labelW) / opts.length);
  const widths = [labelW, ...opts.map(() => oW)];
  const total = widths.reduce((a, b) => a + b, 0);
  widths[1] += W - total; // absorb rounding
  return table(widths, [
    new TableRow({
      children: [cell(labelHead, widths[0], { bold: true, fill: GREY }),
        ...opts.map((o, i) => cell(o, widths[i + 1], { bold: true, fill: GREY, align: AlignmentType.CENTER }))],
    }),
    ...rows.map(r => new TableRow({
      children: [cell(r, widths[0]),
        ...opts.map((_, i) => cell(BOX, widths[i + 1], { size: 24, align: AlignmentType.CENTER }))],
    })),
  ]);
};

const dots = (n) => '.'.repeat(n);

const kids = [];

// ---------- TITLE ----------
kids.push(P('OLGU RAPOR FORMU (ORF)', { bold: true, size: 32, align: AlignmentType.CENTER, before: 0, after: 80 }));
kids.push(P('ÇÖLYAK-BGG Çalışması', { bold: true, size: 24, align: AlignmentType.CENTER, after: 60 }));
kids.push(P('Büyüme-Gelişme Geriliği ile Başvuran Çocuklarda Çölyak Hastalığı Taramasının Tanısal Verimi ve Seçici Tarama Ölçütlerinin Belirlenmesi',
  { size: 19, align: AlignmentType.CENTER, italics: true, after: 100 }));
kids.push(P('Antalya Eğitim ve Araştırma Hastanesi — Çocuk Gastroenteroloji Kliniği',
  { size: 19, align: AlignmentType.CENTER, after: 40 }));
kids.push(P(`Etik Kurul Onay No: ${dots(22)}     Tarih: ..... / ..... / ..........`,
  { size: 19, align: AlignmentType.CENTER, after: 160 }));

// Warning box
kids.push(new Table({
  columnWidths: [W],
  width: { size: W, type: WidthType.DXA },
  rows: [new TableRow({
    children: [new TableCell({
      width: { size: W, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'FFF2CC' },
      margins: { top: 120, bottom: 120, left: 160, right: 160 },
      children: [PR([
        { t: 'UYARI — ', b: true },
        { t: 'Hasta adı, soyadı, T.C. kimlik numarası veya protokol numarası bu forma ', b: true },
        { t: 'YAZILMAZ', b: true },
        { t: '. Yalnızca çalışma kodu kullanılır. Eşleştirme anahtarı ayrı ve şifreli dosyada tutulur.' },
      ])],
    })],
  })],
}));

kids.push(P('', { after: 100 }));
kids.push(table([3200, 3200, 3346], [
  new TableRow({
    children: [
      cell('Çalışma kodu:  ÇLY – _ _ _ _', 3200, { bold: true }),
      cell(`Formu dolduran: ${dots(14)}`, 3200),
      cell('Tarih: ..... /..... /..........', 3346),
    ],
  }),
]));

kids.push(PR([
  { t: 'Kodlama kuralları: ', b: true },
  { t: 'Bilgi dosyada ' },
  { t: 'yok / kayıtlı değil', b: true },
  { t: ' ise ' },
  { t: '9', b: true },
  { t: ' yazın — boş bırakmayın. Test ' },
  { t: 'yapılmamış', b: true },
  { t: ' ise ' },
  { t: '9', b: true },
  { t: '. Uygulanamaz durumlar için ' },
  { t: 'U', b: true },
  { t: ' yazın.' },
], { before: 140 }));

// ---------- A ----------
kids.push(SEC('BÖLÜM A — BAŞVURU VE DEMOGRAFİK BİLGİLER'));
kids.push(fieldTable([
  ['A1. Başvuru yılı', '_ _ _ _'],
  ['A2. Başvuru ayı', '_ _'],
  ['A3. Başvuru yaşı (AY olarak — yıl değil)', '_ _ _  ay'],
  ['A4. Cinsiyet', `${BOX} Kız (0)    ${BOX} Erkek (1)`],
  ['A5. Başvurulan branş', `${BOX} Genel ped. (1)  ${BOX} Ç. gastro (2)  ${BOX} Ç. endokrin (3)  ${BOX} Diğer (4)`],
  ['A6. İstemi yapan hekim', `${BOX} Asistan (1)  ${BOX} Uzman (2)  ${BOX} Öğr. üyesi (3)  ${BOX} Kayıt yok (9)`],
  ['A7. Dış merkezden sevkli mi', `${BOX} Hayır (0)   ${BOX} Evet (1)   ${BOX} Kayıt yok (9)`],
]));

// ---------- B ----------
kids.push(SEC('BÖLÜM B — ANTROPOMETRİK ÖLÇÜMLER'));
kids.push(fieldTable([
  ['B1. Boy', `${dots(14)} cm`],
  ['B2. Ağırlık', `${dots(14)} kg`],
  ['B3. Boy SDS (Neyzi)', dots(16)],
  ['B4. Ağırlık SDS (Neyzi)', dots(16)],
  ['B5. VKİ SDS (Neyzi)', dots(16)],
  ['B6. Boy SDS (WHO 2007)', `${dots(10)}   ${BOX} Hesaplanmadı (9)`],
  ['B7. Anne boyu', `${dots(8)} cm   ${BOX} Kayıt yok (9)`],
  ['B8. Baba boyu', `${dots(8)} cm   ${BOX} Kayıt yok (9)`],
  ['B9. Hedef boy SDS', `${dots(10)}   ${BOX} Hesaplanamadı (9)`],
  ['B10. Hedef boydan sapma  (B3 − B9)', `${dots(10)}   ${BOX} Hesaplanamadı (9)`],
  ['B11. Kemik yaşı (Greulich-Pyle)', `${dots(8)} yıl   ${BOX} Bakılmamış (9)`],
  ['B12. Kemik yaşı − kronolojik yaş', `${dots(8)} yıl   ${BOX} Hesaplanamadı (9)`],
]));
kids.push(PR([{ t: 'B13. Hangi BGG ölçütü karşılanıyor?', b: true },
  { t: '  (birden fazla varsa 5 işaretleyip ilgili tüm kutuları da işaretleyin)', i: true }], { before: 140 }));
kids.push(P(`${BOX} (1) Boy SDS < −2      ${BOX} (2) Ağırlık SDS < −2      ${BOX} (3) VKİ SDS < −2`));
kids.push(P(`${BOX} (4) Hedef boydan sapma > 1,6 SDS      ${BOX} (5) Birden fazla ölçüt`));

// ---------- C ----------
kids.push(SEC('BÖLÜM C — DAHİL / DIŞLAMA KONTROLÜ   ⚠ ÖNCE BURAYI DOLDURUN'));
kids.push(PR([{ t: 'C1. Dahil edilme ölçütleri', b: true }, { t: '  (hepsi "Evet" olmalı)', i: true }]));
kids.push(gridTable('Ölçüt', ['Evet', 'Hayır'], [
  '18 yaşını doldurmamış (0–18 yaş)',
  'Kayıtta BGG / boy kısalığı / kilo alamama / gelişme geriliği var (R62.8, R62.5, R63.4, E34.3)',
  'Antropometrik ölçütlerden en az biri karşılanıyor (Bölüm B13)',
  'Boy, ağırlık ve temel laboratuvar verisi erişilebilir',
], 6946));

kids.push(PR([{ t: 'C2. Dışlama ölçütleri', b: true }, { t: '  (herhangi biri "Evet" ise hasta DIŞLANIR)', i: true }], { before: 160 }));
kids.push(gridTable('Ölçüt', ['Evet', 'Hayır'], [
  'Çalışma dönemi öncesinde çölyak tanısı almış',
  'Değerlendirme sırasında glutensiz diyette (belgelenmiş)',
  'Bilinen sendromik hastalık / iskelet displazisi',
  'Kronik böbrek yetmezliği',
  'Konjenital kalp hastalığı',
  'Malignite',
  'Kronik sistemik kortikosteroid kullanımı',
  'İleri prematürite sekeli',
  'Antropometrik veri eksik / doğrulanamıyor',
], 6946));

kids.push(PR([{ t: 'C3. KARAR: ', b: true }, { t: `${BOX} Çalışmaya DAHİL EDİLDİ (0) → Bölüm D'ye geçin` }], { before: 160 }));
kids.push(P(`${BOX} DIŞLANDI → nedeni:  ${BOX} (1) Önceden çölyak tanılı   ${BOX} (2) Glutensiz diyette`));
kids.push(PR([{ t: `${BOX} (3) Bilinen kronik hastalık   ${BOX} (4) Antropometri eksik   →  ` },
  { t: 'formu burada bitirin', b: true }]));

// ---------- D ----------
kids.push(SEC('BÖLÜM D — GASTROİNTESTİNAL SEMPTOMLAR'));
kids.push(gridTable('Semptom', ['Yok (0)', 'Var (1)', 'Kayıt yok (9)'], [
  'D1. Kronik ishal (≥4 hafta)',
  'D2. Kabızlık',
  'D3. Tekrarlayan karın ağrısı',
  'D4. Karın şişkinliği / distansiyon',
  'D5. Kusma',
  'D6. İştahsızlık',
]));
kids.push(PR([{ t: 'D7. Herhangi bir GİS semptomu var mı?', b: true },
  { t: `  (D1–D6'dan en az biri "Var" ise)    ${BOX} Yok (0)    ${BOX} Var (1)` }], { before: 140 }));

// ---------- E ----------
kids.push(SEC('BÖLÜM E — EŞLİK EDEN HASTALIKLAR VE AİLE ÖYKÜSÜ'));
kids.push(gridTable('Durum', ['Yok (0)', 'Var (1)', 'Kayıt yok (9)'], [
  'E1. Tip 1 diyabet',
  'E2. Otoimmün tiroidit / hipotiroidi',
  'E3. Diğer otoimmün hastalık',
  'E4. 1. derece akrabada çölyak',
]));
kids.push(PR([{ t: 'E5. Sendrom: ', b: true },
  { t: `${BOX} Yok (0)  ${BOX} Down (1)  ${BOX} Turner (2)  ${BOX} Williams (3)  ${BOX} Diğer (4): ${dots(16)}` }], { before: 140 }));

// ---------- F ----------
kids.push(SEC('BÖLÜM F — DİĞER KLİNİK BULGULAR'));
kids.push(gridTable('Bulgu', ['Yok (0)', 'Var (1)', 'Kayıt yok (9)'], [
  'F1. Diş minesi defekti',
  'F2. Tekrarlayan aftöz stomatit',
  'F3. Dermatit herpetiformis',
  'F4. Kronik yorgunluk / halsizlik',
]));
kids.push(PR([{ t: 'F5. Puberte gecikmesi: ', b: true },
  { t: `${BOX} Yok (0)  ${BOX} Var (1)  ${BOX} Yaşa uygun değil (8)  ${BOX} Kayıt yok (9)` }], { before: 140 }));

// ---------- G ----------
kids.push(SEC('BÖLÜM G — LABORATUVAR'));
kids.push(table([5400, 2600, 1746], [
  new TableRow({
    children: [cell('Test', 5400, { bold: true, fill: GREY }), cell('Değer', 2600, { bold: true, fill: GREY }),
      cell('Bakılmamış (9)', 1746, { bold: true, fill: GREY, align: AlignmentType.CENTER })],
  }),
  ...[
    ['G1. Hemoglobin', 'g/dL'], ['G2. MCV', 'fL'], ['G3. Ferritin', 'µg/L'],
    ['G4. ALT', 'U/L'], ['G5. AST', 'U/L'], ['G6. Albümin', 'g/dL'],
    ['G7. 25-OH D vitamini', 'ng/mL'], ['G8. Kalsiyum', 'mg/dL'], ['G9. ALP', 'U/L'],
    ['G10. Çinko', 'µg/dL'], ['G11. TSH', 'mIU/L'], ['G12. IGF-1 SDS', ''],
    ['G13. Total IgA   ← bakılmamışsa G1 kategorisi', 'mg/dL'],
  ].map(([l, u]) => new TableRow({
    children: [cell(l, 5400, { bold: l.startsWith('G13') }), cell(`${dots(12)} ${u}`, 2600),
      cell(BOX, 1746, { size: 24, align: AlignmentType.CENTER })],
  })),
]));
kids.push(P('Türetilmiş değerlendirmeler', { bold: true, before: 160 }));
kids.push(gridTable('Değerlendirme', ['Yok (0)', 'Var (1)', 'Bakılmamış (9)'], [
  'G14. Demir eksikliği (ferritin <12 µg/L [<5 yaş] veya <15 µg/L)',
  'G15. Demir eksikliği anemisi (yaşa göre düşük Hb + düşük ferritin)',
  'G16. Transaminaz yüksekliği (ALT veya AST > ULN)',
  'G17. Anti-TPO pozitifliği',
  'G18. Selektif IgA eksikliği',
]));

// ---------- H ----------
kids.push(SEC('BÖLÜM H — ÇÖLYAK SEROLOJİSİ'));
kids.push(PR([{ t: 'H1. Çölyak serolojisi istendi mi?   ', b: true },
  { t: `${BOX} Hayır (0)  →  ` }, { t: "Bölüm K'ya geçin", b: true }, { t: `      ${BOX} Evet (1)` }]));
kids.push(fieldTable([
  ['H2. İstem ile başvuru arası süre', `${dots(10)} gün`],
  ['H3. Anti-tTG IgA değeri', `${dots(10)} U/mL   ${BOX} İstenmedi (9)`],
  ['H4. Kitin normal üst sınırı (ULN)  — ZORUNLU', `${dots(10)} U/mL`],
  ['H5. tTG / ULN oranı  (H3 ÷ H4)', `${dots(10)} kat`],
  ['H6. Kullanılan kit markası', `${dots(16)}  ${BOX} Kayıt yok (9)`],
]));
kids.push(P('', { after: 60 }));
kids.push(gridTable('Test sonucu', ['Negatif (0)', 'Pozitif (1)', 'İstenmedi (9)'], [
  'H7. Anti-tTG IgA',
  'H8. Anti-tTG IgG  (IgA eksikliğinde)',
  'H9. EMA (endomisyum antikoru)',
  'H10. DGP (deamide gliadin peptid)',
]));
kids.push(PR([{ t: 'H11. tTG ≥ 10× ULN mü?   ', b: true },
  { t: `${BOX} Hayır (0)   ${BOX} Evet (1)   ${BOX} Uygulanamaz (9)` }], { before: 140 }));
kids.push(PR([{ t: 'H12. AGA (anti-gliadin) istendi mi?   ', b: true },
  { t: `${BOX} Hayır (0)   ${BOX} Evet (1)    ` }, { t: '← Evet ise G2 kategorisi', i: true }]));
kids.push(PR([{ t: 'H13. Seroloji pozitif mi?   ', b: true },
  { t: `${BOX} Hayır (0)   ${BOX} Evet (1)` }]));
kids.push(P('(tTG IgA veya EMA veya DGP pozitif; IgA eksikliğinde IgG bazlı test)', { italics: true, size: 17 }));
kids.push(PR([{ t: 'H14. HLA DQ2/DQ8 bakıldı mı?   ', b: true }, { t: `${BOX} Hayır (0)   ${BOX} Evet (1)` }], { before: 100 }));
kids.push(PR([{ t: 'H15. HLA sonucu:   ', b: true },
  { t: `${BOX} Negatif (0)  ${BOX} DQ2 (1)  ${BOX} DQ8 (2)  ${BOX} Her ikisi (3)  ${BOX} Bakılmadı (9)` }]));

// ---------- I ----------
kids.push(SEC('BÖLÜM I — TANI DOĞRULAMA'));
kids.push(PR([{ t: 'I1. Duodenal biyopsi yapıldı mı?   ', b: true }, { t: `${BOX} Hayır (0)   ${BOX} Evet (1)` }]));
kids.push(PR([{ t: 'I2. Marsh evresi:', b: true }], { before: 120 }));
kids.push(P(`${BOX} Marsh 0 (0)   ${BOX} Marsh 1 (1)   ${BOX} Marsh 2 (2)   ${BOX} Marsh 3a (3)   ${BOX} Marsh 3b (4)`));
kids.push(P(`${BOX} Marsh 3c (5)   ${BOX} Biyopsi yapılmadı (9)`));
kids.push(PR([{ t: 'I3. Çölyak tanısı doğrulandı mı?   ', b: true }, { t: `${BOX} Hayır (0)   ${BOX} Evet (1)` }], { before: 120 }));
kids.push(P('ESPGHAN 2020:  Marsh ≥2   VEYA   (tTG ≥10× ULN + ikinci örnekte EMA pozitif)', { italics: true, size: 17 }));
kids.push(PR([{ t: 'I4. Tanı yolu:   ', b: true },
  { t: `${BOX} Biyopsi (1)   ${BOX} Biyopsisiz — ESPGHAN 2020 (2)   ${BOX} Tanı yok (9)` }], { before: 120 }));
kids.push(PR([{ t: 'I5. Yalancı pozitif mi?   ', b: true },
  { t: `${BOX} Hayır (0)   ${BOX} Evet (1)   ${BOX} Uygulanamaz (9)` }], { before: 120 }));
kids.push(P('(seroloji pozitif ama biyopsi normal veya izlemde seroloji normale döndü)', { italics: true, size: 17 }));

// ---------- J ----------
kids.push(SEC('BÖLÜM J — İSTEM UYGUNLUĞU DEĞERLENDİRMESİ'));
kids.push(P('Bu bölüm iki araştırmacı tarafından BİRBİRİNDEN BAĞIMSIZ doldurulur. Uyuşmazlık üçüncü araştırmacı tarafından çözülür. Gözlemciler arası uyum Cohen kappa ile hesaplanacaktır.',
  { italics: true, size: 18 }));
const jW = [700, 5646, 1100, 1100, 1200];
kids.push(table(jW, [
  new TableRow({
    children: [cell('Kod', jW[0], { bold: true, fill: GREY, align: AlignmentType.CENTER }),
      cell('Ölçüt', jW[1], { bold: true, fill: GREY }),
      cell('Hayır (0)', jW[2], { bold: true, fill: GREY, align: AlignmentType.CENTER }),
      cell('Evet (1)', jW[3], { bold: true, fill: GREY, align: AlignmentType.CENTER }),
      cell('U', jW[4], { bold: true, fill: GREY, align: AlignmentType.CENTER })],
  }),
  ...[
    ['G1', 'Anti-tTG IgA istenmiş, total IgA hiç bakılmamış'],
    ['G2', 'AGA (anti-gliadin) istenmiş'],
    ['G3', 'Negatif seroloji, yeni klinik gerekçe olmaksızın <12 ay içinde tekrarlanmış'],
    ['G4', 'İlk basamakta tTG + EMA + DGP birlikte istenmiş'],
    ['G5', 'Pozitif seroloji, hiç ileri tetkik / sevk / izlem yapılmamış'],
    ['G6', 'Hiçbir ek risk bulgusu yok (aile öyküsü, GİS semptomu, anemi, otoimmün hastalık, sendrom yok)'],
    ['G7', 'Glutensiz diyet altında seroloji istenmiş'],
  ].map(([k, d]) => new TableRow({
    children: [cell(k, jW[0], { bold: true, align: AlignmentType.CENTER }), cell(d, jW[1]),
      cell(BOX, jW[2], { size: 24, align: AlignmentType.CENTER }),
      cell(BOX, jW[3], { size: 24, align: AlignmentType.CENTER }),
      cell(BOX, jW[4], { size: 24, align: AlignmentType.CENTER })],
  })),
]));
kids.push(PR([{ t: 'J1. İşaretlenen kategoriler: ', b: true }, { t: dots(44) }], { before: 140 }));
kids.push(P('(çoklu ise noktalı virgülle, örn. G1;G4)', { italics: true, size: 17 }));
kids.push(PR([{ t: 'J2. Gereksiz istem — birincil tanım ', b: true },
  { t: `(G1–G5 veya G7'den en az biri "Evet")    ${BOX} Hayır (0)   ${BOX} Evet (1)` }], { before: 120 }));
kids.push(PR([{ t: 'J3. Kılavuz-dışı endikasyon ', b: true },
  { t: `(yalnızca G6)    ${BOX} Hayır (0)   ${BOX} Evet (1)` }]));

// ---------- K ----------
kids.push(SEC('BÖLÜM K — İZLEM'));
kids.push(fieldTable([
  ['K1. İzlem süresi', `${dots(8)} ay   ${BOX} İzlem yok (9)`],
  ['K2. İzlemde çölyak tanısı aldı mı?', `${BOX} Hayır (0)  ${BOX} Evet (1)  ${BOX} İzlem yok (9)`],
  ['K3. Tanı aldıysa, başvurudan kaç ay sonra?', `${dots(8)} ay   ${BOX} Uygulanamaz (U)`],
]));
kids.push(new Table({
  columnWidths: [W],
  width: { size: W, type: WidthType.DXA },
  rows: [new TableRow({
    children: [new TableCell({
      width: { size: W, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'FFF2CC' },
      margins: { top: 120, bottom: 120, left: 160, right: 160 },
      children: [PR([
        { t: 'K2 kritik öneme sahiptir. ', b: true },
        { t: 'Başvuru anında test istenmemiş hastalarda sonradan tanı alınıp alınmadığı, indikasyon yanlılığının değerlendirilmesi için gereklidir. Bu alanı mutlaka doldurun.' },
      ])],
    })],
  })],
}));

// ---------- L ----------
kids.push(SEC('BÖLÜM L — KALİTE KONTROL VE İMZA'));
kids.push(PR([{ t: 'L1. Bu form çift veri girişi kontrolüne dahil mi?   ', b: true },
  { t: `${BOX} Hayır    ${BOX} Evet (rastgele %10 örneklem)` }]));
kids.push(PR([{ t: 'L2. Aralık kontrolleri yapıldı mı?   ', b: true },
  { t: `${BOX} Evet   ${BOX} Hayır — açıklama: ${dots(24)}` }], { before: 100 }));
kids.push(P('(boy 30–210 cm, kilo 1–150 kg, SDS −6 ile +6 arası)', { italics: true, size: 17 }));
kids.push(P('L3. Bölüm J bağımsız kodlama', { bold: true, before: 140 }));
const lW = [3300, 2800, 1900, 1746];
kids.push(table(lW, [
  new TableRow({
    children: [cell('', lW[0], { fill: GREY }), cell('Ad Soyad', lW[1], { bold: true, fill: GREY }),
      cell('İmza', lW[2], { bold: true, fill: GREY }), cell('Tarih', lW[3], { bold: true, fill: GREY })],
  }),
  ...['1. kodlayıcı', '2. kodlayıcı', 'Uyuşmazlık çözen (gerekirse)'].map(r => new TableRow({
    children: [cell(r, lW[0]), cell('', lW[1]), cell('', lW[2]), cell('..... /..... /........', lW[3])],
  })),
]));
kids.push(PR([{ t: 'L4. Uyuşmazlık durumu:   ', b: true },
  { t: `${BOX} Uyuşmazlık yok (0)   ${BOX} Uyuşmazlık çözüldü (1)` }], { before: 140 }));
kids.push(PR([{ t: 'L5. Formu dolduran araştırmacı: ', b: true }, { t: dots(34) }], { before: 120 }));
kids.push(P(`İmza: ${dots(20)}      Tarih: ..... / ..... / ..........`, { before: 80 }));
kids.push(P('L6. Notlar / açıklamalar:', { bold: true, before: 140 }));
for (let i = 0; i < 4; i++) kids.push(P('', { rule: true, before: 120, after: 40 }));

// ---------- INSTRUCTIONS ----------
kids.push(new Paragraph({ children: [new PageBreak()] }));
kids.push(P('FORM DOLDURMA TALİMATLARI', { bold: true, size: 26, align: AlignmentType.CENTER, after: 200 }));
const instr = [
  ['Sıra önemlidir.', "Önce Bölüm A ve B'yi doldurun, ardından Bölüm C'de dahil/dışlama kararını verin. Hasta dışlanıyorsa formu C3'te bitirin ve nedeni işaretleyin — bu kayıtlar STROBE akış şeması için gereklidir."],
  ['Boş alan bırakmayın.', 'Bilgi dosyada yoksa 9, durum uygulanamıyorsa U yazın. Boş alan ile "kayıt yok" arasındaki ayrım, eksik veri analizinde belirleyicidir.'],
  ['Yaşı ay olarak girin.', 'Standart sapma skorları yaşa çok duyarlıdır; yıl cinsinden giriş hata kaynağıdır.'],
  ['ULN değerini mutlaka kaydedin (H4).', 'Laboratuvarın kit eşiği zaman içinde değişmiş olabilir; "10× ULN" ölçütü ancak bu değerle hesaplanabilir. Kit markasını da yazın.'],
  ["Bölüm J'yi tek başınıza doldurmayın.", 'İki bağımsız kodlayıcı zorunludur; aksi hâlde gözlemciler arası uyum analizi yapılamaz.'],
  ['Kimlik bilgisi yazmayın.', 'Ad, soyad, T.C. kimlik numarası, protokol numarası, dosya numarası hiçbir alana girilmez.'],
  ['Doldurulan formlar', 'kilitli dolapta saklanır; elektronik girişten sonra da imha edilmez, denetim izi olarak korunur.'],
];
instr.forEach(([h, b], i) => {
  kids.push(PR([{ t: `${i + 1}.  `, b: true }, { t: h, b: true }, { t: ' ' + b }], { before: 120, after: 60 }));
});
kids.push(P('Form sürümü: v1.0 — Değişken tanımları için colyak-bgg-veri-sozlugu.csv, çalışma protokolü için colyak-bgg-calisma-plani.md dosyalarına bakınız.',
  { italics: true, size: 17, before: 300 }));

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
      },
    },
    children: kids,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/home/user/sunu-/docs/olgu-rapor-formu.docx', buf);
  console.log('OK ->', buf.length, 'bytes');
});
