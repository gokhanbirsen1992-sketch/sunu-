#!/usr/bin/env bash
# PDF + slayt PNG + 2x2 paftalar. Kullanım: bash tools/render.sh <pafta_dizini>
set -euo pipefail
cd "$(dirname "$0")/../output"
SHEETS="${1:-.}"
timeout 300 python3 "$PPTX_SKILL_DIR/scripts/office/soffice.py" --headless --convert-to pdf KronikKusmaYaklasim.pptx >/dev/null 2>&1
rm -f slides_png/*.jpg
pdftoppm -jpeg -r 100 KronikKusmaYaklasim.pdf slides_png/s
python3 - "$SHEETS" <<'PY'
import glob, sys
from PIL import Image
fs = sorted(glob.glob("slides_png/s-*.jpg"))
for k in range(0, len(fs), 4):
    ims = [Image.open(f) for f in fs[k:k + 4]]
    w, h = ims[0].size
    sheet = Image.new("RGB", (w * 2 + 10, h * 2 + 10), "white")
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * (w + 10), (i // 2) * (h + 10)))
    sheet.save(f"{sys.argv[1]}/sheet_{k // 4 + 1:02d}.jpg", quality=85)
print(len(fs), "slayt")
PY
