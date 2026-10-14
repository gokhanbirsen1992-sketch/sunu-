#!/usr/bin/env python3
"""Onaylı research/slides_content.md → research/slides.json (deck üreticisinin tek içerik kaynağı).

Her slayt: id, title, bullets/numbered/table/dipnot/etiket/gri/gorsel. Her metin "runs" listesidir:
{"t": metin, "b": kalın?} ya da {"cite": [n, ...]} — n, references/ref_order.json'daki numaradır.
Böylece deck'teki her cümle Kapı 2'de onaylanan metinle birebir aynı kalır; kaynak numarası elle yazılmaz."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = {r["pmid"]: r["n"] for r in json.loads((ROOT / "references" / "ref_order.json").read_text(encoding="utf-8"))}
TOKEN = re.compile(r"(\[@[\d;\s@]+\]|\*\*.+?\*\*)")


def runs(text):
    out = []
    for part in TOKEN.split(text.strip()):
        if not part:
            continue
        if part.startswith("[@"):
            nums = [REF[p] for p in re.findall(r"\d+", part)]
            out.append({"cite": nums})
        elif part.startswith("**"):
            out.append({"t": part[2:-2], "b": True})
        else:
            out.append({"t": part, "b": False})
    # alıntı öncesi boşluğu temizle
    for i, r in enumerate(out):
        if "cite" in r and i > 0 and "t" in out[i - 1]:
            out[i - 1]["t"] = out[i - 1]["t"].rstrip()
    return out


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def main():
    text = (ROOT / "research" / "slides_content.md").read_text(encoding="utf-8")
    slides = []
    for blk in re.split(r"\n### ", text)[1:]:
        head, _, body = blk.partition("\n")
        sid, _, title = head.partition(" · ")
        title = re.sub(r"\s*\((TABLO|GÖRSEL|3 SÜTUN|görsel harita)\)\s*$", "", title.strip())
        s = {"id": sid.strip(), "title": title, "bullets": [], "numbered": [], "table": [],
             "dipnot": None, "etiket": None, "gri": None, "gorsel": None, "cites": []}
        for line in body.splitlines():
            ln = line.strip()
            if not ln or ln.startswith("---") or ln.startswith("## "):
                continue
            if ln.startswith("Dayanak:"):
                continue
            if ln.startswith("- "):
                s["bullets"].append(runs(ln[2:]))
            elif re.match(r"\d+\. ", ln):
                s["numbered"].append(runs(re.sub(r"^\d+\. ", "", ln)))
            elif ln.startswith("|"):
                if re.match(r"^\|[\s\-|]+\|$", ln):
                    continue
                s["table"].append([runs(c) for c in cells(ln)])
            elif ln.startswith("Dipnot:"):
                s["dipnot"] = runs(ln[len("Dipnot:"):])
            elif ln.startswith("Etiket:"):
                s["etiket"] = ln[len("Etiket:"):].strip()
            elif ln.startswith("Gri kutu"):
                s["gri"] = runs(re.sub(r"^Gri kutu[^:]*:\s*", "", ln))
                m = re.match(r'^Gri kutu — "([^"]+)":', ln)
                s["gri_title"] = m.group(1) if m else None
            elif ln.startswith("Görsel:"):
                s["gorsel"] = ln[len("Görsel:"):].strip()
            elif ln.startswith("[@"):
                s["cites_line"] = runs(ln)
            else:
                s.setdefault("other", []).append(ln)
        all_n = sorted({n for r in json.dumps(s) and re.findall(r'"cite": \[([\d, ]+)\]', json.dumps(s))
                        for n in map(int, r.split(","))})
        s["cites"] = all_n
        slides.append(s)
    (ROOT / "research" / "slides.json").write_text(json.dumps(slides, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(slides)} slayt bloğu → research/slides.json")
    for s in slides:
        if s.get("other"):
            print("  sınıflanmamış satır:", s["id"], s["other"])


if __name__ == "__main__":
    main()
