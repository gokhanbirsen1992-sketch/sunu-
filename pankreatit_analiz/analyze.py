"""
Pediatrik pankreatit hemogram indeks turetme ve siddet analizi.

Veri: data/Pankreatit_Analiz_SPSS_Fixed.xlsx
Cikti: results/*.csv, results/grafikler/*.png

Calistirma: python analyze.py
"""
from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scikit_posthocs as sp
import seaborn as sns
from scipy import stats
from sklearn.metrics import roc_auc_score, roc_curve
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "Pankreatit_Analiz_SPSS_Fixed.xlsx"
RESULTS = ROOT / "results"
FIGS = RESULTS / "grafikler"
RESULTS.mkdir(exist_ok=True)
FIGS.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")


# Hemogram parametreleri her zaman noktasi icin: 0, 24, 48 saat
HEMO_BASE = {
    "wbc": "wbc_{t}",
    "neu": "neu_{t}",
    "lenf": "lenf_{t}",
    "mono": "monosit_{t}",
    "plt": "plt_{t}",
    "hb": "hb_{t}",
    # eos: 0h sutunu eos_0, 24/48h sutunu e0s_24/e0s_48 (typo in dataset)
    "eos": {"0": "eos_0", "24": "e0s_24", "48": "e0s_48"},
}


def get_col(df: pd.DataFrame, param: str, t: str) -> pd.Series:
    """Hemogram sutununa zaman noktasiyla eris."""
    spec = HEMO_BASE[param]
    if isinstance(spec, dict):
        return df[spec[t]]
    return df[spec.format(t=t)]


def compute_indexes(df: pd.DataFrame, t: str) -> pd.DataFrame:
    """Belirli zaman noktasi (t in {'0','24','48'}) icin tum indeksleri turet."""
    wbc = get_col(df, "wbc", t)
    neu = get_col(df, "neu", t)
    lenf = get_col(df, "lenf", t)
    mono = get_col(df, "mono", t)
    plt_ = get_col(df, "plt", t)
    hb = get_col(df, "hb", t)

    out = pd.DataFrame(index=df.index)

    # 1-degiskenli (referans)
    out[f"WBC_{t}"] = wbc
    out[f"NEU_{t}"] = neu
    out[f"LENF_{t}"] = lenf
    out[f"MONO_{t}"] = mono
    out[f"PLT_{t}"] = plt_
    out[f"HB_{t}"] = hb

    # 2-degiskenli klasik
    out[f"NLR_{t}"] = neu / lenf
    out[f"PLR_{t}"] = plt_ / lenf
    out[f"LMR_{t}"] = lenf / mono
    out[f"MLR_{t}"] = mono / lenf
    out[f"NMR_{t}"] = neu / mono
    out[f"PNR_{t}"] = plt_ / neu

    # 2-degiskenli turev/varyantlar
    # dNLR: NEU / (WBC - NEU); WBC == NEU oldugunda inf — guvenli pay
    wbc_minus_neu = (wbc - neu).replace(0, np.nan)
    out[f"dNLR_{t}"] = neu / wbc_minus_neu
    out[f"HLR_{t}"] = hb / lenf
    out[f"HNR_{t}"] = hb / neu
    out[f"NHR_{t}"] = neu / hb
    out[f"MHR_{t}"] = mono / hb

    # 3-degiskenli kompozitler
    out[f"SII_{t}"] = neu * plt_ / lenf
    out[f"SIRI_{t}"] = neu * mono / lenf
    out[f"NLPR_{t}"] = neu / (lenf * plt_)
    # dSII = (WBC - LENF) * PLT / LENF (dNLR temelli SII varyanti)
    wbc_minus_lenf = wbc - lenf
    out[f"dSII_{t}"] = wbc_minus_lenf * plt_ / lenf
    out[f"dSIRI_{t}"] = wbc_minus_lenf * mono / lenf
    out[f"SIIH_{t}"] = (neu * plt_ / lenf) / hb
    out[f"HSI_{t}"] = hb * lenf / neu

    # sonsuzlari NaN yap
    out = out.replace([np.inf, -np.inf], np.nan)
    return out


# Index gruplari (yorumlama icin)
INDEX_GROUPS = {
    "1-degiskenli": ["WBC", "NEU", "LENF", "MONO", "PLT", "HB"],
    "2-degiskenli klasik": ["NLR", "PLR", "LMR", "MLR", "NMR", "PNR"],
    "2-degiskenli turev": ["dNLR", "HLR", "HNR", "NHR", "MHR"],
    "3-degiskenli kompozit": ["SII", "SIRI", "NLPR", "dSII", "dSIRI", "SIIH", "HSI"],
}
ALL_INDEX_NAMES = [n for g in INDEX_GROUPS.values() for n in g]


def median_iqr(s: pd.Series) -> str:
    s = s.dropna()
    if len(s) == 0:
        return ""
    q1, q2, q3 = np.percentile(s, [25, 50, 75])
    return f"{q2:.2f} [{q1:.2f}-{q3:.2f}]"


def descriptive_table(df: pd.DataFrame, indexes: pd.DataFrame, t: str) -> pd.DataFrame:
    """Her indeks icin siddet gruplari + tum hastalar medyan [IQR]."""
    rows = []
    sev = df["siddet"]
    for name in ALL_INDEX_NAMES:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        row = {"Index": name, "Tum (n={})".format(indexes[col].notna().sum()): median_iqr(indexes[col])}
        for g in [1, 2, 3]:
            mask = sev == g
            row[f"Siddet={g} (n={(mask & indexes[col].notna()).sum()})"] = median_iqr(indexes.loc[mask, col])
        rows.append(row)
    return pd.DataFrame(rows)


def kruskal_wallis_table(df: pd.DataFrame, indexes: pd.DataFrame, t: str) -> pd.DataFrame:
    rows = []
    sev = df["siddet"]
    for name in ALL_INDEX_NAMES:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        groups = [indexes.loc[sev == g, col].dropna().values for g in [1, 2, 3]]
        if any(len(x) < 3 for x in groups):
            rows.append({"Index": name, "KW_H": np.nan, "p": np.nan})
            continue
        H, p = stats.kruskal(*groups)
        rows.append({"Index": name, "KW_H": H, "p": p})
    out = pd.DataFrame(rows)
    if len(out) and out["p"].notna().any():
        pvals = out["p"].fillna(1).values
        _, p_adj, _, _ = multipletests(pvals, method="fdr_bh")
        out["p_FDR"] = p_adj
        out.loc[out["p"].isna(), "p_FDR"] = np.nan
    return out.sort_values("p")


def dunn_posthoc_table(df: pd.DataFrame, indexes: pd.DataFrame, t: str, sig_indexes: list[str]) -> pd.DataFrame:
    """Dunn testi: KW anlamli olan indeksler icin ikili karsilastirma."""
    rows = []
    sev = df["siddet"]
    for name in sig_indexes:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        sub = pd.DataFrame({"v": indexes[col], "g": sev}).dropna()
        if sub["g"].nunique() < 3:
            continue
        d = sp.posthoc_dunn(sub, val_col="v", group_col="g", p_adjust="bonferroni")
        rows.append({
            "Index": name,
            "p_1vs2": d.loc[1, 2],
            "p_1vs3": d.loc[1, 3],
            "p_2vs3": d.loc[2, 3],
        })
    return pd.DataFrame(rows)


def mann_whitney_table(df: pd.DataFrame, indexes: pd.DataFrame, t: str) -> pd.DataFrame:
    """Siddetli (3) vs siddetli degil (1+2)."""
    rows = []
    sev = df["siddet"]
    for name in ALL_INDEX_NAMES:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        a = indexes.loc[sev == 3, col].dropna().values
        b = indexes.loc[sev.isin([1, 2]), col].dropna().values
        if len(a) < 3 or len(b) < 3:
            rows.append({"Index": name, "U": np.nan, "p": np.nan})
            continue
        U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        rows.append({
            "Index": name,
            "n_severe": len(a),
            "n_nonsevere": len(b),
            "median_severe": np.median(a),
            "median_nonsevere": np.median(b),
            "U": U,
            "p": p,
        })
    out = pd.DataFrame(rows)
    if len(out) and out["p"].notna().any():
        pvals = out["p"].fillna(1).values
        _, p_adj, _, _ = multipletests(pvals, method="fdr_bh")
        out["p_FDR"] = p_adj
        out.loc[out["p"].isna(), "p_FDR"] = np.nan
    return out.sort_values("p")


def bootstrap_auc_ci(y_true: np.ndarray, scores: np.ndarray, n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(y_true)
    aucs = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y_true[idx])) < 2:
            continue
        aucs.append(roc_auc_score(y_true[idx], scores[idx]))
    if not aucs:
        return (np.nan, np.nan)
    return float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))


def roc_table(df: pd.DataFrame, indexes: pd.DataFrame, t: str) -> pd.DataFrame:
    """Siddetli (3) vs siddetli degil icin ROC, AUC, Youden cutoff."""
    rows = []
    y = (df["siddet"] == 3).astype(int)
    for name in ALL_INDEX_NAMES:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        x = indexes[col]
        mask = x.notna() & df["siddet"].notna()
        y_m = y[mask].values
        x_m = x[mask].values
        if y_m.sum() < 3 or (1 - y_m).sum() < 3:
            continue
        # yon: median(severe) >= median(non) ise dogrudan; degilse ters cevir
        med_s = np.median(x_m[y_m == 1])
        med_ns = np.median(x_m[y_m == 0])
        direction = 1 if med_s >= med_ns else -1
        scores = direction * x_m
        try:
            auc = roc_auc_score(y_m, scores)
        except ValueError:
            continue
        fpr, tpr, thr = roc_curve(y_m, scores)
        youden = tpr - fpr
        j = int(np.argmax(youden))
        cutoff = direction * thr[j]
        sens = tpr[j]
        spec = 1 - fpr[j]
        lo, hi = bootstrap_auc_ci(y_m, scores)
        rows.append({
            "Index": name,
            "AUC": auc,
            "AUC_95CI_low": lo,
            "AUC_95CI_high": hi,
            "yon": ">=" if direction == 1 else "<=",
            "cutoff": cutoff,
            "sensitivite": sens,
            "spesifite": spec,
        })
    out = pd.DataFrame(rows)
    return out.sort_values("AUC", ascending=False)


def spearman_table(df: pd.DataFrame, indexes: pd.DataFrame, t: str) -> pd.DataFrame:
    rows = []
    sev = df["siddet"]
    for name in ALL_INDEX_NAMES:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        mask = indexes[col].notna() & sev.notna()
        if mask.sum() < 10:
            continue
        rho, p = stats.spearmanr(indexes.loc[mask, col], sev[mask])
        rows.append({"Index": name, "Spearman_rho": rho, "p": p})
    out = pd.DataFrame(rows)
    if len(out):
        _, p_adj, _, _ = multipletests(out["p"].values, method="fdr_bh")
        out["p_FDR"] = p_adj
    return out.sort_values("p")


def ordinal_logistic_table(df: pd.DataFrame, indexes: pd.DataFrame, t: str, top_names: list[str]) -> pd.DataFrame:
    """Yas + cinsiyet ayarli ordinal lojistik regresyon (her indeks ayri model)."""
    rows = []
    sev = df["siddet"]
    age = df["YAS"]
    sex = (df["CINS"].astype(str).str.upper() == "ERKEK").astype(int)  # 1=erkek
    for name in top_names:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        x = indexes[col]
        sub = pd.DataFrame({"y": sev, "x": x, "age": age, "sex": sex}).dropna()
        if sub.empty:
            continue
        # log-doneusum sag-carpik degerler icin
        sub["x_z"] = stats.zscore(np.log1p(sub["x"] - sub["x"].min() + 1))
        try:
            model = OrderedModel(sub["y"], sub[["x_z", "age", "sex"]], distr="logit")
            res = model.fit(method="bfgs", disp=False)
            or_ = np.exp(res.params["x_z"])
            ci = np.exp(res.conf_int().loc["x_z"])
            p = res.pvalues["x_z"]
            rows.append({"Index": name, "OR_per_1SD_log": or_, "OR_95CI_low": ci[0], "OR_95CI_high": ci[1], "p": p})
        except Exception as e:
            rows.append({"Index": name, "OR_per_1SD_log": np.nan, "OR_95CI_low": np.nan, "OR_95CI_high": np.nan, "p": np.nan, "error": str(e)})
    return pd.DataFrame(rows)


def delta_analysis(df: pd.DataFrame, ix0: pd.DataFrame, ix24: pd.DataFrame, ix48: pd.DataFrame) -> pd.DataFrame:
    """delta_24 = X24 - X0; delta_48 = X48 - X0. KW + Mann-Whitney."""
    rows = []
    sev = df["siddet"]
    for name in ALL_INDEX_NAMES:
        c0, c24, c48 = f"{name}_0", f"{name}_24", f"{name}_48"
        for label, src, base in [("delta_24", ix24[c24] if c24 in ix24 else None, ix0[c0]),
                                  ("delta_48", ix48[c48] if c48 in ix48 else None, ix0[c0])]:
            if src is None:
                continue
            delta = src - base
            # KW 3'lu
            groups = [delta[(sev == g) & delta.notna()].values for g in [1, 2, 3]]
            if any(len(x) < 3 for x in groups):
                continue
            H, p_kw = stats.kruskal(*groups)
            # Mann-Whitney 2'li (sid=3 vs 1+2)
            a = delta[(sev == 3) & delta.notna()].values
            b = delta[sev.isin([1, 2]) & delta.notna()].values
            if len(a) >= 3 and len(b) >= 3:
                U, p_mw = stats.mannwhitneyu(a, b, alternative="two-sided")
            else:
                p_mw = np.nan
            rows.append({
                "Index": name,
                "delta": label,
                "n": int(delta.notna().sum()),
                "median_severe": np.median(a) if len(a) else np.nan,
                "median_nonsevere": np.median(b) if len(b) else np.nan,
                "KW_H": H,
                "p_KW": p_kw,
                "p_MW_3vs1+2": p_mw,
            })
    return pd.DataFrame(rows).sort_values("p_KW")


def naples_comparison(df: pd.DataFrame, top_roc: pd.DataFrame) -> pd.DataFrame:
    """Naples skoru (0h) ile en iyi 5 yeni indeksin AUC karsilastirmasi (siddetli vs degil)."""
    rows = []
    y = (df["siddet"] == 3).astype(int)
    # Naples skoru
    if "naples" in df.columns:
        x = df["naples"]
        mask = x.notna() & df["siddet"].notna()
        if mask.sum() and y[mask].sum() >= 3:
            auc = roc_auc_score(y[mask], x[mask])
            lo, hi = bootstrap_auc_ci(y[mask].values, x[mask].values)
            rows.append({"Index": "Naples_skoru", "AUC": auc, "AUC_95CI_low": lo, "AUC_95CI_high": hi, "n": int(mask.sum())})
    return pd.DataFrame(rows)


# ----- Gorseller -----

def boxplot_top_indexes(df: pd.DataFrame, indexes: pd.DataFrame, names: list[str], t: str, fname: str, title: str):
    n = len(names)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), squeeze=False)
    for i, name in enumerate(names):
        ax = axes[i // cols, i % cols]
        col = f"{name}_{t}"
        sub = pd.DataFrame({"deger": indexes[col], "Siddet": df["siddet"]}).dropna()
        sub["Siddet"] = sub["Siddet"].astype(int)
        sns.boxplot(data=sub, x="Siddet", y="deger", ax=ax, palette="Set2", showfliers=False)
        sns.stripplot(data=sub, x="Siddet", y="deger", ax=ax, color="black", size=2, alpha=0.4)
        ax.set_title(name)
        ax.set_xlabel("Siddet (1=hafif, 2=orta, 3=siddetli)")
        ax.set_ylabel(name)
    # bos eksenleri sil
    for j in range(n, rows * cols):
        fig.delaxes(axes[j // cols, j % cols])
    fig.suptitle(title, y=1.02, fontsize=14)
    fig.tight_layout()
    fig.savefig(FIGS / fname, dpi=130, bbox_inches="tight")
    plt.close(fig)


def roc_plot_top(df: pd.DataFrame, indexes: pd.DataFrame, names_directions: list[tuple[str, int]], t: str, fname: str, title: str, naples: bool = False):
    fig, ax = plt.subplots(figsize=(7, 6))
    y = (df["siddet"] == 3).astype(int)
    for name, direction in names_directions:
        col = f"{name}_{t}"
        if col not in indexes.columns:
            continue
        x = indexes[col]
        mask = x.notna() & df["siddet"].notna()
        scores = direction * x[mask].values
        try:
            fpr, tpr, _ = roc_curve(y[mask], scores)
            auc = roc_auc_score(y[mask], scores)
        except Exception:
            continue
        ax.plot(fpr, tpr, lw=2, label=f"{name} (AUC={auc:.2f})")
    if naples and "naples" in df.columns:
        xn = df["naples"]
        mask = xn.notna() & df["siddet"].notna()
        try:
            fpr, tpr, _ = roc_curve(y[mask], xn[mask])
            auc = roc_auc_score(y[mask], xn[mask])
            ax.plot(fpr, tpr, lw=2, ls="--", color="black", label=f"Naples (AUC={auc:.2f})")
        except Exception:
            pass
    ax.plot([0, 1], [0, 1], color="gray", lw=1, ls=":")
    ax.set_xlabel("1 - Spesifite (Yanlis pozitif orani)")
    ax.set_ylabel("Sensitivite (Dogru pozitif orani)")
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGS / fname, dpi=130, bbox_inches="tight")
    plt.close(fig)


# ----- Ana akis -----

def main():
    print(f"Veri okuma: {DATA_FILE}")
    df = pd.read_excel(DATA_FILE)
    print(f"  Boyut: {df.shape}")
    print(f"  Siddet dagilimi: {df['siddet'].value_counts(dropna=False).to_dict()}")

    # Indeksleri 3 zaman noktasi icin hesapla
    ix0 = compute_indexes(df, "0")
    ix24 = compute_indexes(df, "24")
    ix48 = compute_indexes(df, "48")

    # Tum indeks frame'i (rapor/CSV icin)
    full = pd.concat([df[["KABUL_NO", "YAS", "CINS", "siddet", "naples"]], ix0, ix24, ix48], axis=1)
    full.to_csv(RESULTS / "tum_indeksler.csv", index=False)

    # ---- 0h analizleri ----
    print("\n[0h] Tanimlayici tablo")
    desc0 = descriptive_table(df, ix0, "0")
    desc0.to_csv(RESULTS / "tablo1_tanimlayici_0h.csv", index=False)

    print("[0h] Kruskal-Wallis")
    kw0 = kruskal_wallis_table(df, ix0, "0")
    kw0.to_csv(RESULTS / "tablo2_kruskal_wallis_0h.csv", index=False)
    sig0 = kw0.loc[kw0["p"] < 0.05, "Index"].tolist()
    print(f"  KW p<0.05: {len(sig0)} indeks")

    print("[0h] Dunn post-hoc")
    dunn0 = dunn_posthoc_table(df, ix0, "0", sig0)
    dunn0.to_csv(RESULTS / "tablo3_dunn_posthoc_0h.csv", index=False)

    print("[0h] Mann-Whitney (siddetli vs degil)")
    mw0 = mann_whitney_table(df, ix0, "0")
    mw0.to_csv(RESULTS / "tablo4_mann_whitney_0h.csv", index=False)

    print("[0h] ROC / AUC")
    roc0 = roc_table(df, ix0, "0")
    roc0.to_csv(RESULTS / "tablo5_roc_auc_0h.csv", index=False)
    top5_roc = roc0.head(5)

    print("[0h] Spearman")
    sp0 = spearman_table(df, ix0, "0")
    sp0.to_csv(RESULTS / "tablo6_spearman_0h.csv", index=False)

    print("[0h] Ordinal lojistik (top 8 by AUC)")
    top8 = roc0.head(8)["Index"].tolist()
    ord0 = ordinal_logistic_table(df, ix0, "0", top8)
    ord0.to_csv(RESULTS / "tablo7_ord_logistic_0h.csv", index=False)

    # ---- 24h / 48h analizleri (kisa) ----
    print("\n[24h] KW + Mann-Whitney + ROC")
    kw24 = kruskal_wallis_table(df, ix24, "24"); kw24.to_csv(RESULTS / "tablo2_kruskal_wallis_24h.csv", index=False)
    mw24 = mann_whitney_table(df, ix24, "24"); mw24.to_csv(RESULTS / "tablo4_mann_whitney_24h.csv", index=False)
    roc24 = roc_table(df, ix24, "24"); roc24.to_csv(RESULTS / "tablo5_roc_auc_24h.csv", index=False)

    print("[48h] KW + Mann-Whitney + ROC")
    kw48 = kruskal_wallis_table(df, ix48, "48"); kw48.to_csv(RESULTS / "tablo2_kruskal_wallis_48h.csv", index=False)
    mw48 = mann_whitney_table(df, ix48, "48"); mw48.to_csv(RESULTS / "tablo4_mann_whitney_48h.csv", index=False)
    roc48 = roc_table(df, ix48, "48"); roc48.to_csv(RESULTS / "tablo5_roc_auc_48h.csv", index=False)

    # ---- Delta ----
    print("\n[delta] 0->24 ve 0->48 degisim")
    delta = delta_analysis(df, ix0, ix24, ix48)
    delta.to_csv(RESULTS / "tablo8_delta.csv", index=False)

    # ---- Naples kiyas ----
    print("\nNaples skoru kiyas")
    naples = naples_comparison(df, top5_roc)
    kiyas = pd.concat([naples, top5_roc[["Index", "AUC", "AUC_95CI_low", "AUC_95CI_high"]].assign(n=lambda d: df["siddet"].notna().sum())], ignore_index=True)
    kiyas.to_csv(RESULTS / "tablo9_naples_kiyas.csv", index=False)

    # ---- Gorseller ----
    print("\nGorseller olusturuluyor")
    top5_names = top5_roc["Index"].tolist()
    boxplot_top_indexes(df, ix0, top5_names, "0", "fig1_boxplot_top5_0h.png", "0h: En yuksek AUC'li 5 indeks - siddet gruplari")
    names_dirs = [(r["Index"], 1 if r["yon"] == ">=" else -1) for _, r in top5_roc.iterrows()]
    roc_plot_top(df, ix0, names_dirs, "0", "fig2_roc_top5_0h.png", "0h: ROC egrileri (siddetli vs siddetli degil)", naples=True)

    # delta gorseli: en anlamli 3 delta indeksi
    top3_delta = delta.dropna(subset=["p_KW"]).head(3)
    if len(top3_delta) > 0:
        fig, axes = plt.subplots(1, len(top3_delta), figsize=(5 * len(top3_delta), 4), squeeze=False)
        for i, (_, r) in enumerate(top3_delta.iterrows()):
            name = r["Index"]; tlabel = r["delta"]
            t_target = "24" if tlabel == "delta_24" else "48"
            ix_t = ix24 if t_target == "24" else ix48
            delta_vals = ix_t[f"{name}_{t_target}"] - ix0[f"{name}_0"]
            sub = pd.DataFrame({"deger": delta_vals, "Siddet": df["siddet"]}).dropna()
            sub["Siddet"] = sub["Siddet"].astype(int)
            ax = axes[0, i]
            sns.boxplot(data=sub, x="Siddet", y="deger", ax=ax, palette="Set3", showfliers=False)
            sns.stripplot(data=sub, x="Siddet", y="deger", ax=ax, color="black", size=2, alpha=0.4)
            ax.set_title(f"{name} {tlabel}")
            ax.axhline(0, color="red", lw=0.8, ls="--")
            ax.set_xlabel("Siddet")
            ax.set_ylabel(f"{name} degisimi")
        fig.suptitle("Dinamik degisim: en anlamli 3 indeks-delta cifti", y=1.02)
        fig.tight_layout()
        fig.savefig(FIGS / "fig3_boxplot_delta.png", dpi=130, bbox_inches="tight")
        plt.close(fig)

    # Naples vs en iyi 3 yeni indeks ROC
    top3_names = top5_roc.head(3)
    names_dirs3 = [(r["Index"], 1 if r["yon"] == ">=" else -1) for _, r in top3_names.iterrows()]
    roc_plot_top(df, ix0, names_dirs3, "0", "fig4_naples_vs_yeni.png", "Naples vs en iyi 3 yeni hemogram indeksi", naples=True)

    print("\nBitti. Sonuclar: results/")
    print("\nEn yuksek AUC (0h):")
    print(roc0.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
