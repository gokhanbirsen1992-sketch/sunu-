"""Aşama 4: Makale yazımı — Yöntem/Bulgular deterministik, Giriş/Tartışma ajan ordusuyla."""
from __future__ import annotations

import asyncio

from app.agents import prompts, validators
from app.llm import template_provider as tpl
from app.llm.provider import LLMUnavailable
from app.models import ValidationIssue
from app.pipeline.stage import PipelineContext, Stage

P_ADJUST_NAMES = {"holm": "Holm", "fdr_bh": "Benjamini-Hochberg (FDR)", "none": None}


def build_methods(ctx: PipelineContext) -> str:
    lang = ctx.job.config.language
    r = ctx.cleaning_report
    n = r.rows_after if r else (len(ctx.df) if ctx.df is not None else 0)
    adj = P_ADJUST_NAMES[ctx.job.config.p_adjust]
    rationales = []
    for p in ctx.plans:
        rat = p.rationale_tr if lang == "tr" else p.rationale_en
        if rat and rat not in rationales:
            rationales.append(rat)
    if lang == "tr":
        paras = [
            f"Araştırmanın veri seti {r.rows_before if r else n} gözlemden oluşmaktadır. "
            "Veri temizleme sürecinde " + " ".join(r.actions[:-1] if r and len(r.actions) > 1 else (r.actions if r else []))
            + f" Nihai analizler {n} gözlem üzerinden yürütülmüştür.",
            "Analizlerden önce her sürekli değişken için normallik (Shapiro-Wilk testi ve çarpıklık-basıklık "
            "katsayıları) ve gerektiğinde varyans homojenliği (Levene testi) incelenmiş; test seçimi bu varsayım "
            "kontrollerine dayandırılmıştır. " + " ".join(rationales[:12]),
            f"Anlamlılık düzeyi α = {ctx.job.config.alpha} olarak belirlenmiştir."
            + (f" Çoklu karşılaştırmalar için p-değerleri {adj} yöntemiyle düzeltilmiştir." if adj else "")
            + " Etki büyüklükleri (Cohen d, η², Cramér V vb.) tüm testler için raporlanmıştır. "
            "Tüm analizler Python (SciPy, statsmodels) ile gerçekleştirilmiştir.",
        ]
    else:
        paras = [
            f"The dataset comprised {r.rows_before if r else n} observations. "
            f"After data screening, the final analyses were conducted on {n} observations.",
            "Prior to the analyses, normality (Shapiro-Wilk test and skewness-kurtosis coefficients) and, "
            "where appropriate, homogeneity of variance (Levene's test) were examined for each continuous "
            "variable; test selection was based on these assumption checks. " + " ".join(rationales[:12]),
            f"The significance level was set at α = {ctx.job.config.alpha}."
            + (f" P-values were corrected for multiple comparisons using the {adj} method." if adj else "")
            + " Effect sizes (Cohen's d, η², Cramér's V, etc.) are reported for all tests. "
            "All analyses were performed in Python (SciPy, statsmodels).",
        ]
    return "\n\n".join(paras)


def build_results(ctx: PipelineContext) -> str:
    lang = ctx.job.config.language
    valid = [f for f in ctx.findings if f.error is None]
    sig = [f for f in valid if f.significant]
    nonsig = [f for f in valid if not f.significant]
    lines = []
    if lang == "tr":
        lines.append(
            f"Yürütülen {len(valid)} analizden {len(sig)} tanesi istatistiksel olarak anlamlı sonuç vermiştir. "
            "Tüm test sonuçları Tablo 1'de özetlenmiştir."
        )
        for f in sig:
            sentence = f.apa_tr
            if f.posthoc:
                sig_pairs = [f"{p['a']} – {p['b']}" for p in f.posthoc if p.get("significant")]
                if sig_pairs:
                    sentence += f" Post-hoc karşılaştırmalarda anlamlı fark gösteren çiftler: {'; '.join(sig_pairs)}."
            lines.append(sentence)
        if nonsig:
            lines.append("Diğer analizlerde istatistiksel olarak anlamlı sonuç elde edilmemiştir: "
                         + " ".join(f.apa_tr for f in nonsig[:8]))
    else:
        lines.append(
            f"Of the {len(valid)} analyses conducted, {len(sig)} yielded statistically significant results. "
            "All test results are summarized in Table 1."
        )
        for f in sig:
            sentence = f.apa_en
            if f.posthoc:
                sig_pairs = [f"{p['a']} – {p['b']}" for p in f.posthoc if p.get("significant")]
                if sig_pairs:
                    sentence += f" Post-hoc comparisons showed significant differences between: {'; '.join(sig_pairs)}."
            lines.append(sentence)
        if nonsig:
            lines.append("The remaining analyses were not statistically significant: "
                         + " ".join(f.apa_en for f in nonsig[:8]))
    return "\n\n".join(lines)


def build_exploratory(ctx: PipelineContext) -> str:
    """Kümeleme/anomali/bilgi-teorisi/risk skoru bulgularını keşifsel bir bölüm olarak yazar.

    Bu bölüm bilinçli olarak Bulgular'dan ayrı tutulur: p-değeri taşıyan doğrulayıcı hipotez
    testlerinin aksine, kümeleme/ML sonuçları klasik anlamda "anlamlı" değildir — hipotez
    üreticidir, doğrulayıcı değil.
    """
    d = ctx.discovery
    if d is None:
        return ""
    lang = ctx.job.config.language
    paras: list[str] = []

    if lang == "tr":
        intro = (
            "Doğrulayıcı hipotez testlerine ek olarak, klasik yöntemlerin gözden kaçırabileceği "
            "örüntüleri ortaya çıkarmak amacıyla kümeleme, anomali tespiti, bilgi teorisi ve "
            "(uygunsa) makine öğrenmesi tabanlı risk modellemesi içeren keşifsel bir analiz "
            "yürütülmüştür. Aşağıdaki bulgular hipotez üreticidir; p-değerine dayalı anlamlılık "
            "testi içermez ve doğrulayıcı sonuçlarla karıştırılmamalıdır."
        )
    else:
        intro = (
            "In addition to the confirmatory hypothesis tests, an exploratory analysis — "
            "clustering, anomaly detection, information theory, and, where applicable, "
            "machine-learning-based risk modeling — was conducted to surface patterns that "
            "classical methods may overlook. The findings below are hypothesis-generating; "
            "they carry no p-value-based significance and should not be conflated with the "
            "confirmatory results."
        )
    paras.append(intro)

    if d.clustering:
        c = d.clustering
        if lang == "tr":
            paras.append(
                f"K-Means kümeleme ve temel bileşenler analizi (PCA) ile veride {c.k} gizli alt-grup "
                f"tespit edilmiştir (silhouette skoru = {c.silhouette:.2f}). "
                + " ".join(
                    f"Grup {cl.cluster_id} (n={cl.size}, %{cl.share*100:.0f}) en çok "
                    + ", ".join(v["name"] for v in cl.top_variables[:3])
                    + " değişkenleriyle ayrışmaktadır."
                    for cl in c.clusters
                )
            )
        else:
            paras.append(
                f"K-Means clustering combined with principal component analysis (PCA) identified "
                f"{c.k} hidden subgroups in the data (silhouette score = {c.silhouette:.2f}). "
                + " ".join(
                    f"Group {cl.cluster_id} (n={cl.size}, {cl.share*100:.0f}%) is most distinguished by "
                    + ", ".join(v["name"] for v in cl.top_variables[:3]) + "."
                    for cl in c.clusters
                )
            )

    if d.anomalies and d.anomalies.n_flagged:
        if lang == "tr":
            paras.append(
                f"Isolation Forest algoritmasıyla yapılan çok-değişkenli aykırı değer taramasında "
                f"{d.anomalies.n_flagged} sıra dışı vaka işaretlenmiştir (kirlilik oranı "
                f"%{d.anomalies.contamination*100:.0f}); bu vakalar tek-değişkenli aykırı değer "
                "kontrolünde fark edilmemiş olabilir."
            )
        else:
            paras.append(
                f"A multivariate outlier scan using Isolation Forest flagged {d.anomalies.n_flagged} "
                f"atypical cases (contamination = {d.anomalies.contamination*100:.0f}%) that univariate "
                "outlier checks may have missed."
            )

    hidden_pairs = [p for p in d.mutual_info if p.hidden]
    if hidden_pairs:
        top = hidden_pairs[:5]
        if lang == "tr":
            listed = "; ".join(f"{p.var_a}–{p.var_b} (MI={p.mi:.3f})" for p in top)
            paras.append(
                "Karşılıklı bilgi (mutual information) analizi, klasik Pearson/Spearman "
                "korelasyonunun zayıf gösterdiği ancak doğrusal olmayan bir bilgi akışı taşıyan "
                f"{len(hidden_pairs)} değişken çifti ortaya çıkarmıştır: {listed}."
            )
        else:
            listed = "; ".join(f"{p.var_a}–{p.var_b} (MI={p.mi:.3f})" for p in top)
            paras.append(
                "Mutual information analysis revealed "
                f"{len(hidden_pairs)} variable pairs carrying a non-linear informational relationship "
                f"that classical Pearson/Spearman correlation rated as weak: {listed}."
            )

    if d.risk_score:
        r = d.risk_score
        auc = r.auc_logreg if r.auc_logreg is not None else r.auc_rf
        top_pred = ", ".join(p["name"] for p in r.predictors[:5])
        if lang == "tr":
            auc_txt = f"AUC = {auc:.2f}" if auc is not None else "AUC hesaplanamadı"
            paras.append(
                f"'{r.dv}' değişkeni için lojistik regresyon ve Random Forest ile çapraz doğrulamalı "
                f"bir risk skoru modeli kurulmuştur (n={r.n}, {auc_txt}). En güçlü yordayıcılar: "
                f"{top_pred}. Bu skor, klinik/karar amaçlı kullanılmadan önce bağımsız bir örneklemde "
                "doğrulanmalıdır."
            )
        else:
            auc_txt = f"AUC = {auc:.2f}" if auc is not None else "AUC could not be computed"
            paras.append(
                f"A cross-validated risk-score model (logistic regression and Random Forest) was "
                f"built for '{r.dv}' (n={r.n}, {auc_txt}). Strongest predictors: {top_pred}. This "
                "score should be validated on an independent sample before any clinical or "
                "decision-making use."
            )

    if d.skipped_reasons:
        if lang == "tr":
            paras.append("Atlanan keşifsel analizler: " + " ".join(d.skipped_reasons))
        else:
            paras.append("Skipped exploratory analyses: " + " ".join(d.skipped_reasons))

    return "\n\n".join(paras)


class WritingStage(Stage):
    stage_id = "writing"
    name = "Makale Yazımı"
    max_attempts = 2

    async def _army_write(self, ctx: PipelineContext, attempt: int, section_label: str,
                          system: str, user: str, template_fn) -> str:
        """N paralel işçi ajan taslak yazar, seçici ajan en iyisini seçer; LLM yoksa şablon."""
        n = max(1, ctx.job.config.n_workers)
        if ctx.router.mode != "llm":
            async with self.agent(ctx, f"Şablon Yazarı ({section_label})", "worker", attempt) as h:
                text = template_fn()
                await h.passed(f"{len(text.split())} kelime")
                return text

        async def worker(i: int) -> str | None:
            async with self.agent(ctx, f"{section_label} Yazarı #{i + 1}", "worker", attempt) as h:
                try:
                    resp = await ctx.router.complete(system, user, temperature=0.6 + 0.15 * i)
                    text = resp.text.strip()
                    await h.passed(f"{len(text.split())} kelime ({resp.provider})")
                    return text
                except LLMUnavailable as exc:
                    await h.failed(str(exc))
                    return None

        drafts = [d for d in await asyncio.gather(*(worker(i) for i in range(n))) if d]
        if not drafts:
            async with self.agent(ctx, f"Şablon Yazarı ({section_label})", "worker", attempt) as h:
                text = template_fn()
                await h.passed("LLM kullanılamadı; şablona düşüldü")
                return text
        if len(drafts) == 1:
            return drafts[0]

        async with self.agent(ctx, f"Seçici Editör ({section_label})", "selector", attempt) as h:
            try:
                data = await ctx.router.complete_json(prompts.system_selector(), prompts.user_selector(drafts))
                best = int(data.get("best", 1)) - 1
                best = best if 0 <= best < len(drafts) else 0
                await h.passed(f"Taslak {best + 1} seçildi: {str(data.get('reason', ''))[:120]}")
            except (LLMUnavailable, ValueError, AttributeError):
                best = max(range(len(drafts)), key=lambda i: len(drafts[i].split()))
                await h.passed("Seçici LLM yanıt vermedi; en kapsamlı taslak seçildi")
            return drafts[best]

    async def run(self, ctx: PipelineContext, attempt: int):
        lang = ctx.job.config.language
        topic = ctx.job.config.topic_hint
        feedback = ctx.feedback
        n_rows = ctx.cleaning_report.rows_after if ctx.cleaning_report else 0
        sections: dict[str, str] = {}

        async with self.agent(ctx, "Yöntem Derleyici", "worker", attempt) as h:
            sections["methods"] = build_methods(ctx)
            await h.passed("varsayım gerekçeleriyle derlendi")
        async with self.agent(ctx, "Bulgu Derleyici", "worker", attempt) as h:
            sections["results"] = build_results(ctx)
            await h.passed("APA sonuç cümleleri derlendi")
        async with self.agent(ctx, "Keşifsel Bulgu Derleyici", "worker", attempt) as h:
            sections["exploratory"] = build_exploratory(ctx)
            await h.passed("keşifsel bulgular derlendi" if sections["exploratory"] else "keşifsel bulgu yok, atlandı")

        # Başlık
        title = tpl.draft_title(ctx.findings, topic, lang)
        if ctx.router.mode == "llm":
            async with self.agent(ctx, "Başlık Yazarı", "worker", attempt) as h:
                try:
                    resp = await ctx.router.complete(prompts.system_writer(lang), prompts.user_title(ctx.findings, topic, lang), max_tokens=256)
                    candidate = resp.text.strip().strip('"').splitlines()[0].strip()[:150]
                    if len(candidate.split()) >= 3:
                        title = candidate
                        await h.passed(title)
                    else:
                        await h.failed(f"başlık çok kısa ({candidate!r}); şablon başlık korundu")
                except LLMUnavailable as exc:
                    await h.failed(str(exc))

        intro_refs = ctx.intro_refs()
        refs_by_finding = {f.id: ctx.refs_for(f.id) for f in ctx.findings}
        all_cited_refs = ctx.references

        sections["intro"] = await self._army_write(
            ctx, attempt, "Giriş",
            prompts.system_writer(lang),
            prompts.user_intro(ctx.findings, intro_refs, topic, lang, feedback),
            lambda: tpl.draft_intro(ctx.findings, intro_refs, topic, lang),
        )
        sections["discussion"] = await self._army_write(
            ctx, attempt, "Tartışma",
            prompts.system_writer(lang),
            prompts.user_discussion(ctx.findings, all_cited_refs, lang, feedback),
            lambda: tpl.draft_discussion(ctx.findings, refs_by_finding, lang),
        )
        sections["limitations"] = await self._army_write(
            ctx, attempt, "Sınırlılıklar",
            prompts.system_writer(lang),
            prompts.user_limitations(n_rows, lang),
            lambda: tpl.draft_limitations(n_rows, lang),
        )
        return title, sections

    async def validate(self, ctx: PipelineContext, output, attempt: int):
        title, sections = output
        valid_ids = {r.id for r in ctx.references}
        issues: list[ValidationIssue] = []

        async with self.agent(ctx, "Atıf Denetçisi", "validator", attempt) as h:
            for key in ("intro", "discussion"):
                issues.extend(validators.check_citations(sections.get(key, ""), valid_ids, key))
            n_block = sum(1 for i in issues if i.severity == "block")
            if n_block:
                await h.failed(f"{n_block} atıf ihlali")
            else:
                await h.passed("tüm atıf işaretleri geçerli")

        async with self.agent(ctx, "Yapı Denetçisi", "validator", attempt) as h:
            before = len(issues)
            issues.extend(validators.check_min_length(sections.get("intro", ""), 60, "intro"))
            issues.extend(validators.check_min_length(sections.get("discussion", ""), 60, "discussion"))
            issues.extend(validators.check_min_length(sections.get("limitations", ""), 30, "limitations"))
            issues.extend(validators.check_pvalues_match(sections.get("discussion", ""), ctx.findings, "discussion"))
            if not title.strip():
                issues.append(ValidationIssue(severity="block", message="Başlık üretilemedi.", target="title"))
            if len(issues) > before:
                await h.failed(f"{len(issues) - before} yapı sorunu")
            else:
                await h.passed("bölüm uzunlukları ve sayılar tutarlı")

        if ctx.router.mode == "llm":
            lang = ctx.job.config.language
            for key in ("intro", "discussion"):
                async with self.agent(ctx, f"Tutarlılık Denetçisi ({key})", "validator", attempt) as h:
                    try:
                        data = await ctx.router.complete_json(
                            prompts.system_coherence_validator(),
                            prompts.user_coherence(key, sections.get(key, ""), ctx.findings, lang),
                        )
                        if isinstance(data, dict) and data.get("pass") is False:
                            problems = [str(p) for p in (data.get("problems") or [])][:3]
                            for p in problems:
                                issues.append(ValidationIssue(severity="block", message=f"Tutarlılık ({key}): {p}", target=key))
                            await h.failed("; ".join(problems) or "tutarsızlık bildirildi")
                        else:
                            await h.passed("bulgularla tutarlı")
                    except LLMUnavailable:
                        await h.passed("LLM denetçi atlandı (sağlayıcı yok)")
        return issues

    def accept(self, ctx: PipelineContext, output) -> None:
        title, sections = output
        m = ctx.manuscript
        m.title = title
        m.language = ctx.job.config.language
        m.sections.update(sections)
        m.references = ctx.references
        sr = ctx.job.stages[self.stage_id]
        total_words = sum(len(t.split()) for t in sections.values())
        sr.summary = f"Beş bölüm yazıldı (~{total_words} kelime); başlık: “{title[:80]}”"
