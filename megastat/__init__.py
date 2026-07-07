"""MegaStat — sınırsız, kapsamlı istatistik motoru.

Bir veri dosyasını (CSV / Excel / SPSS .sav) alır ve hesaplanabilecek HER istatistiği hesaplar:

* Her değişken için tam betimsel istatistik bataryası (20+ ölçü + normallik testleri)
* Her sayısal çift için Pearson + Spearman + Kendall korelasyonları ve doğrusal regresyon
* Her kategorik × sayısal çift için t-testi / Welch / Mann-Whitney / ANOVA / Welch ANOVA /
  Kruskal-Wallis + etki büyüklükleri + Tukey post-hoc
* Her kategorik × kategorik çift için ki-kare / Fisher + Cramér's V + odds oranı
* Gelişmiş katman: eşleştirilmiş t / Wilcoxon, Friedman + Kendall W, Cohen kappa + McNemar,
  Cronbach alfa + McDonald omega + madde analizi, faktör analizi (KMO/Bartlett/varimax),
  çoklu doğrusal regresyon (VIF'li), lojistik regresyon (odds oranları), ROC (AUC + Youden)
* Tüm p-değerleri için Bonferroni, Holm ve Benjamini-Hochberg (FDR) düzeltmeleri

Hiçbir yapay zekâ yok; tüm sayılar SciPy / statsmodels / pandas ile deterministik hesaplanır.
PaperForge (app/) kodundan tamamen bağımsızdır.
"""

__version__ = "1.1.0"

from megastat.engine import analyze_dataframe, AnalysisResult
from megastat.loader import load_dataset

__all__ = ["analyze_dataframe", "AnalysisResult", "load_dataset", "__version__"]
