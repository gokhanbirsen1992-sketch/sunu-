"""Şablon modu: LLM anahtarı yokken kural-tabanlı, kusursuz atıflı taslak üretimi.

Metin kuru olabilir ama sayılar gerçek, atıflar gerçek ve yapı tamdır.
"""
from __future__ import annotations

from app.models import Finding, Reference


def _refs_markers(refs: list[Reference], limit: int = 3) -> str:
    ids = [str(r.id) for r in refs[:limit]]
    return f" [{', '.join(ids)}]" if ids else ""


def _topic_sentence(topic: str | None, lang: str) -> str:
    if topic:
        return topic.strip().rstrip(".") + "."
    return (
        "Bu çalışma, incelenen değişkenler arasındaki ilişkileri ve grup farklılıklarını nicel olarak ele almaktadır."
        if lang == "tr"
        else "This study quantitatively examines the relationships and group differences among the variables under investigation."
    )


def draft_title(findings: list[Finding], topic: str | None, lang: str) -> str:
    sig = [f for f in findings if f.significant]
    if topic:
        base = topic.strip().rstrip(".")
        return base[:120]
    if sig:
        kw = sig[0].keywords[:2]
        if lang == "tr":
            return f"{' ve '.join(kw)} Arasındaki İlişkilerin İncelenmesi: Nicel Bir Araştırma"
        return f"An Examination of the Relationships Between {' and '.join(kw)}: A Quantitative Study"
    return "Nicel Bir Araştırma" if lang == "tr" else "A Quantitative Study"


def draft_intro(findings: list[Finding], intro_refs: list[Reference], topic: str | None, lang: str) -> str:
    sig = [f for f in findings if f.significant]
    kws: list[str] = []
    for f in sig[:4]:
        for k in f.keywords:
            if k not in kws:
                kws.append(k)
    kw_text = ", ".join(kws[:6]) if kws else ("araştırma değişkenleri" if lang == "tr" else "the study variables")
    m1 = _refs_markers(intro_refs[:3])
    m2 = _refs_markers(intro_refs[3:6])
    if lang == "tr":
        paras = [
            _topic_sentence(topic, lang)
            + f" Alanyazında {kw_text} kavramları farklı örneklemlerde ele alınmış ve bu değişkenlerin "
            f"birbirleriyle ilişkili olabileceği öne sürülmüştür{m1}.",
            "Önceki çalışmalar, bu değişkenler arasındaki ilişkilerin bağlama ve örneklem özelliklerine göre "
            f"değişebildiğini göstermektedir{m2}. Ancak mevcut bulgular her zaman tutarlı değildir ve bu ilişkilerin "
            "hangi koşullarda ortaya çıktığı henüz tam olarak netleşmemiştir.",
            "Bu çalışmanın amacı, söz konusu değişkenler arasındaki ilişkileri ve grup farklılıklarını uygun "
            "istatistiksel yöntemlerle incelemek ve elde edilen bulguları alanyazın ışığında tartışmaktır. "
            "Bu doğrultuda veriler sistematik olarak temizlenmiş, her araştırma sorusu için varsayım kontrollerine "
            "dayalı olarak uygun testler seçilmiş ve sonuçlar raporlanmıştır.",
        ]
    else:
        paras = [
            _topic_sentence(topic, lang)
            + f" Prior literature has examined {kw_text} across diverse samples and suggested that these "
            f"constructs may be interrelated{m1}.",
            f"Previous studies indicate that the relationships among these variables can vary by context and "
            f"sample characteristics{m2}. However, existing findings are not always consistent, and the conditions "
            "under which these relationships emerge remain unclear.",
            "The aim of the present study is to examine the relationships and group differences among these "
            "variables using appropriate statistical methods and to discuss the findings in light of the "
            "literature. Data were systematically screened, assumption checks guided the selection of each "
            "statistical test, and results are reported accordingly.",
        ]
    return "\n\n".join(paras)


def draft_discussion(findings: list[Finding], refs_by_finding: dict[str, list[Reference]], lang: str) -> str:
    sig = [f for f in findings if f.significant]
    nonsig = [f for f in findings if not f.significant and f.error is None]
    paras: list[str] = []
    if lang == "tr":
        paras.append(
            "Bu çalışmada elde edilen bulgular, araştırma değişkenleri arasındaki ilişkiler açısından "
            "değerlendirilmiş ve alanyazın ile karşılaştırılmıştır."
        )
        for f in sig:
            markers = _refs_markers(refs_by_finding.get(f.id, []))
            paras.append(
                f"{f.apa_tr} Bu bulgu, alanyazındaki benzer çalışmalarla birlikte "
                f"değerlendirildiğinde anlamlıdır{markers}. Sonuç, ilgili değişkenler arasındaki ilişkinin "
                "kuramsal beklentilerle uyumlu olduğuna işaret etmektedir."
            )
        if nonsig:
            paras.append(
                f"Öte yandan {len(nonsig)} analizde istatistiksel olarak anlamlı sonuç elde edilmemiştir. "
                "Bu durum örneklem büyüklüğü, ölçüm özellikleri veya gerçek bir etkinin bulunmamasıyla açıklanabilir."
            )
        paras.append(
            "Genel olarak bulgular, incelenen değişkenler arasındaki ilişkilerin daha büyük ve çeşitli "
            "örneklemlerde yeniden sınanmasının alanyazına katkı sağlayacağını göstermektedir."
        )
    else:
        paras.append(
            "The findings of this study were evaluated with respect to the relationships among the study "
            "variables and compared with the existing literature."
        )
        for f in sig:
            markers = _refs_markers(refs_by_finding.get(f.id, []))
            paras.append(
                f"{f.apa_en} This finding is meaningful when considered alongside similar studies in the "
                f"literature{markers}. The result suggests that the relationship between these variables is "
                "consistent with theoretical expectations."
            )
        if nonsig:
            paras.append(
                f"On the other hand, {len(nonsig)} analyses did not yield statistically significant results. "
                "This may be explained by sample size, measurement characteristics, or the absence of a true effect."
            )
        paras.append(
            "Overall, the findings suggest that re-examining these relationships in larger and more diverse "
            "samples would contribute to the literature."
        )
    return "\n\n".join(paras)


def draft_limitations(n_rows: int, lang: str) -> str:
    if lang == "tr":
        return (
            f"Bu çalışmanın bazı sınırlılıkları bulunmaktadır. Birincisi, analizler {n_rows} katılımcıdan oluşan "
            "kesitsel bir veri setine dayanmaktadır; bu nedenle neden-sonuç çıkarımı yapılamaz. İkincisi, çoklu "
            "karşılaştırmalar için p-değeri düzeltmesi uygulanmış olsa da, birinci tip hata olasılığı tamamen "
            "dışlanamaz. Son olarak, bulguların genellenebilirliği örneklemin özellikleriyle sınırlıdır."
        )
    return (
        f"This study has several limitations. First, the analyses are based on a cross-sectional dataset of "
        f"{n_rows} participants; therefore, causal inferences cannot be drawn. Second, although p-value "
        "corrections were applied for multiple comparisons, the possibility of Type I error cannot be fully "
        "excluded. Finally, the generalizability of the findings is limited by the characteristics of the sample."
    )


def template_critiques(manuscript_sections: dict[str, str], n_refs: int, lang: str) -> list[dict]:
    """Reviewer 2'nin şablon modu: sabit ama yerinde kontrol listesi eleştirileri."""
    critiques = []
    intro = manuscript_sections.get("intro", "")
    disc = manuscript_sections.get("discussion", "")
    if lang == "tr":
        if len(intro.split()) < 150:
            critiques.append({"section": "intro", "critique": "Giriş bölümü kısa; araştırmanın gerekçesi ve alanyazın bağlamı genişletilmelidir.", "requires_new_literature": False})
        if n_refs < 5:
            critiques.append({"section": "discussion", "critique": "Kaynak sayısı az; tartışma daha fazla güncel çalışmayla desteklenmelidir.", "requires_new_literature": True})
        if "sınırlılık" not in (disc + manuscript_sections.get("limitations", "")).lower():
            critiques.append({"section": "limitations", "critique": "Sınırlılıklar bölümü yetersiz; örneklem ve desen sınırlılıkları açıkça belirtilmelidir.", "requires_new_literature": False})
        critiques.append({"section": "discussion", "critique": "Tartışmada her anlamlı bulgunun pratik anlamı (etki büyüklüğü yorumu) vurgulanmalıdır.", "requires_new_literature": False})
    else:
        if len(intro.split()) < 150:
            critiques.append({"section": "intro", "critique": "The introduction is brief; the rationale and literature context should be expanded.", "requires_new_literature": False})
        if n_refs < 5:
            critiques.append({"section": "discussion", "critique": "The number of references is low; the discussion should be supported by more recent studies.", "requires_new_literature": True})
        if "limitation" not in (disc + manuscript_sections.get("limitations", "")).lower():
            critiques.append({"section": "limitations", "critique": "The limitations section is insufficient; sample and design limitations should be stated explicitly.", "requires_new_literature": False})
        critiques.append({"section": "discussion", "critique": "The practical meaning of each significant finding (effect size interpretation) should be emphasized in the discussion.", "requires_new_literature": False})
    return critiques


def build_queries_template(finding: Finding) -> list[str]:
    """Bulgu anahtar kelimelerinden İngilizce arama sorguları üretir."""
    kws = [k for k in finding.keywords if k][:3]
    if not kws:
        return []
    queries = [" ".join(kws)]
    if len(kws) >= 2:
        queries.append(f"{kws[0]} {kws[1]} relationship")
    return queries
