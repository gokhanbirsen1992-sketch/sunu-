"""Otomatik analiz planı üretici — generality'nin kalbi.

Herhangi bir `.sav`'ın profili (+ opsiyonel brief) verildiğinde, hangi
değişkene hangi testin uygulanacağını içeren `analysis_plan.json`'u KENDİ kurar.
Böylece plan veri setine elle yazılmaz.

İki mod:
  * brief VARSA: araştırma soruları + bildirilen roller (outcome/group/predictors,
    correlation, regression, confirmatory) plana çevrilir.
  * brief YOKSA (heuristik): kimlik/PII değişkenleri dışlanır; gruplama değişkeni
    otomatik bulunur; her sürekli değişken için grup karşılaştırması + Tablo 1
    önerilir. Bu taslak İNSAN KAPISI 1'de onaylanır/düzeltilir.

Plan otomatik üretilse bile NİHAİ DEĞİLDİR: methodologist + kullanıcı onayı şarttır.
"""

from __future__ import annotations

import re

# Doğrudan kimlik/PII göstergesi olan ad parçaları (analiz dışı bırakılır).
_PII_NAME = re.compile(
    r"(ad.?soyad|hastaad|isim|soyad|\bname\b|do[gğ]umtar|birth.?date|"
    r"ar[sş]iv|dosyano|protokol|tckn|kimlik|barkod|numuneno|\btarih\b|filter)",
    re.IGNORECASE,
)
_GROUP_NAME = re.compile(r"(grup|grub|group|tan[iı]|diagnos|kohort|cohort|\barm\b|\bcase\b)", re.IGNORECASE)
_SEX_NAME = re.compile(r"(cinsiyet|\bsex\b|gender|cins)", re.IGNORECASE)


def detect_id_vars(profile: dict) -> list[str]:
    out = []
    for v in profile["variables"]:
        if v["role"] in ("id", "constant"):
            out.append(v["name"])
        elif _PII_NAME.search(v["name"]):
            out.append(v["name"])
    return out


def _is_categorical(v: dict) -> bool:
    return v["role"] in ("binary", "nominal", "ordinal")


def detect_group_vars(profile: dict, id_vars: set[str]) -> list[str]:
    """2–8 düzeyli kategorik değişkenleri (gruplama adayı) bulur, ad eşleşmesini öne alır."""
    cands = [v for v in profile["variables"]
             if v["name"] not in id_vars and _is_categorical(v) and 2 <= v["n_unique"] <= 8]
    named = [v for v in cands if _GROUP_NAME.search(v["name"])]
    rest = [v for v in cands if not _GROUP_NAME.search(v["name"])]
    return [v["name"] for v in named + rest]


def detect_sex_var(profile: dict, id_vars: set[str]) -> str | None:
    for v in profile["variables"]:
        if v["name"] not in id_vars and _SEX_NAME.search(v["name"]):
            return v["name"]
    return None


def continuous_vars(profile: dict, id_vars: set[str]) -> list[str]:
    return [v["name"] for v in profile["variables"]
            if v["name"] not in id_vars and v["role"] == "continuous"]


def _group_levels(profile: dict, name: str) -> int:
    for v in profile["variables"]:
        if v["name"] == name:
            return v["n_unique"]
    return 0


def build_plan(profile: dict, brief: dict | None = None, run_id: str = "auto") -> dict:
    brief = brief or {}
    id_vars = sorted(set(detect_id_vars(profile)) | set(brief.get("id_vars", [])))
    id_set = set(id_vars)

    confirmatory = set(brief.get("confirmatory_outcomes", []))
    # doğrulayıcı hipotezlerden ana belirteçleri çıkar (research_questions.outcome)
    for rq in brief.get("research_questions", []):
        if rq.get("primary"):
            if rq.get("outcome"):
                confirmatory.add(rq["outcome"])

    # Gruplama değişkeni: brief'te bildirilmişse onu, yoksa otomatik ilk adayı kullan
    group_var = brief.get("group")
    if not group_var:
        for rq in brief.get("research_questions", []):
            if rq.get("group"):
                group_var = rq["group"]; break
    if not group_var:
        gvs = detect_group_vars(profile, id_set)
        group_var = gvs[0] if gvs else None

    cont = continuous_vars(profile, id_set)
    steps: list[dict] = []

    include = [v["name"] for v in profile["variables"]
               if v["name"] not in id_set and v["role"] not in ("id", "constant", "unknown")]
    steps.append({"type": "descriptives", "include": include})

    if group_var:
        k = _group_levels(profile, group_var)
        cmp_type = "multi_group_compare" if k >= 3 else "group_compare"
        i = 0
        for cv in cont:
            if cv == group_var:
                continue
            i += 1
            steps.append({"type": cmp_type, "id": f"M{i}", "outcome": cv, "group": group_var,
                          "confirmatory": cv in confirmatory, "question_ref": "RQ1"})
        sex = detect_sex_var(profile, id_set)
        if sex and sex != group_var:
            steps.append({"type": "categorical", "id": "CAT1", "row": sex, "col": group_var,
                          "question_ref": "RQ1"})

    # Korelasyon matrisi / regresyon yalnız brief bildirmişse (tahmin riski yüksek)
    cm = brief.get("correlation_matrix")
    if cm:
        steps.append({"type": "correlation_matrix", "id": "KMAT",
                      "x_vars": cm["x_vars"], "y_vars": cm["y_vars"], "question_ref": "RQ2"})
    reg = brief.get("regression")
    if reg:
        steps.append({"type": "regression_linear", "id": "REG1",
                      "outcome": reg["outcome"], "predictors": reg["predictors"], "question_ref": "RQ3"})

    plan = {
        "run_id": brief.get("run_id", run_id),
        "design": {"kind": brief.get("study_design", "cross_sectional"),
                   "checklist": brief.get("reporting_checklist") or "STROBE"},
        "id_vars": id_vars,
        "multiplicity_policy": brief.get("multiplicity_policy", "bh"),
        "missing_data_policy": brief.get("missing_data_policy", "pairwise"),
        "group_var": group_var,
        "steps": steps,
        "table1": {"title": brief.get("table1_title", "Tablo 1. Gruplara göre özellikler")},
    }
    if brief.get("figures"):
        plan["figures"] = brief["figures"]
    return plan
