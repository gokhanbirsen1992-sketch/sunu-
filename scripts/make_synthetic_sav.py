"""Doğrulama için sentetik sağlık/hemşirelik veri seti (.sav) üretir.

GERÇEK hasta verisi DEĞİLDİR — yalnızca boru hattını test etmek için kurgusaldır.

Çalıştırma:
  .venv/bin/python scripts/make_synthetic_sav.py sav2q1/input/ornek.sav
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sav2q1.tests.synth import make_synthetic  # noqa: E402


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "sav2q1/input/ornek.sav"
    path = make_synthetic(out)
    print(f"[synthetic] {path} yazıldı (sentetik; gerçek hasta verisi değildir)")


if __name__ == "__main__":
    main()
