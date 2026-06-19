"""Eksik veri raporu ve politika yardımcıları.

Listwise silme SESSİZCE uygulanmaz; her analizde n raporlanır. Bu veri setinde
eksiklik var (ör. crp, usg), bu yüzden eksiklik açıkça belgelenir.
"""

from __future__ import annotations


def missingness_report(df, variables: list[str] | None = None) -> dict:
    variables = variables or list(df.columns)
    n = int(len(df))
    rows = []
    for v in variables:
        miss = int(df[v].isna().sum())
        rows.append({"var": v, "n_missing": miss,
                     "pct_missing": round(100.0 * miss / n, 1) if n else 0.0})
    rows.sort(key=lambda r: r["pct_missing"], reverse=True)
    return {
        "n_rows": n,
        "n_complete_cases": int(df[variables].dropna().shape[0]),
        "variables_with_missing": [r for r in rows if r["n_missing"] > 0],
        "policy_note": "Analiz başına pairwise (mevcut vakalar); çok değişkenli regresyon listwise (n raporlanır).",
    }
