"""Deterministik şekil üretimi (matplotlib, 300 dpi). Türkçe etiketler.

Bu makale için: 3 belirtecin gruplara göre kutu grafiği + sitrülin↔karaciğer
yağı saçılımı (regresyon doğrusuyla).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def _glabels(value_labels, codes):
    out = []
    for c in codes:
        lab = str(c)
        if value_labels:
            for k, v in value_labels.items():
                try:
                    if float(k) == float(c):
                        lab = str(v); break
                except (TypeError, ValueError):
                    pass
        out.append(lab)
    return out


def make_marker_boxplots(df, group_var, markers, value_labels, var_labels, outdir,
                         fid="F1", title="Şekil 1. Bağırsak bariyeri belirteçlerinin gruplara göre dağılımı") -> dict:
    codes = sorted(df[group_var].dropna().unique())
    glabels = _glabels(value_labels, codes)
    fig, axes = plt.subplots(1, len(markers), figsize=(4 * len(markers), 4))
    if len(markers) == 1:
        axes = [axes]
    for ax, m in zip(axes, markers):
        pairs = [(lab, df.loc[df[group_var] == c, m].dropna().to_numpy())
                 for c, lab in zip(codes, glabels)]
        pairs = [(lab, arr) for lab, arr in pairs if arr.size > 0]   # boş grupları ele
        if not pairs:
            ax.set_axis_off(); continue
        labs2 = [p[0] for p in pairs]; data = [p[1] for p in pairs]
        try:
            ax.boxplot(data, tick_labels=labs2)            # matplotlib >= 3.9
        except TypeError:
            ax.boxplot(data, labels=labs2)                 # eski matplotlib (Colab)
        ax.set_title((var_labels.get(m) or m))
        ax.set_ylabel((var_labels.get(m) or m))
        ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    path = Path(outdir) / f"{fid}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return {"id": fid, "file": f"figures/{fid}.png", "title": title, "kind": "boxplot"}


def make_scatter(df, x, y, var_labels, outdir, fid="F2",
                 title="Şekil 2. Sitrülin ile karaciğer yağ oranı ilişkisi") -> dict:
    sub = df[[x, y]].dropna()
    xv = sub[x].to_numpy(float); yv = sub[y].to_numpy(float)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(xv, yv, s=16, alpha=0.6, edgecolor="none")
    if len(sub) > 2:
        coef = np.polyfit(xv, yv, 1)
        xs = np.linspace(xv.min(), xv.max(), 50)
        ax.plot(xs, coef[0] * xs + coef[1], color="crimson", lw=1.5)
    ax.set_xlabel((var_labels.get(x) or x))
    ax.set_ylabel((var_labels.get(y) or y))
    fig.tight_layout()
    path = Path(outdir) / f"{fid}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return {"id": fid, "file": f"figures/{fid}.png", "title": title, "kind": "scatter"}
