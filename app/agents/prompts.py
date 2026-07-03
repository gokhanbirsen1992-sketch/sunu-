"""Tüm LLM ajanlarının prompt şablonları (makale dili TR/EN)."""
from __future__ import annotations

from app.models import Finding, Reference

LANG_NAME = {"tr": "Türkçe", "en": "İngilizce (English)"}

CITE_RULE = (
    "ATIF KURALI (ZORUNLU): Yalnızca sana verilen numaralı kaynak listesinden, köşeli parantezli "
    "numara işaretiyle atıf yap: [1] veya [2, 5] gibi. Listede olmayan bir numara KULLANMA. "
    "Yazar adı-yıl biçiminde atıf (ör. '(Smith, 2020)') KESİNLİKLE YAZMA — dönüşümü sistem yapacak. "
    "Kaynak uydurma. Önceki çalışmalara dair her iddia bir işaret taşımalı."
)

NUMBER_RULE = (
    "SAYI KURALI (ZORUNLU): İstatistiksel değerleri (p, t, F, r, ortalama...) sana verilen bulgulardan "
    "aynen aktar; asla yeni sayı üretme veya yuvarlama dışında değiştirme."
)


def findings_block(findings: list[Finding], lang: str) -> str:
    lines = []
    for f in findings:
        if f.error:
            continue
        apa = f.apa_tr if lang == "tr" else f.apa_en
        sig = "ANLAMLI" if f.significant else "anlamlı değil"
        lines.append(f"- {f.id} ({sig}): {apa}")
    return "\n".join(lines) or "(bulgu yok)"


def refs_block(refs: list[Reference]) -> str:
    lines = []
    for r in refs:
        authors = ", ".join(r.authors[:3]) + (" et al." if len(r.authors) > 3 else "")
        abstract = (r.abstract or "")[:400]
        lines.append(f"[{r.id}] {authors} ({r.year}). {r.title}. {r.journal or ''}\n    Özet: {abstract}")
    return "\n".join(lines) or "(kaynak yok)"


def system_writer(lang: str) -> str:
    return (
        f"Sen deneyimli bir akademik yazarsın. Nicel bir araştırma makalesi için {LANG_NAME[lang]} "
        f"dilinde, akademik üslupla, APA 7 anlayışıyla bölüm metni yazıyorsun. {CITE_RULE} {NUMBER_RULE} "
        "Yanıt olarak YALNIZCA istenen bölüm metnini yaz; başlık, açıklama veya not ekleme."
    )


def user_intro(findings, intro_refs, topic, lang, feedback: list[str]) -> str:
    fb = ("\n\nÖNCEKİ DENEMENİN HATALARI (düzelt):\n- " + "\n- ".join(feedback)) if feedback else ""
    topic_line = f"Çalışmanın konusu: {topic}" if topic else "Konu, değişken adlarından çıkarılmalı."
    return (
        f"{topic_line}\n\nBULGULAR:\n{findings_block(findings, lang)}\n\n"
        f"KAYNAK LİSTESİ:\n{refs_block(intro_refs)}\n\n"
        f"GÖREV: Makalenin GİRİŞ bölümünü {LANG_NAME[lang]} yaz (3-5 paragraf, 300-500 kelime). "
        "Alanyazın bağlamını kur, araştırma boşluğunu belirt, çalışmanın amacını son paragrafta net ver. "
        "Bulgu sonuçlarını Giriş'te AÇIKLAMA (henüz bilinmiyor gibi yaz)." + fb
    )


def user_discussion(findings, refs, lang, feedback: list[str]) -> str:
    fb = ("\n\nÖNCEKİ DENEMENİN HATALARI (düzelt):\n- " + "\n- ".join(feedback)) if feedback else ""
    return (
        f"BULGULAR:\n{findings_block(findings, lang)}\n\n"
        f"KAYNAK LİSTESİ:\n{refs_block(refs)}\n\n"
        f"GÖREV: Makalenin TARTIŞMA bölümünü {LANG_NAME[lang]} yaz (4-6 paragraf, 400-600 kelime). "
        "Her ANLAMLI bulguyu ayrı ele al: sonucu alanyazınla karşılaştır (atıf işaretli), olası mekanizmayı yorumla. "
        "Anlamlı olmayan bulgulara kısaca değin. Etki büyüklüklerinin pratik anlamını yorumla." + fb
    )


def user_limitations(n_rows: int, lang: str) -> str:
    return (
        f"GÖREV: {n_rows} katılımcılı kesitsel bir nicel çalışma için SINIRLILIKLAR bölümünü "
        f"{LANG_NAME[lang]} yaz (1 paragraf, 80-150 kelime). Kesitsel desen, örneklem, çoklu karşılaştırma "
        "konularına değin. Atıf işareti kullanma."
    )


def user_title(findings, topic, lang) -> str:
    return (
        f"Konu: {topic or '(verilmedi)'}\nANLAMLI BULGULAR:\n{findings_block([f for f in findings if f.significant], lang)}\n\n"
        f"GÖREV: Bu çalışma için {LANG_NAME[lang]} akademik bir makale başlığı öner (en fazla 15 kelime). "
        "Yalnızca başlığı yaz."
    )


def system_selector() -> str:
    return (
        "Sen titiz bir editörsün. Sana aynı bölüm için birden fazla taslak verilecek. "
        "En iyi taslağı seç. Yanıtını JSON ver: {\"best\": <taslak numarası 1'den başlar>, \"reason\": \"...\"}"
    )


def user_selector(drafts: list[str]) -> str:
    parts = [f"--- TASLAK {i+1} ---\n{d}" for i, d in enumerate(drafts)]
    return (
        "\n\n".join(parts)
        + "\n\nAkademik derinlik, akıcılık ve atıf kullanımına göre en iyi taslağı seç (JSON)."
    )


def system_editor(lang: str) -> str:
    return (
        f"Sen bir akademik dil editörüsün. Verilen {LANG_NAME[lang]} metni dilbilgisi, akıcılık ve akademik "
        f"üslup açısından düzelt. ANLAMI, SAYILARI ve [n] atıf işaretlerini DEĞİŞTİRME; işaret ekleme/çıkarma. "
        "Yanıt olarak yalnızca düzeltilmiş metni yaz."
    )


def system_reviewer(lang: str) -> str:
    return (
        "Sen 'Reviewer 2' olarak bilinen sert ama adil bir hakemsin. Nicel araştırma makalelerini metodoloji, "
        "alanyazın bağlantısı, iç tutarlılık ve raporlama kalitesi açısından acımasızca değerlendirirsin. "
        "Yanıtını JSON dizisi olarak ver: "
        '[{"section": "intro|methods|results|discussion|limitations", "critique": "...", '
        '"requires_new_literature": true|false}] — en fazla 5 eleştiri, en önemlilerden başla. '
        f"Eleştirileri {LANG_NAME[lang]} yaz."
    )


def user_reviewer(sections: dict[str, str], findings, lang) -> str:
    text = "\n\n".join(f"## {k.upper()}\n{v}" for k, v in sections.items() if v)
    return (
        f"MAKALE:\n{text}\n\nBULGULAR (gerçek değerler):\n{findings_block(findings, lang)}\n\n"
        "Bu makaleyi hakem olarak değerlendir (JSON)."
    )


def system_revisor(lang: str) -> str:
    return (
        f"Sen makale revizyonu yapan bir akademik yazarsın. Hakem eleştirisini gidermek için verilen bölümü "
        f"{LANG_NAME[lang]} yeniden yaz. {CITE_RULE} {NUMBER_RULE} Yanıt olarak yalnızca revize bölüm metnini yaz."
    )


def user_revisor(section_name: str, section_text: str, critique: str, refs, findings, lang) -> str:
    return (
        f"HAKEM ELEŞTİRİSİ ({section_name}): {critique}\n\n"
        f"MEVCUT BÖLÜM:\n{section_text}\n\n"
        f"KAYNAK LİSTESİ:\n{refs_block(refs)}\n\nBULGULAR:\n{findings_block(findings, lang)}\n\n"
        "Bölümü eleştiriyi karşılayacak şekilde revize et."
    )


def system_coherence_validator() -> str:
    return (
        "Sen bir kalite denetçisisin. Verilen makale bölümünün istenen ölçütleri karşılayıp karşılamadığını "
        'değerlendir. Yanıt JSON: {"pass": true|false, "problems": ["..."]} — küçük üslup sorunlarını değil, '
        "yalnızca ciddi sorunları (eksik amaç, bulgularla çelişki, kopuk mantık) bildir."
    )


def user_coherence(section_name: str, text: str, findings, lang) -> str:
    return (
        f"BÖLÜM ({section_name}):\n{text}\n\nBULGULAR:\n{findings_block(findings, lang)}\n\n"
        "Bu bölüm bulgularla tutarlı ve amaca uygun mu? (JSON)"
    )


def user_queries(findings, topic, lang) -> str:
    return (
        f"Çalışma konusu: {topic or '(verilmedi)'}\n\nANLAMLI BULGULAR:\n"
        f"{findings_block([f for f in findings if f.significant], lang)}\n\n"
        "GÖREV: Her anlamlı bulgu için 2 İngilizce akademik literatür arama sorgusu ve ayrıca giriş bölümü "
        "için 2 genel sorgu üret. Sorgular 3-6 kelimelik anahtar kelime dizileri olsun (soru cümlesi değil). "
        'Yanıt JSON: {"F1": ["query", "query"], ..., "INTRO": ["query", "query"]}'
    )
