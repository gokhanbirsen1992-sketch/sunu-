from __future__ import annotations

import io
from typing import get_args

import pandas as pd
import streamlit as st

from core.auto_typer import VarType, profile_columns, to_dataframe
from core.bivariate import run_bivariate
from core.data_loader import impute, load_dataframe, missing_summary
from core.literature import search_for_findings
from core.multivariate import auto_multivariate
from core.report import build_markdown, llm_article_ideas
from core.survival import run_cox, run_kaplan_meier


VAR_TYPES = list(get_args(VarType))
STEPS = [
    "1️⃣ Veri Yükle",
    "2️⃣ Sütun Tipleri",
    "3️⃣ Outcome & Çalışma Tipi",
    "4️⃣ Bivariate",
    "5️⃣ Multivariate / Sağkalım",
    "6️⃣ Literatür",
    "7️⃣ Rapor",
]

st.set_page_config(page_title="Otomatik İstatistik & Literatür", layout="wide")
st.title("📊 Otomatik İstatistik → Literatür → Makale Fikri")


def _init_state():
    defaults = {
        "df": None, "filename": None, "types": {}, "outcome": None,
        "study_type": None, "time_col": None, "event_col": None,
        "missing_strategy": "yok", "bivariate": None, "multivariate": None,
        "survival_km": None, "survival_cox": None, "literature": None,
        "report_md": None, "step": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()

with st.sidebar:
    st.header("Akış")
    for i, s in enumerate(STEPS):
        marker = "▶️" if i == st.session_state.step else ("✅" if i < st.session_state.step else "  ")
        st.write(f"{marker} {s}")
    st.divider()
    st.markdown("**API anahtarları (opsiyonel)**")
    pubmed_key = st.text_input("PubMed API key", type="password", key="pubmed_key",
                               help="https://www.ncbi.nlm.nih.gov/account/")
    anthropic_key = st.text_input("Anthropic API key", type="password", key="anthropic_key",
                                  help="LLM ile makale fikri üretimi için")


def _next():
    st.session_state.step = min(st.session_state.step + 1, len(STEPS) - 1)


def _back():
    st.session_state.step = max(st.session_state.step - 1, 0)


# ---- STEP 1: Veri Yükle ----
if st.session_state.step == 0:
    st.header(STEPS[0])
    st.write("Desteklenen formatlar: **CSV, TSV, XLSX, SPSS (.sav), Stata (.dta)**")
    up = st.file_uploader("Veri dosyası", type=["csv", "tsv", "xlsx", "xls", "sav", "dta"])
    if up is not None:
        try:
            df = load_dataframe(up, filename=up.name)
            st.session_state.df = df
            st.session_state.filename = up.name
            st.success(f"✅ Yüklendi: **{up.name}** — {df.shape[0]} satır × {df.shape[1]} sütun")
            st.dataframe(df.head(20))

            st.subheader("Eksik Veri Özeti")
            miss = missing_summary(df)
            st.dataframe(miss)

            strategy = st.radio("Eksik veri stratejisi",
                                ["yok (analiz sırasında dropna)", "median_mode (median + mode)", "mean"],
                                horizontal=True)
            st.session_state.missing_strategy = strategy.split(" ")[0]
            if st.session_state.missing_strategy != "yok":
                st.session_state.df = impute(df, strategy=st.session_state.missing_strategy)
                st.info(f"Imputation uygulandı: {st.session_state.missing_strategy}")
        except Exception as e:
            st.error(f"Yükleme hatası: {e}")

    if st.session_state.df is not None:
        st.button("Sonraki adım →", on_click=_next, type="primary")


# ---- STEP 2: Sütun Tipleri ----
elif st.session_state.step == 1:
    st.header(STEPS[1])
    df = st.session_state.df
    if df is None:
        st.warning("Önce veri yükleyin.")
    else:
        infos = profile_columns(df)
        st.write("Otomatik tespit edilen tipler. **Yanlış olanları düzeltin.**")
        editable = to_dataframe(infos)
        editable["override"] = editable["type"]
        edited = st.data_editor(
            editable, column_config={
                "override": st.column_config.SelectboxColumn("Tip", options=VAR_TYPES, required=True),
                "type": st.column_config.TextColumn("Otomatik", disabled=True),
            },
            hide_index=True, use_container_width=True,
        )
        st.session_state.types = dict(zip(edited["column"], edited["override"]))

    c1, c2 = st.columns(2)
    c1.button("← Geri", on_click=_back)
    c2.button("Sonraki adım →", on_click=_next, type="primary",
              disabled=not bool(st.session_state.types))


# ---- STEP 3: Outcome ----
elif st.session_state.step == 2:
    st.header(STEPS[2])
    df = st.session_state.df
    cols = list(df.columns)

    st.session_state.outcome = st.selectbox(
        "Bağımlı değişken (outcome)", cols,
        index=cols.index(st.session_state.outcome) if st.session_state.outcome in cols else 0,
    )
    st.session_state.study_type = st.radio(
        "Çalışma tipi", ["kesitsel/vaka-kontrol", "sağkalım/kohort", "RCT", "belirsiz"],
        horizontal=True,
    )
    if st.session_state.study_type == "sağkalım/kohort":
        c1, c2 = st.columns(2)
        st.session_state.time_col = c1.selectbox(
            "Zaman sütunu (süre)", cols,
            index=cols.index(st.session_state.time_col) if st.session_state.time_col in cols else 0,
        )
        st.session_state.event_col = c2.selectbox(
            "Olay sütunu (0/1)", cols,
            index=cols.index(st.session_state.event_col) if st.session_state.event_col in cols else 0,
        )

    c1, c2 = st.columns(2)
    c1.button("← Geri", on_click=_back)
    c2.button("Bivariate analizini çalıştır →", on_click=_next, type="primary")


# ---- STEP 4: Bivariate ----
elif st.session_state.step == 3:
    st.header(STEPS[3])
    df = st.session_state.df
    outcome = st.session_state.outcome
    types = st.session_state.types

    skip = set()
    if st.session_state.study_type == "sağkalım/kohort":
        skip.update({st.session_state.time_col, st.session_state.event_col})

    with st.spinner("Tüm değişkenler outcome ile karşılaştırılıyor..."):
        biv = run_bivariate(df, outcome, types, skip=skip)
    st.session_state.bivariate = biv

    st.subheader(f"Sonuçlar (n={len(biv)} test)")
    sig = biv[biv["significant"]]
    st.metric("FDR<0.05 anlamlı", f"{len(sig)} / {len(biv)}")

    st.dataframe(biv, use_container_width=True)
    csv = biv.to_csv(index=False).encode()
    st.download_button("📥 Bivariate sonuçlarını CSV indir", csv, "bivariate.csv", "text/csv")

    c1, c2 = st.columns(2)
    c1.button("← Geri", on_click=_back)
    c2.button("Multivariate adımına →", on_click=_next, type="primary")


# ---- STEP 5: Multivariate ----
elif st.session_state.step == 4:
    st.header(STEPS[4])
    biv = st.session_state.bivariate
    df = st.session_state.df
    types = st.session_state.types
    outcome = st.session_state.outcome

    p_threshold = st.slider("Multivariate için p_FDR eşiği (girecek değişkenler için)",
                            0.05, 0.20, 0.10, 0.01)
    candidates = biv.loc[(biv["p_fdr"].fillna(1) < p_threshold) & (biv["p"].notna()), "feature"].tolist()
    chosen = st.multiselect("Modele alınacak değişkenler", biv["feature"].tolist(), default=candidates)

    if st.session_state.study_type == "sağkalım/kohort":
        if st.button("Cox regresyon + KM eğrileri çalıştır", type="primary"):
            with st.spinner("Cox regresyon..."):
                cox = run_cox(df, st.session_state.time_col, st.session_state.event_col,
                              chosen, types)
                st.session_state.survival_cox = cox
            with st.spinner("Kaplan-Meier..."):
                group = chosen[0] if chosen else None
                km = run_kaplan_meier(df, st.session_state.time_col, st.session_state.event_col,
                                      group_col=group)
                st.session_state.survival_km = km

        if st.session_state.survival_cox:
            cox = st.session_state.survival_cox
            if "error" in cox:
                st.error(cox["error"])
            else:
                st.subheader(f"Cox Regresyon (n={cox['n']}, olay={cox['events']})")
                st.metric("C-index", f"{cox['concordance']:.3f}")
                st.dataframe(cox["coefficients"], use_container_width=True)

        if st.session_state.survival_km:
            km = st.session_state.survival_km
            st.subheader("Kaplan-Meier")
            if km.get("logrank_p") is not None:
                st.metric("Log-rank p", f"{km['logrank_p']:.4f}")
            for label, c in km["curves"].items():
                st.write(f"**{label}** — medyan: {c.get('median')}")
                st.line_chart(pd.DataFrame({label: c["survival"]}, index=c["timeline"]))
    else:
        if st.button("Multivariate regresyon çalıştır", type="primary"):
            with st.spinner("Lineer/lojistik regresyon..."):
                mv = auto_multivariate(df, outcome, chosen, types)
                st.session_state.multivariate = mv

        if st.session_state.multivariate:
            mv = st.session_state.multivariate
            if "error" in mv:
                st.error(mv["error"])
            else:
                st.subheader(f"{mv['type'].title()} regresyon (n={mv['n']})")
                st.dataframe(mv["coefficients"], use_container_width=True)
                if "vif" in mv:
                    with st.expander("VIF (multikolineerlik)"):
                        st.dataframe(mv["vif"])
                with st.expander("Tam istatistik özeti"):
                    st.code(mv["summary"])

    c1, c2 = st.columns(2)
    c1.button("← Geri", on_click=_back)
    c2.button("Literatüre →", on_click=_next, type="primary")


# ---- STEP 6: Literatür ----
elif st.session_state.step == 5:
    st.header(STEPS[5])
    biv = st.session_state.bivariate
    sig = biv[biv["significant"]]
    if sig.empty:
        st.warning("FDR-anlamlı bulgu yok. p<0.05 olanlarla devam edebilirsiniz.")
        sig = biv[biv["p"].fillna(1) < 0.05]

    st.write(f"Bulgu sayısı: **{len(sig)}**")
    st.dataframe(sig[["feature", "test", "p_fdr", "effect"]], use_container_width=True)

    extra = st.text_input("Ek anahtar kelimeler (boşlukla ayır, opsiyonel)",
                          placeholder="örn: cardiovascular mortality")
    max_per = st.slider("Bulgu başına makale sayısı", 3, 10, 5)

    if st.button("PubMed'de ara", type="primary"):
        findings = [{"feature": r["feature"], "outcome": st.session_state.outcome}
                    for _, r in sig.iterrows()]
        extra_terms = extra.split() if extra else None
        with st.spinner("PubMed E-utilities..."):
            lit = search_for_findings(findings, extra_terms=extra_terms,
                                      max_per_finding=max_per,
                                      api_key=st.session_state.pubmed_key or None)
        st.session_state.literature = lit

    if st.session_state.literature:
        for feat, papers in st.session_state.literature.items():
            if feat == "_errors":
                continue
            with st.expander(f"🔬 {feat} ({len(papers)} makale)"):
                for p in papers:
                    st.markdown(f"**[{p.title}]({p.url})**  \n"
                                f"{', '.join(p.authors[:3])} · *{p.journal}* ({p.year}) · "
                                f"PMID: {p.pmid}")
                    if p.abstract:
                        st.caption(p.abstract[:500] + ("..." if len(p.abstract) > 500 else ""))

    c1, c2 = st.columns(2)
    c1.button("← Geri", on_click=_back)
    c2.button("Raporu oluştur →", on_click=_next, type="primary")


# ---- STEP 7: Rapor ----
elif st.session_state.step == 6:
    st.header(STEPS[6])
    df = st.session_state.df
    biv = st.session_state.bivariate
    mv = st.session_state.multivariate or st.session_state.survival_cox
    types = st.session_state.types
    outcome = st.session_state.outcome

    meta = {
        "outcome": outcome,
        "outcome_type": types.get(outcome),
        "study_type": st.session_state.study_type,
        "n_rows": len(df) if df is not None else 0,
        "n_cols": df.shape[1] if df is not None else 0,
        "missing_strategy": st.session_state.missing_strategy,
    }

    use_llm = st.checkbox("Anthropic API ile makale fikri üret (anahtar gerekli)",
                          value=bool(st.session_state.anthropic_key))
    article_ideas = None
    if use_llm and st.session_state.anthropic_key:
        with st.spinner("Claude yazıyor..."):
            article_ideas = llm_article_ideas(
                meta, biv, mv, st.session_state.literature,
                api_key=st.session_state.anthropic_key,
            )

    md = build_markdown(meta, biv, mv, st.session_state.literature, article_ideas)
    st.session_state.report_md = md

    st.markdown(md)
    st.download_button("📥 Raporu indir (Markdown)",
                       md.encode("utf-8"), "rapor.md", "text/markdown")

    c1, _ = st.columns(2)
    c1.button("← Geri", on_click=_back)
