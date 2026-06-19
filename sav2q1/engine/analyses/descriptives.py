"""Tanımlayıcı istatistikler → ledger 'descriptives' girdileri.

Her girdi, raporlanabilir hazır string'leri (`apa_*`) ve `_tokens` (yazarların
kullanabileceği sayı token'ları) içerir. Yerel biçim burada KESİNLEŞİR.
"""

from __future__ import annotations

from ..fmt import fmt_num, fmt_pct


def describe_continuous(var: str, label: str, s: dict) -> dict:
    mean_s, sd_s = fmt_num(s["mean"]), fmt_num(s["sd"])
    median_s = fmt_num(s["median"])
    q1_s, q3_s = fmt_num(s["q1"]), fmt_num(s["q3"])
    min_s, max_s = fmt_num(s["min"]), fmt_num(s["max"])
    return {
        "id": f"desc.{var}",
        "var": var,
        "label": label,
        "type": "continuous",
        "n": s.get("n"),
        "mean": s["mean"], "sd": s["sd"], "median": s["median"],
        "q1": s["q1"], "q3": s["q3"], "min": s["min"], "max": s["max"],
        "apa_mean_sd": f"{mean_s} ± {sd_s}",
        "apa_median_iqr": f"{median_s} ({q1_s}–{q3_s})",
        "apa_range": f"{min_s}–{max_s}",
        # Yazarların kullanabileceği render edilmiş string'ler (number_index buradan taranır):
        "_display": [f"{mean_s} ± {sd_s}", f"{median_s} ({q1_s}–{q3_s})", f"{min_s}–{max_s}"],
        "_global": [str(s.get("n"))] if s.get("n") is not None else [],
    }


def describe_categorical(var: str, label: str, s: dict) -> dict:
    cats_out = []
    display: list[str] = []
    for c in s["categories"]:
        pct_s = fmt_pct(c["pct"])
        n_s = str(c["n"])
        apa = f"{n_s} (%{pct_s})"
        cats_out.append({**c, "apa": apa})
        display.append(apa)
    return {
        "id": f"desc.{var}",
        "var": var,
        "label": label,
        "type": "categorical",
        "total": s.get("total"),
        "categories": cats_out,
        "_display": display,
        "_global": [str(s.get("total"))] if s.get("total") is not None else [],
    }


def build_descriptives(profile: dict, include: list[str] | None = None) -> list[dict]:
    """dataset_profile.json'dan tanımlayıcı ledger girdileri üretir."""
    out = []
    for v in profile["variables"]:
        if include is not None and v["name"] not in include:
            continue
        if v["role"] in ("id", "constant", "unknown"):
            continue
        s = dict(v["summary"]); s["n"] = v["n"] - v["n_missing"]
        if v["role"] == "continuous":
            out.append(describe_continuous(v["name"], v["label"], s))
        else:
            out.append(describe_categorical(v["name"], v["label"], s))
    return out
