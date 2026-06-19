"""İstatistiksel varsayım kontrolleri (normallik, varyans homojenliği, vb.).

Her test seçimi bu kontrollerin sonucuna dayanır ve gerekçesiyle birlikte
ledger'a yazılır (Yöntem dürüst yazılsın, hakem denetleyebilsin diye).
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def shapiro(x) -> dict:
    """Shapiro-Wilk normallik testi. n<3 veya n>5000 için uyarı döner."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = int(x.size)
    if n < 3:
        return {"test": "shapiro_wilk", "W": None, "p": None, "n": n, "normal": None,
                "note": "n<3, test uygulanamaz"}
    W, p = stats.shapiro(x)
    return {"test": "shapiro_wilk", "W": float(W), "p": float(p), "n": n,
            "normal": bool(p > 0.05)}


def levene(*groups, center: str = "median") -> dict:
    """Levene varyans homojenliği testi (Brown-Forsythe, center='median')."""
    arrs = [np.asarray(g, dtype=float) for g in groups]
    arrs = [a[~np.isnan(a)] for a in arrs]
    W, p = stats.levene(*arrs, center=center)
    return {"test": "levene", "center": center, "W": float(W), "p": float(p),
            "equal_variance": bool(p > 0.05)}


def normality_by_group(values, groups) -> dict:
    """Her grup için ayrı Shapiro; tüm gruplar normal mi özetini döner."""
    values = np.asarray(values, dtype=float)
    groups = np.asarray(groups)
    out = {}
    all_normal = True
    for g in [x for x in np.unique(groups) if x == x]:  # NaN'ları at
        res = shapiro(values[groups == g])
        out[str(g)] = res
        if res.get("normal") is False:
            all_normal = False
        if res.get("normal") is None:
            all_normal = None if all_normal is not False else False
    return {"per_group": out, "all_normal": all_normal}
