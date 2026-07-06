#!/usr/bin/env python3
"""Çocuk gastroenteroloji kan istem formunu bağımlılıksız .docx olarak üretir."""
import zipfile
from xml.sax.saxutils import escape

NAVY = "1A3E6E"
BOX = "☐"  # ☐

# --- Tetkik grupları ---
GROUPS = [
    ("1. HEMATOLOJİ", [
        "Tam kan sayımı (Hemogram)", "Periferik yayma", "Retikülosit",
        "Sedimentasyon (ESH)", "PT / INR", "aPTT", "Fibrinojen", "Kan grubu + Rh",
    ]),
    ("2. BİYOKİMYA – TEMEL", [
        "Glukoz (açlık)", "Üre (BUN)", "Kreatinin", "AST", "ALT", "GGT", "ALP",
        "Total / Direkt bilirubin", "Total protein", "Albümin", "Na, K, Cl",
        "Kalsiyum (Ca)", "Fosfor (P)", "Magnezyum (Mg)", "Ürik asit", "LDH", "CK",
    ]),
    ("3. PANKREAS / LİPİT", [
        "Amilaz", "Lipaz", "Trigliserid", "Total kolesterol", "HDL / LDL",
    ]),
    ("4. İNFLAMASYON / İBH", [
        "CRP", "Prokalsitonin", "ANCA (p-ANCA / c-ANCA)", "ASCA (IgA / IgG)",
        "Quantiferon (TDT öncesi tarama)", "TPMT aktivitesi (azatiyoprin öncesi)",
    ]),
    ("5. ÇÖLYAK PANELİ", [
        "Total IgA", "Anti-doku transglutaminaz IgA (anti-tTG IgA)",
        "Anti-tTG IgG (IgA eksikliğinde)", "Anti-endomisyum antikoru (EMA)",
        "Deamide gliadin peptid (DGP IgA/IgG)", "HLA-DQ2 / DQ8",
    ]),
    ("6. VİTAMİN – MİNERAL / BESLENME", [
        "Demir, demir bağlama (TDBK)", "Ferritin", "Vitamin B12",
        "Folat (folik asit)", "25-OH Vitamin D", "Çinko", "Vitamin A",
        "Vitamin E", "Selenyum", "Prealbümin",
    ]),
    ("7. HORMON / METABOLİK", [
        "TSH", "Serbest T4", "HbA1c", "İnsülin (açlık)", "Parathormon (PTH)",
        "Laktat", "Amonyak",
    ]),
    ("8. HEPATİT / VİRAL SEROLOJİ", [
        "HBsAg", "Anti-HBs", "Anti-HBc IgM / total", "Anti-HAV IgM / IgG",
        "Anti-HCV", "Anti-HIV", "EBV serolojisi (VCA IgM/IgG)",
        "CMV serolojisi (IgM/IgG)",
    ]),
    ("9. KARACİĞER – İLERİ / KOLESTAZ", [
        "Seruloplazmin", "Serum bakır", "Alfa-1 antitripsin (düzey)",
        "Alfa-fetoprotein (AFP)", "Safra asitleri (açlık)", "ANA",
        "Anti-düz kas antikoru (ASMA)", "Anti-LKM-1", "IgG (otoimmün hepatit için)",
        "TORCH paneli (infantil kolestaz)",
    ]),
    ("10. İMMÜNOLOJİ / ALERJİ", [
        "İmmünoglobulinler (IgA, IgG, IgM)", "Total IgE",
        "Spesifik IgE – besin paneli (süt, yumurta, buğday…)", "Eozinofil sayısı",
    ]),
    ("11. DİĞER", [
        "H. pylori antikoru (serum)", "İlaç düzeyi: ..............................",
        "Diğer: ......................................",
        "Diğer: ......................................",
    ]),
]

PANELS = [
    "Karın ağrısı / dispepsi temel paneli", "Kronik ishal – malabsorbsiyon paneli",
    "Çölyak tarama paneli", "Transaminaz yüksekliği / hepatit paneli",
    "Kolestaz paneli", "İBH (İnflamatuvar Bağırsak Hastalığı) paneli",
    "Büyüme geriliği / beslenme paneli", "Kabızlık paneli",
]


def e(s):
    return escape(s)


def run(text, bold=False, sz=17, color=None, italic=False):
    rpr = "<w:rPr>"
    if bold:
        rpr += "<w:b/>"
    if italic:
        rpr += "<w:i/>"
    if color:
        rpr += f'<w:color w:val="{color}"/>'
    rpr += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr>'
    return f'<w:r>{rpr}<w:t xml:space="preserve">{e(text)}</w:t></w:r>'


def para(runs, sz=17, spacing_after=20, ind=None):
    ppr = f'<w:pPr><w:spacing w:after="{spacing_after}" w:line="240" w:lineRule="auto"/>'
    if ind is not None:
        ppr += f'<w:ind w:left="{ind}"/>'
    ppr += "</w:pPr>"
    return f"<w:p>{ppr}{runs}</w:p>"


def shading(color):
    return f'<w:shd w:val="clear" w:color="auto" w:fill="{color}"/>'


def group_xml(title, items):
    parts = []
    # başlık paragrafı (navy zemin)
    hdr_ppr = ('<w:pPr>'
               f'<w:shd w:val="clear" w:color="auto" w:fill="{NAVY}"/>'
               '<w:spacing w:before="40" w:after="30" w:line="240" w:lineRule="auto"/>'
               '<w:ind w:left="60" w:right="60"/></w:pPr>')
    parts.append(f'<w:p>{hdr_ppr}{run(title, bold=True, sz=17, color="FFFFFF")}</w:p>')
    for it in items:
        parts.append(para(run(BOX + "  ", sz=18) + run(it, sz=16),
                          sz=16, spacing_after=10, ind=60))
    return "".join(parts)


def cell(content, width, valign="top", fill=None, borders=True):
    tcpr = f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
    if borders:
        tcpr += ('<w:tcBorders>'
                 '<w:top w:val="single" w:sz="6" w:color="B6C3D4"/>'
                 '<w:left w:val="single" w:sz="6" w:color="B6C3D4"/>'
                 '<w:bottom w:val="single" w:sz="6" w:color="B6C3D4"/>'
                 '<w:right w:val="single" w:sz="6" w:color="B6C3D4"/></w:tcBorders>')
    if fill:
        tcpr += shading(fill)
    tcpr += ('<w:tcMar><w:top w:w="40" w:type="dxa"/><w:left w:w="70" w:type="dxa"/>'
             '<w:bottom w:w="40" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tcMar>')
    tcpr += f'<w:vAlign w:val="{valign}"/>'
    tcpr += "</w:tcPr>"
    return f"<w:tc>{tcpr}{content}</w:tc>"


def build_document():
    body = []

    # ---- BAŞLIK ----
    title_runs = run("ÇOCUK GASTROENTEROLOJİ POLİKLİNİĞİ", bold=True, sz=26, color=NAVY)
    body.append(para(title_runs, spacing_after=20))
    body.append(para(run("Kan Tetkik İstem Formu", sz=18, color="444444"), spacing_after=10))
    body.append(para(
        run("Poliklinik: Çocuk Gastroenteroloji, Hepatoloji ve Beslenme    •    Form No: ÇG-LAB-01", sz=15, color="666666"),
        spacing_after=80))

    # ---- HASTA BİLGİLERİ ----
    def hp(label, val=""):
        return para(run(label + " ", bold=True, sz=16, color=NAVY) + run(val, sz=16), sz=16, spacing_after=10)

    rows = []
    hb = [
        [("Adı Soyadı: ....................................", 5600), ("Doğum Tarihi: ..................", 3200), ("Cinsiyet: ☐ K  ☐ E", 2000)],
        [("Protokol / Dosya No: .....................", 5600), ("T.C. Kimlik No: ................", 3200), ("Açlık: ☐ Aç  ☐ Tok", 2000)],
        [("Ön Tanı / Tanı (ICD-10): ...............", 5600), ("Tarih: ..............................", 3200), ("Aciliyet: ☐ Rutin ☐ Acil", 2000)],
    ]
    for r in hb:
        cells = "".join(cell(hp("", c[0]) if False else para(run(c[0], sz=16), sz=16, spacing_after=10), c[1], fill="EEF3FA") for c in r)
        rows.append(f"<w:tr>{cells}</w:tr>")
    hasta_tbl = ('<w:tbl><w:tblPr><w:tblW w:w="10800" w:type="dxa"/>'
                 '<w:tblBorders>'
                 '<w:top w:val="single" w:sz="6" w:color="9AABBB"/>'
                 '<w:left w:val="single" w:sz="6" w:color="9AABBB"/>'
                 '<w:bottom w:val="single" w:sz="6" w:color="9AABBB"/>'
                 '<w:right w:val="single" w:sz="6" w:color="9AABBB"/>'
                 '<w:insideH w:val="single" w:sz="6" w:color="9AABBB"/>'
                 '<w:insideV w:val="single" w:sz="6" w:color="9AABBB"/></w:tblBorders></w:tblPr>'
                 + "".join(rows) + "</w:tbl>")
    body.append(hasta_tbl)
    body.append(para(run("", sz=8), spacing_after=40))

    # ---- HIZLI PANEL SEÇİMİ ----
    body.append(para(run("HIZLI PANEL SEÇİMİ", bold=True, sz=17, color=NAVY)
                     + run("  (işaretlenen panel, altındaki tüm tetkikleri kapsar)", sz=14, color="666666", italic=True),
                     spacing_after=20))
    # paneller 2 kolonlu tablo
    prows = []
    for i in range(0, len(PANELS), 2):
        c1 = para(run(BOX + "  ", sz=18) + run(PANELS[i], sz=15), sz=15, spacing_after=10)
        c2 = para(run(BOX + "  ", sz=18) + run(PANELS[i+1], sz=15), sz=15, spacing_after=10) if i+1 < len(PANELS) else para(run("", sz=15))
        prows.append(f"<w:tr>{cell(c1, 5400, fill='F6F9FD')}{cell(c2, 5400, fill='F6F9FD')}</w:tr>")
    panel_tbl = ('<w:tbl><w:tblPr><w:tblW w:w="10800" w:type="dxa"/>'
                 '<w:tblBorders><w:top w:val="single" w:sz="8" w:color="' + NAVY + '"/>'
                 '<w:left w:val="single" w:sz="8" w:color="' + NAVY + '"/>'
                 '<w:bottom w:val="single" w:sz="8" w:color="' + NAVY + '"/>'
                 '<w:right w:val="single" w:sz="8" w:color="' + NAVY + '"/></w:tblBorders></w:tblPr>'
                 + "".join(prows) + "</w:tbl>")
    body.append(panel_tbl)
    body.append(para(run("", sz=8), spacing_after=40))

    # ---- TETKİK GRUPLARI: 3 kolon ----
    col1 = GROUPS[0:3]   # hematoloji, biyokimya, pankreas
    col2 = GROUPS[3:7]   # inflamasyon, çölyak, vitamin, hormon
    col3 = GROUPS[7:11]  # hepatit, karaciğer, immünoloji, diğer

    def col_content(groups):
        out = []
        for t, items in groups:
            out.append(group_xml(t, items))
            out.append(para(run("", sz=6), spacing_after=30))
        return "".join(out)

    tetkik_tbl = ('<w:tbl><w:tblPr><w:tblW w:w="10800" w:type="dxa"/>'
                  '<w:tblBorders><w:insideV w:val="single" w:sz="2" w:color="FFFFFF"/></w:tblBorders>'
                  '<w:tblLayout w:type="fixed"/></w:tblPr>'
                  '<w:tr>'
                  + cell(col_content(col1), 3600, borders=False)
                  + cell(col_content(col2), 3600, borders=False)
                  + cell(col_content(col3), 3600, borders=False)
                  + '</w:tr></w:tbl>')
    body.append(tetkik_tbl)
    body.append(para(run("", sz=8), spacing_after=40))

    # ---- ALT: klinik not + imza ----
    note = para(run("Klinik Not / Açıklama:", bold=True, sz=16, color=NAVY), sz=16, spacing_after=20)
    note += para(run("......................................................................................", sz=16), spacing_after=20)
    note += para(run("......................................................................................", sz=16), spacing_after=20)
    imza = para(run("İsteyen Hekim", bold=True, sz=16, color=NAVY), sz=16, spacing_after=200)
    imza += para(run("Adı Soyadı / Kaşe – İmza", sz=15, color="444444"), sz=15, spacing_after=10)
    alt_tbl = ('<w:tbl><w:tblPr><w:tblW w:w="10800" w:type="dxa"/>'
               '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="B6C3D4"/>'
               '<w:left w:val="single" w:sz="6" w:color="B6C3D4"/>'
               '<w:bottom w:val="single" w:sz="6" w:color="B6C3D4"/>'
               '<w:right w:val="single" w:sz="6" w:color="B6C3D4"/>'
               '<w:insideV w:val="single" w:sz="6" w:color="B6C3D4"/></w:tblBorders></w:tblPr>'
               f'<w:tr>{cell(note, 6600)}{cell(imza, 4200, valign="center")}</w:tr></w:tbl>')
    body.append(alt_tbl)

    body.append(para(run("Tetkik seçimi klinik endikasyona göre hekim tarafından yapılır. Açlık gerektiren tetkikler (glukoz, insülin, lipit paneli, safra asitleri) için hasta aç gelmelidir.",
                         sz=13, color="777777", italic=True), spacing_after=0))

    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="567" w:right="567" w:bottom="567" w:left="567" '
            'w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>')

    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body>' + "".join(body) + sect + '</w:body></w:document>')
    return doc


CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                 '<Default Extension="xml" ContentType="application/xml"/>'
                 '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                 '</Types>')

RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>')

OUT = "/home/user/sunu-/docs/cocuk_gastro_kan_istem_formu.docx"
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CONTENT_TYPES)
    z.writestr("_rels/.rels", RELS)
    z.writestr("word/document.xml", build_document())
print("Yazıldı:", OUT)
