"""Gruplara göre Tablo 1 ve korelasyon tablosu (ledger'dan üretilir).

Tablolar doğrudan ledger sonuçlarından kurulur (yazardan geçmez) → içerikleri
zaten temellendirilmiştir.
"""

from __future__ import annotations

from .fmt import fmt_num, fmt_p


def _val(group: dict, style: str) -> str:
    if style == "median_iqr":
        return f"{fmt_num(group['median'])} ({fmt_num(group['q1'])}–{fmt_num(group['q3'])})"
    return f"{fmt_num(group['mean'])} ± {fmt_num(group['sd'])}"


def _p_str(r: dict) -> str:
    return r.get("p_adjusted_str") or fmt_p(r["p_value"])


def build_group_table1(ledger: dict, var_labels: dict, *, title: str) -> dict | None:
    mg = [r for r in ledger["results"] if r.get("family") == "multi_group_compare"]
    if not mg:
        return None
    groups = mg[0]["groups"]
    col_labels = [g["label"] for g in groups]
    group_n = [g["n"] for g in groups]

    rows = []
    # Kategorik (ör. cinsiyet) satırları
    for r in ledger["results"]:
        if r.get("family") != "categorical":
            continue
        by_row: dict[str, dict] = {}
        for c in r["cells"]:
            by_row.setdefault(c["row"], {})[c["col"]] = c
        for rlab, cols in by_row.items():
            vals = [f"{cols.get(cl, {}).get('n', 0)} (%{fmt_num(cols.get(cl, {}).get('col_pct', 0), 1)})"
                    for cl in col_labels]
            rows.append({"label": f"{r['variables']['row']} – {rlab}", "values": vals,
                         "p": _p_str(r), "result_id": r["id"]})

    # Sürekli değişken satırları
    for r in mg:
        var = r["variables"]["outcome"]
        rows.append({"label": (var_labels.get(var) or var),
                     "values": [_val(g, r["report_style"]) for g in r["groups"]],
                     "p": _p_str(r), "result_id": r["id"]})

    return {"id": "T1", "title": title, "kind": "group_table1",
            "columns": ["Değişken"] + [f"{cl} (n={n})" for cl, n in zip(col_labels, group_n)] + ["p"],
            "rows": rows,
            "footnote": "Değerler ortalama ± SS veya ortanca (Ç1–Ç3); kategorikler n (%). "
                        "p: gruplar arası (ANOVA/Kruskal-Wallis/ki-kare); keşifsel analizlerde Benjamini-Hochberg düzeltmeli."}


def build_correlation_table(ledger: dict, var_labels: dict, *, title: str) -> dict | None:
    km = next((r for r in ledger["results"] if r.get("family") == "correlation_matrix"), None)
    if not km:
        return None
    ys = km["y_vars"]
    rows = []
    cellmap = {(c["x"], c["y"]): c for c in km["cells"]}
    for x in km["x_vars"]:
        vals = []
        for y in ys:
            c = cellmap[(x, y)]
            star = "**" if c["p"] < 0.01 else ("*" if c["p"] < 0.05 else "")
            vals.append(f"{fmt_num(c['r'])}{star}")
        rows.append({"label": (var_labels.get(x) or x), "values": vals})
    return {"id": "T2", "title": title, "kind": "correlation_table",
            "columns": ["Belirteç"] + [(var_labels.get(y) or y) for y in ys], "rows": rows,
            "footnote": "Pearson/Spearman korelasyon katsayıları. *p<0,05; **p<0,01."}
