"""Karar ağacı dal seçim testleri — test seçim mantığını kilitler."""

from sav2q1.engine.decision_tree import (
    choose_two_group_test, choose_multi_group_test,
    choose_categorical_test, choose_correlation_test,
)


def test_two_group_normal_equalvar():
    assert choose_two_group_test(True, True, False)[0] == "student_t"


def test_two_group_normal_unequalvar():
    assert choose_two_group_test(True, False, False)[0] == "welch_t"


def test_two_group_nonnormal():
    assert choose_two_group_test(False, True, False)[0] == "mann_whitney_u"


def test_two_group_paired_normal():
    assert choose_two_group_test(True, True, True)[0] == "paired_t"


def test_two_group_paired_nonnormal():
    assert choose_two_group_test(False, True, True)[0] == "wilcoxon"


def test_multi_group():
    assert choose_multi_group_test(True, True, False)[0] == "oneway_anova"
    assert choose_multi_group_test(False, True, False)[0] == "kruskal_wallis"
    assert choose_multi_group_test(True, True, True)[0] == "rm_anova"


def test_categorical():
    assert choose_categorical_test(2, 2, min_expected=3, paired=False)[0] == "fisher_exact"
    assert choose_categorical_test(2, 2, min_expected=10, paired=False)[0] == "chi_square_yates"
    assert choose_categorical_test(3, 4, min_expected=10, paired=False)[0] == "chi_square"
    assert choose_categorical_test(2, 2, min_expected=10, paired=True)[0] == "mcnemar"


def test_correlation():
    assert choose_correlation_test(True)[0] == "pearson"
    assert choose_correlation_test(False)[0] == "spearman"
