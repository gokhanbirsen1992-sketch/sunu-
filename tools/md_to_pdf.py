#!/usr/bin/env python3
"""Çocuk gastroenteroloji kronik hastalıklar markdown -> biçimli PDF dönüştürücü.
Türkçe karakter desteği için DejaVuSans (regular + bold) gömülür.
"""
import re
import sys
from fpdf import FPDF
from fpdf.fonts import FontFace

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
TEAL   = (13, 71, 82)
TEAL2  = (21, 101, 112)
ACCENT = (0, 137, 123)
BODY   = (45, 45, 45)
GREY   = (90, 90, 90)

INLINE = re.compile(r'\*\*(.+?)\*\*|\*(.+?)\*')

def tokenize(text):
    runs, pos = [], 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], ''))
        if m.group(1) is not None:
            runs.append((m.group(1), 'B'))
        else:
            runs.append((m.group(2), ''))   # italik fontu yok -> normal
        pos = m.end()
    if pos < len(text):
        runs.append((text[pos:], ''))
    return runs or [(text, '')]

class PDF(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, str(self.page_no()), align='C')

def write_runs(pdf, text, size, h):
    for t, style in tokenize(text):
        pdf.set_font('DejaVu', 'B' if style == 'B' else '', size)
        pdf.write(h, t)

def strip_md(text):
    return re.sub(r'\*\*?(.*?)\*\*?', r'\1', text).strip()

def render(md_path, pdf_path):
    raw = open(md_path, encoding='utf-8').read()

    pdf = PDF(format='A4')
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(auto=True, margin=16)
    for style, fname in [('', 'DejaVuSans.ttf'), ('B', 'DejaVuSans-Bold.ttf')]:
        pdf.add_font('DejaVu', style, f"{FONT_DIR}/{fname}")
    pdf.add_page()

    # blokla (boş satırlarla ayır)
    blocks, cur = [], []
    for line in raw.split('\n'):
        if line.strip() == '':
            if cur:
                blocks.append(cur); cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append(cur)

    cw = pdf.w - pdf.l_margin - pdf.r_margin

    def hr():
        y = pdf.get_y() + 1
        pdf.set_draw_color(210, 210, 210); pdf.set_line_width(0.3)
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(4)

    for blk in blocks:
        first = blk[0]

        # --- başlıklar ---
        if first.startswith('#'):
            level = len(first) - len(first.lstrip('#'))
            text = first.lstrip('#').strip()
            if level == 1:
                pdf.set_text_color(*TEAL); pdf.set_font('DejaVu', 'B', 19)
                pdf.multi_cell(0, 9, text, align='C')
                pdf.ln(1)
                pdf.set_text_color(*GREY); pdf.set_font('DejaVu', '', 10.5)
                pdf.multi_cell(0, 5.5, "Pediatrik Gastroenteroloji — Literatür Temelli Sınıflandırma", align='C')
                pdf.ln(2)
                y = pdf.get_y()
                pdf.set_draw_color(*ACCENT); pdf.set_line_width(0.6)
                pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
                pdf.ln(5)
            else:
                pdf.ln(4)
                pdf.set_text_color(*TEAL); pdf.set_font('DejaVu', 'B', 13.5)
                pdf.multi_cell(0, 7, text)
                y = pdf.get_y()
                pdf.set_draw_color(*ACCENT); pdf.set_line_width(0.5)
                pdf.line(pdf.l_margin, y + 0.5, pdf.w - pdf.r_margin, y + 0.5)
                pdf.ln(3.5)
            pdf.set_text_color(*BODY)
            continue

        # --- yatay çizgi ---
        if re.match(r'^-{3,}$', first):
            hr(); continue

        # --- tablo ---
        if first.startswith('|'):
            rows = []
            for line in blk:
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                if all(re.match(r'^:?-+:?$', c) for c in cells):
                    continue
                rows.append(cells)
            pdf.set_font('DejaVu', '', 9.5)
            pdf.set_text_color(*BODY)
            pdf.set_draw_color(205, 205, 205); pdf.set_line_width(0.2)
            head_style = FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=TEAL)
            with pdf.table(col_widths=(34, 66), text_align="LEFT",
                           headings_style=head_style, padding=2,
                           cell_fill_color=(244, 248, 248),
                           cell_fill_mode="ROWS") as table:
                for r in rows:
                    table.row(r)
            pdf.ln(3)
            continue

        # --- blockquote / not kutusu ---
        if first.startswith('>'):
            text = ' '.join(re.sub(r'^>\s?', '', l).strip() for l in blk)
            x0 = pdf.l_margin
            y0 = pdf.get_y()
            pdf.set_left_margin(x0 + 6); pdf.set_x(x0 + 6)
            pdf.set_text_color(*GREY)
            write_runs(pdf, text, 10, 5.3)
            pdf.ln(5.3)
            y1 = pdf.get_y()
            pdf.set_left_margin(x0); pdf.set_x(x0)
            pdf.set_draw_color(*ACCENT); pdf.set_line_width(1.3)
            pdf.line(x0 + 1.3, y0, x0 + 1.3, y1 - 1)
            pdf.set_text_color(*BODY)
            pdf.ln(3)
            continue

        # --- madde listesi ---
        if first.startswith('- '):
            items, buf = [], None
            for line in blk:
                if line.startswith('- '):
                    if buf is not None:
                        items.append(buf)
                    buf = line[2:].strip()
                else:
                    buf += ' ' + line.strip()
            if buf is not None:
                items.append(buf)
            for it in items:
                x0 = pdf.l_margin
                pdf.set_x(x0)
                pdf.set_font('DejaVu', '', 10.5); pdf.set_text_color(*ACCENT)
                pdf.cell(5, 5.4, '•')
                pdf.set_text_color(*BODY)
                pdf.set_left_margin(x0 + 5); pdf.set_x(x0 + 5)
                write_runs(pdf, it, 10.5, 5.4)
                pdf.ln(5.4)
                pdf.set_left_margin(x0); pdf.set_x(x0)
                pdf.ln(1.1)
            pdf.ln(0.6)
            continue

        # --- numaralı liste (kaynaklar) ---
        if re.match(r'^\d+\.\s', first):
            items, buf = [], None
            for line in blk:
                if re.match(r'^\d+\.\s', line):
                    if buf is not None:
                        items.append(buf)
                    buf = line
                else:
                    buf += ' ' + line.strip()
            if buf is not None:
                items.append(buf)
            for it in items:
                m = re.match(r'^(\d+)\.\s(.*)$', it, re.S)
                num, text = m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip()
                x0 = pdf.l_margin
                pdf.set_x(x0)
                pdf.set_font('DejaVu', '', 9.5); pdf.set_text_color(*ACCENT)
                pdf.cell(7, 5.0, f"{num}.")
                pdf.set_text_color(*BODY)
                pdf.set_left_margin(x0 + 7); pdf.set_x(x0 + 7)
                write_runs(pdf, text, 9.5, 5.0)
                pdf.ln(5.0)
                pdf.set_left_margin(x0); pdf.set_x(x0)
                pdf.ln(1.4)
            continue

        # --- tek satır kalın -> alt başlık ---
        joined = ' '.join(l.strip() for l in blk)
        if re.match(r'^\*\*.+\*\*$', joined):
            pdf.ln(1.5)
            pdf.set_font('DejaVu', 'B', 11); pdf.set_text_color(*TEAL2)
            pdf.multi_cell(0, 6, strip_md(joined))
            pdf.ln(1.5)
            pdf.set_text_color(*BODY)
            continue

        # --- normal paragraf ---
        pdf.set_text_color(*BODY)
        write_runs(pdf, joined, 10.5, 5.4)
        pdf.ln(5.4); pdf.ln(2)

    pdf.output(pdf_path)
    print(f"OK -> {pdf_path}  ({pdf.page_no()} sayfa)")

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
