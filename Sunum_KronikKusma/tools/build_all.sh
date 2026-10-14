#!/usr/bin/env bash
# Tüm üretim + QC zinciri. Kullanım: bash tools/build_all.sh
set -euo pipefail
cd "$(dirname "$0")/.."
NP="${NODE_MODULES:?NODE_MODULES=<pptxgenjs node_modules> verin}"
SK="${PPTX_SKILL_DIR:?PPTX_SKILL_DIR=<pptx skill dizini> verin}"
python3 tools/build_refs.py
python3 tools/parse_slides.py
python3 figures/make_figures.py
NODE_PATH="$NP" PPTX_SKILL_DIR="$SK" node build_deck.js
python3 tools/fix_ppr.py output/KronikKusmaYaklasim.pptx
python3 "$SK/scripts/office/validate.py" output/KronikKusmaYaklasim.pptx
