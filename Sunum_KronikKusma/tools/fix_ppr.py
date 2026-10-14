#!/usr/bin/env python3
"""pptxgenjs 3.12 her metin parçası için ayrı <a:pPr> yazar; aynı paragraftaki 2., 3. pPr'ler
(ör. <a:buNone/>) madde işaretini siler ve OOXML sırasını bozar. Her <a:p> içinde yalnız ilk pPr kalır.
Kullanım: python tools/fix_ppr.py output/X.pptx (yerinde düzenler)."""
import re
import shutil
import sys
import tempfile
import zipfile

PPR = re.compile(r"<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>", re.S)
PARA = re.compile(r"<a:p>.*?</a:p>", re.S)


def fix_para(m):
    p = m.group(0)
    found = list(PPR.finditer(p))
    if len(found) <= 1:
        return p
    keep_end = found[0].end()
    return p[:keep_end] + PPR.sub("", p[keep_end:])


def main(path):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx").name
    n = 0
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.match(r"ppt/slides/slide\d+\.xml$", item.filename):
                xml = data.decode("utf-8")
                new = PARA.sub(fix_para, xml)
                n += xml != new
                data = new.encode("utf-8")
            zout.writestr(item, data)
    shutil.move(tmp, path)
    print(f"pPr düzeltildi: {n} slayt")


if __name__ == "__main__":
    main(sys.argv[1])
