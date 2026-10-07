"""docs/ altındaki bağımsız sayfalardan Claude Artifact sürümlerini üretir.

docs/ tek kaynaktır. Bu betik ortak.css ve ortak.js'yi sayfaya gömer, <!doctype>/<html>/<head>/<body>
sarmalayıcılarını, manifest ve service worker bağlantılarını çıkarır.
Kullanım: python3 araclar/derle.py
"""
import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parent.parent
DOCS = KOK / "docs"
HEDEF = {
    "yabanci-cisim/index.html": "araclar/yabanci-cisim-karar/index.html",
    "eozinofilik-ozofajit/index.html": "araclar/eoe-karar/index.html",
}


def derle(kaynak: pathlib.Path) -> str:
    h = kaynak.read_text(encoding="utf-8")
    css = (DOCS / "ortak.css").read_text(encoding="utf-8")
    js = (DOCS / "ortak.js").read_text(encoding="utf-8")
    baslik = re.search(r"<title>.*?</title>", h, re.S).group(0)
    fontlar = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis[^>]*>', h).group(0)
    govde = re.search(r"<body[^>]*>(.*)</body>", h, re.S).group(1)
    arac = re.search(r'<body data-tool="(\w+)"', h).group(1)
    govde = govde.replace('<script src="../ortak.js"></script>', "<script>\n" + js + "\n</script>")
    # Artifact ortamında araçlar arası göreli bağlantılar çalışmaz: GitHub Pages adresine yönlendir.
    site = "https://gokhanbirsen1992-sketch.github.io/sunu-/"
    govde = govde.replace('href="../eozinofilik-ozofajit/', 'href="' + site + "eozinofilik-ozofajit/")
    govde = govde.replace('href="../yabanci-cisim/', 'href="' + site + "yabanci-cisim/")
    govde = govde.replace('href="../"', 'href="' + site + '"')
    return (
        baslik + "\n" + fontlar + "\n<style>\n" + css + "\n</style>\n"
        + '<script>document.body&&document.body.setAttribute("data-tool","' + arac + '");</script>\n'
        + '<div data-tool-wrap="' + arac + '">' + govde + "</div>\n"
        + '<script>document.body.setAttribute("data-tool","' + arac + '");</script>\n'
    )


if __name__ == "__main__":
    for kaynak, hedef in HEDEF.items():
        cikti = derle(DOCS / kaynak)
        yol = KOK / hedef
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(cikti, encoding="utf-8")
        print(hedef, len(cikti), "bayt")
