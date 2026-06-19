"""Çoklu karşılaştırma düzeltmesi.

Doğrulayıcı hipotezler (brief'te bildirilen birincil belirteçler) düzeltmeye
GİRMEZ; geri kalan KEŞİFSEL analizlere Benjamini-Hochberg (FDR) veya Holm
uygulanır. Düzeltilmiş p ledger'a yazılır.
"""

from __future__ import annotations

from statsmodels.stats.multitest import multipletests

_METHODS = {"bh": "fdr_bh", "holm": "holm", "none": None}


def adjust_pvalues(pvals: list[float], method: str = "bh") -> list[float]:
    sm_method = _METHODS.get(method, "fdr_bh")
    if sm_method is None or not pvals:
        return list(pvals)
    _, p_adj, _, _ = multipletests(pvals, method=sm_method)
    return [float(x) for x in p_adj]
