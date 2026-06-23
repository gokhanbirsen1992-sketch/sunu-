"""Deterministik Türkçe bölüm üretimi (LLM YOK) — ledger'dan Yöntem/Bulgular/Öz.

Her sayı içeren cümle, ilgili sonucun `apa`/`apa_*` string'inden BİREBİR kurulur ve
o sonucun `result_id`'sine bağlanır; örneklem sayıları `global`'dir. Böylece üretilen
bölümler `verify-numeric`'ten İNŞAEN geçer. Bu, anahtarsız/ücretsiz PWA'nın çekirdeğidir.
"""

from __future__ import annotations

import re


def _label_map(ledger: dict) -> dict:
    return {d["var"]: (d.get("label") or d["var"]) for d in ledger.get("descriptives", [])}


def _lab(ledger: dict, var: str) -> str:
    return _label_map(ledger).get(var) or var


def _find_desc(ledger: dict, name_re: str, dtype: str | None = None):
    for d in ledger.get("descriptives", []):
        if re.search(name_re, d["var"], re.I) and (dtype is None or d["type"] == dtype):
            return d
    return None


def _groups(ledger: dict):
    for r in ledger.get("results", []):
        if r.get("family") in ("multi_group_compare", "group_compare") and r.get("groups"):
            return r["groups"]
    return None


def _sig(r: dict) -> bool:
    return float(r.get("p_adjusted", r.get("p_value", 1))) < 0.05


def _sent(text: str, rid: str | None = None) -> dict:
    return {"text": text, "binding": ({"kind": "ledger", "result_id": rid} if rid else {"kind": "narrative"})}


def _tests_used(ledger: dict) -> str:
    names = {
        "mann_whitney_u": "Mann-Whitney U testi", "student_t": "bağımsız örneklem t testi",
        "welch_t": "Welch t testi", "oneway_anova": "tek yönlü ANOVA",
        "welch_anova": "Welch ANOVA", "kruskal_wallis": "Kruskal-Wallis H testi",
        "chi_square": "ki-kare testi", "chi_square_yates": "ki-kare testi",
        "fisher_exact": "Fisher kesin testi", "pearson": "Pearson korelasyonu",
        "spearman": "Spearman korelasyonu",
    }
    used = []
    for r in ledger.get("results", []):
        t = names.get(r.get("test"))
        if t and t not in used:
            used.append(t)
    if any(r.get("family") in ("correlation", "correlation_matrix") for r in ledger.get("results", [])):
        if "Spearman korelasyonu" not in used and "Pearson korelasyonu" not in used:
            used.append("korelasyon analizi")
    if any(r.get("family") == "linear_regression" for r in ledger.get("results", [])):
        used.append("çok değişkenli doğrusal regresyon")
    return ", ".join(used) if used else "tanımlayıcı istatistikler"


def _sample_sentences(ledger: dict) -> list[dict]:
    out = [_sent(f"Bu çalışmaya toplam {ledger['dataset']['n_rows']} katılımcı dahil edildi.")]
    g = _groups(ledger)
    if g:
        parts = ", ".join(f"{x['label']} (n = {x['n']})" for x in g)
        out.append(_sent(f"Katılımcılar şu gruplara ayrıldı: {parts}."))
    age = _find_desc(ledger, r"ya[sş]|age|yaş", "continuous")
    if age:
        out.append(_sent(f"Yaş ortancası {age['apa_median_iqr']} idi." if "apa_median_iqr" in age
                         else f"Yaş ortalaması {age['apa_mean_sd']} idi.", age["id"]))
    sex = _find_desc(ledger, r"cinsiyet|sex|cins", "categorical")
    if sex and sex.get("categories"):
        c = sex["categories"]
        desc = " ve ".join(f"{x['apa']} {x['label'].lower()}" for x in c[:2])
        out.append(_sent(f"Katılımcıların {desc} idi.", sex["id"]))
    return out


def narrate_methods(ledger: dict) -> dict:
    blocks = [{"type": "paragraph", "sentences": _sample_sentences(ledger)}]
    m = [_sent(f"Sürekli değişkenler için grup karşılaştırmalarında {_tests_used(ledger)} kullanıldı; "
               f"varsayım kontrolleri (normallik, varyans homojenliği) sonuçlara göre test seçimi yapıldı.")]
    if any(r.get("family") == "linear_regression" for r in ledger.get("results", [])):
        m.append(_sent("Çok değişkenli ilişkiler doğrusal regresyonla incelenmiş; gerektiğinde ısıya "
                       "dayanıklı (HC3) robust standart hatalar kullanılmıştır."))
    if ledger.get("multiplicity"):
        m.append(_sent("Keşifsel karşılaştırmalara Benjamini-Hochberg yanlış keşif oranı düzeltmesi uygulanmıştır."))
    m.append(_sent("Her çıkarımsal testte etki büyüklüğü ve %95 güven aralığı raporlanmış; istatistiksel "
                   "anlamlılık düzeyi p < 0,05 olarak kabul edilmiştir."))
    blocks.append({"type": "paragraph", "sentences": m})
    return {"section": "methods", "language": "tr", "blocks": blocks,
            "tables_referenced": ["T1"], "figures_referenced": []}


def _result_sentence(ledger: dict, r: dict) -> dict:
    var = r["variables"].get("outcome") or r["variables"].get("row", "")
    lab = _lab(ledger, var)
    sig = "anlamlı" if _sig(r) else "anlamlı olmayan"
    return _sent(f"{lab} için gruplar arasında {sig} bir farklılık saptandı ({r['apa']}).", r["id"])


def narrate_results(ledger: dict) -> dict:
    blocks = [{"type": "paragraph", "sentences": _sample_sentences(ledger) +
               [_sent("Değişkenlerin gruplara göre dağılımı Tablo 1'de sunulmuştur.")]}]

    cmp_results = [r for r in ledger.get("results", []) if r.get("family") in ("multi_group_compare", "group_compare")]
    sig_cmp = [r for r in cmp_results if _sig(r)]
    sents = [_result_sentence(ledger, r) for r in sig_cmp[:15]]
    if len(sig_cmp) > 15:
        sents.append(_sent("Diğer anlamlı farklar Tablo 1'de ayrıntılı olarak verilmiştir."))
    if sents:
        blocks.append({"type": "paragraph", "sentences": sents})

    km = next((r for r in ledger.get("results", []) if r.get("family") == "correlation_matrix"), None)
    if km:
        cs = [c for c in km["cells"] if c["p"] < 0.05][:8]
        csent = [_sent(f"{_lab(ledger, c['x'])} ile {_lab(ledger, c['y'])} arasında anlamlı korelasyon "
                       f"bulundu ({c['apa']}).", km["id"]) for c in cs]
        if csent:
            blocks.append({"type": "paragraph", "sentences": csent})

    reg = next((r for r in ledger.get("results", []) if r.get("family") == "linear_regression"), None)
    if reg:
        rs = [_sent(f"Çok değişkenli doğrusal regresyon modeli anlamlıydı ({reg['apa']}).", reg["id"])]
        for c in reg["coefficients"]:
            if c["p"] < 0.05:
                rs.append(_sent(f"{c.get('label') or c['predictor']}, sonucun bağımsız öngörücüsüydü "
                                f"({c['apa']}).", reg["id"]))
        blocks.append({"type": "paragraph", "sentences": rs})

    return {"section": "results", "language": "tr", "blocks": blocks,
            "tables_referenced": ["T1"], "figures_referenced": [f["id"] for f in ledger.get("figures", [])]}


def narrate_abstract(ledger: dict) -> dict:
    """Yapılandırılmamış section_draft (verify-numeric için) — doğrulanabilir Bulgular cümleleri."""
    sents = [_sent("Bu çalışmada gruplara göre klinik ve laboratuvar değişkenleri karşılaştırıldı.")]
    g = _groups(ledger)
    if g:
        parts = ", ".join(f"{x['label']} (n = {x['n']})" for x in g)
        sents.append(_sent(f"Toplam {ledger['dataset']['n_rows']} katılımcı şu gruplara ayrıldı: {parts}."))
    cmp_results = [r for r in ledger.get("results", []) if r.get("family") in ("multi_group_compare", "group_compare") and _sig(r)]
    cmp_results.sort(key=lambda r: -abs(r.get("effect", {}).get("value", 0) or 0))
    for r in cmp_results[:2]:
        sents.append(_result_sentence(ledger, r))
    sents.append(_sent("Ayrıntılı bulgular ve etki büyüklükleri metinde sunulmuştur."))
    return {"section": "abstract", "language": "tr",
            "blocks": [{"type": "paragraph", "sentences": sents}],
            "tables_referenced": [], "figures_referenced": []}


def _group_var(ledger: dict) -> str | None:
    for r in ledger.get("results", []):
        if r.get("family") in ("multi_group_compare", "group_compare"):
            return r["variables"].get("group")
    return None


def narrate_intro(ledger: dict) -> dict:
    """Deterministik Giriş (amaç/gerekçe) — atıf/sayı içermez."""
    gv = _group_var(ledger)
    glab = _lab(ledger, gv) if gv else "gruplar"
    sents = [
        _sent("Klinik araştırmalarda farklı gruplar arasında değişkenlerin karşılaştırılması, "
              "hastalık ve sağlık süreçlerinin anlaşılmasına katkı sağlar."),
        _sent(f"Bu çalışmada, {glab} temelinde tanımlanan gruplar arasında klinik ve laboratuvar "
              "değişkenleri karşılaştırılmış ve değişkenler arası ilişkiler incelenmiştir."),
        _sent("Çalışmanın amacı, gruplar arasındaki farkları ortaya koymak ve ilgili değişkenler "
              "arasındaki ilişkileri tanımlamaktır."),
    ]
    return {"section": "intro", "language": "tr", "blocks": [{"type": "paragraph", "sentences": sents}],
            "tables_referenced": [], "figures_referenced": []}


def narrate_discussion(ledger: dict) -> dict:
    """Deterministik Tartışma: önemli bulguların özeti (ledger-bağlı) + genel sınırlılıklar."""
    sig = [r for r in ledger.get("results", [])
           if r.get("family") in ("multi_group_compare", "group_compare") and _sig(r)]
    sig.sort(key=lambda r: -abs(r.get("effect", {}).get("value", 0) or 0))
    main = [_sent("Bu çalışmada gruplar arasında çeşitli değişkenlerde anlamlı farklar saptanmıştır.")]
    for r in sig[:3]:
        main.append(_result_sentence(ledger, r))
    main.append(_sent("Bu bulgular, incelenen değişkenlerin gruplar arasında farklılaştığını göstermektedir."))
    lim = [
        _sent("Çalışmanın bazı sınırlılıkları bulunmaktadır."),
        _sent("Tasarımın gözlemsel doğası neden-sonuç çıkarımına izin vermez; bulgular daha büyük ve "
              "prospektif örneklemlerde doğrulanmalıdır."),
        _sent("Sonuç olarak, saptanan farklar ilgili literatür ışığında değerlendirilmelidir."),
    ]
    return {"section": "discussion", "language": "tr",
            "blocks": [{"type": "paragraph", "sentences": main}, {"type": "paragraph", "sentences": lim}],
            "tables_referenced": [], "figures_referenced": []}


def abstract_dict(ledger: dict) -> dict:
    """manuscript.json için yapılandırılmış Öz (assembler bunu render eder)."""
    g = _groups(ledger)
    grp = ("; " + ", ".join(f"{x['label']} (n = {x['n']})" for x in g)) if g else ""
    bul = []
    cmp_results = [r for r in ledger.get("results", []) if r.get("family") in ("multi_group_compare", "group_compare") and _sig(r)]
    cmp_results.sort(key=lambda r: -abs(r.get("effect", {}).get("value", 0) or 0))
    for r in cmp_results[:2]:
        var = r["variables"].get("outcome", "")
        bul.append(f"{_lab(ledger, var)}: {r['apa']}")
    return {
        "Amaç": "Gruplara göre klinik ve laboratuvar değişkenlerini karşılaştırmak.",
        "Yöntem": f"Toplam {ledger['dataset']['n_rows']} katılımcı{grp}; {_tests_used(ledger)} kullanıldı.",
        "Bulgular": (" ".join(bul) if bul else "Bulgular metinde ve Tablo 1'de sunulmuştur."),
        "Sonuç": "Gruplar arasında saptanan farklar metinde tartışılmıştır.",
    }
