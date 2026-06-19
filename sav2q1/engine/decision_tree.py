"""Test seçim karar ağacı — SAF, birim test edilebilir fonksiyonlar.

Sağlık bilimleri verisi için "doğru testi" seçen mantık burada izole edilir ki
golden/branch testleriyle doğrulanabilsin. Her fonksiyon (test_id, gerekçe)
döndürür; gerekçe ledger'a yazılır ve Yöntem'de aynen kullanılır.
"""

from __future__ import annotations


def choose_two_group_test(all_normal: bool | None, equal_variance: bool, paired: bool) -> tuple[str, str]:
    """İki gruplu karşılaştırmada test seçimi.

    all_normal: tüm grupların Shapiro'ya göre normal olup olmadığı (None=karar yok).
    """
    if paired:
        if all_normal:
            return ("paired_t", "İki eşleştirilmiş ölçüm normal dağıldığından eşli örneklem t testi seçildi.")
        return ("wilcoxon", "Eşleştirilmiş ölçümler normallik varsayımını karşılamadığından (Shapiro p < 0,05) Wilcoxon işaretli sıra testi seçildi.")
    # bağımsız iki grup
    if all_normal:
        if equal_variance:
            return ("student_t", "Sonuç değişkeni her iki grupta normal dağıldığından ve varyanslar homojen olduğundan (Levene p > 0,05) bağımsız örneklem (Student) t testi seçildi.")
        return ("welch_t", "Sonuç değişkeni normal dağılsa da varyans homojenliği sağlanmadığından (Levene p < 0,05) Welch düzeltmeli t testi seçildi.")
    return ("mann_whitney_u", "Sonuç değişkeni en az bir grupta normallik varsayımını karşılamadığından (Shapiro p < 0,05) ve iki bağımsız grup karşılaştırıldığından Mann-Whitney U testi seçildi.")


def choose_multi_group_test(all_normal: bool | None, equal_variance: bool, repeated: bool) -> tuple[str, str]:
    """İkiden çok gruplu karşılaştırmada test seçimi."""
    if repeated:
        if all_normal:
            return ("rm_anova", "İkiden çok tekrarlı ölçüm normal dağıldığından tekrarlı ölçümler ANOVA seçildi.")
        return ("friedman", "Tekrarlı ölçümler normallik varsayımını karşılamadığından Friedman testi seçildi.")
    if all_normal and equal_variance:
        return ("oneway_anova", "İkiden çok bağımsız grup normal dağıldığından ve varyanslar homojen olduğundan tek yönlü ANOVA (post-hoc Tukey) seçildi.")
    return ("kruskal_wallis", "İkiden çok bağımsız grup normallik/varyans varsayımlarını karşılamadığından Kruskal-Wallis H testi (post-hoc Dunn) seçildi.")


def choose_categorical_test(r: int, c: int, min_expected: float, paired: bool) -> tuple[str, str]:
    """Kategorik × kategorik test seçimi (beklenen göze göre)."""
    if paired and r == 2 and c == 2:
        return ("mcnemar", "Eşleştirilmiş 2×2 tablo için McNemar testi seçildi.")
    if r == 2 and c == 2 and min_expected < 5:
        return ("fisher_exact", "2×2 tabloda beklenen göze < 5 olduğundan Fisher kesin testi seçildi.")
    if r == 2 and c == 2:
        return ("chi_square_yates", "2×2 tablo için Yates süreklilik düzeltmeli ki-kare testi seçildi.")
    return ("chi_square", "R×C tablo için Pearson ki-kare bağımsızlık testi (Cramér's V) seçildi.")


def choose_correlation_test(both_continuous_normal: bool) -> tuple[str, str]:
    """İki nicel değişken arası korelasyon test seçimi."""
    if both_continuous_normal:
        return ("pearson", "Her iki değişken sürekli ve yaklaşık normal dağıldığından Pearson korelasyon katsayısı hesaplandı.")
    return ("spearman", "Değişkenlerden en az biri normallik/sürekli varsayımını karşılamadığından Spearman sıra korelasyonu hesaplandı.")
