"""Kendi-kendine yeten Google Colab not defteri üretir (SPSS_Makale_Uretici.ipynb).

`sav2q1` paketini base64 tarball olarak not defterine GÖMER; böylece repoya erişim
gerekmeden herhangi bir Colab oturumunda (hatta iPhone Safari'de) çalışır:
.sav yükle → makale üret → Word indir. Ücretsiz, kurulumsuz, sunucusuz.

Çalıştırma: .venv/bin/python scripts/build_colab.py
"""

from __future__ import annotations

import base64
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "colab" / "SPSS_Makale_Uretici.ipynb"
EXCLUDE = {"runs", "input", "__pycache__", "tests", "examples", ".pytest_cache"}


def _pkg_b64() -> str:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for p in sorted((ROOT / "sav2q1").rglob("*")):
            if any(part in EXCLUDE for part in p.relative_to(ROOT).parts):
                continue
            if p.is_file() and p.suffix in (".py", ".json", ".yaml", ".txt", ".md"):
                tar.add(p, arcname=str(p.relative_to(ROOT)))
    return base64.b64encode(buf.getvalue()).decode()


def _md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def _code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.splitlines(keepends=True)}


def build() -> None:
    pkg = _pkg_b64()
    cells = [
        _md("# 📊 SPSS → Makale Üretici\n"
            "\n"
            "SPSS **.sav** dosyanızdan **Türkçe akademik makale taslağı (Word)** üretir.\n"
            "Ücretsiz, kurulumsuz, sunucusuz — iPhone Safari'de bile çalışır.\n"
            "\n"
            "**Kullanım:** Üstten **Çalışma Zamanı → Tümünü Çalıştır** (Runtime → Run all). "
            "Sonra `.sav` dosyanızı seçin; biraz bekleyin; Word otomatik inecek.\n"
            "\n"
            "Sayılar istatistik motorundan **birebir** gelir (uydurma yok); kimlik/PII değişkenleri "
            "otomatik dışlanır ve veriniz yalnızca bu oturumda kalır.\n"),
        _code("#@title 1) Gerekli kütüphaneleri kur (1-2 dk)\n"
              "!pip -q install pyreadstat pingouin scikit-posthocs factor_analyzer python-docx "
              "jsonschema tabulate httpx 2>/dev/null\n"
              "print('Kurulum tamam.')\n"),
        _code("#@title 2) Makale motorunu yükle (pakete gömülü)\n"
              "import base64, io, tarfile, sys\n"
              f"_PKG = \"{pkg}\"\n"
              "tarfile.open(fileobj=io.BytesIO(base64.b64decode(_PKG)), mode='r:gz').extractall('/content')\n"
              "sys.path.insert(0, '/content')\n"
              "import sav2q1; print('Motor yüklendi, sürüm', sav2q1.__version__)\n"),
        _code("#@title 3) SPSS .sav yükle → Makale üret → Word indir\n"
              "with_pubmed = False  #@param {type:'boolean'}\n"
              "konu = ''  #@param {type:'string'}\n"
              "from google.colab import files\n"
              "from sav2q1.pipeline import generate_article\n"
              "print('SPSS .sav dosyanızı seçin…')\n"
              "up = files.upload()\n"
              "sav_name = list(up.keys())[0]\n"
              "brief = {'topic': konu} if konu.strip() else None\n"
              "res = generate_article(sav_name, '/content/run', brief=brief, with_pubmed=with_pubmed)\n"
              "print('\\nGruplama değişkeni:', res['group_var'], '| Sonuç:', res['n_results'],\n"
              "      '| Sayı doğrulama:', res['gate'].get('numeric'))\n"
              "print('Word indiriliyor…')\n"
              "files.download(res['docx'])\n"),
        _md("---\n"
            "**Notlar:** Etik kurul no, finansman ve yazar alanları Word'de `[köşeli parantez]` ile "
            "işaretlidir; siz doldurun. **Gerçek PubMed kaynakları** için 3. hücrede `with_pubmed`'i "
            "işaretleyip bir **konu** yazın (ör. *nonalcoholic fatty liver children*).\n"),
    ]
    nb = {"cells": cells, "metadata": {"colab": {"name": "SPSS Makale Üretici", "provenance": []},
          "kernelspec": {"name": "python3", "display_name": "Python 3"},
          "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[colab] {OUT} yazıldı ({OUT.stat().st_size // 1024} KB, gömülü paket {len(pkg)//1024} KB b64)")


if __name__ == "__main__":
    build()
