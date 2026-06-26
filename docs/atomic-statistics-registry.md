# Atomic Registry of the Statistical Universe — v2.0
### İstatistiksel ve Matematiksel Evrenin Genişletilmiş & Düzeltilmiş Taksonomisi

Bu belge, istatistiksel ve hesaplamalı yöntemlerin kapsamlı bir referans haritasıdır.
v1'deki **7 sütunlu mimari** korunmuş; eksik bir temel sütun (**Zaman Serileri**) eklenmiş,
tüm analizin altında yatan bir **Sütun 0 (Metodolojik Temeller)** tanımlanmış ve birkaç
sınıflandırma hatası düzeltilmiştir.

> **Not — "eksiksiz" değil, "kapsamlı":** Hiçbir taksonomi gerçekten tüm yöntemleri içeremez.
> Bu registry, ana yöntem ailelerinin mantıklı ve genişletilebilir bir haritasıdır.

---

## Mimari Genel Bakış

| # | SÜTUN | ROL | TEMEL SORU |
|---|-------|-----|------------|
| 0 | Metodolojik Temeller | **Zemin** | "Sonucuma ne kadar güvenebilirim?" |
| 1 | Frequentist Inference | **Yargıç** | "Bu sonuç tesadüf mü?" |
| 2 | Predictive / Algorithmic ML | **Kâhin** | "Sırada ne var / değer kaç olacak?" |
| 3 | Causal Inference | **Mühendis** | "Müdahale edersem ne olur?" |
| 4 | Bayesian Probability | **Filozof** | "Belirsizliğim ne kadar?" |
| 5 | Information Theory | **Sinyalci** | "Burada ne kadar saf bilgi var?" |
| 6 | Cybernetics / Dynamic | **Karar Verici** | "Sistem zamanla nasıl davranmalı?" |
| 7 | Time Series & Stochastic | **Tarihçi** | "Geçmiş geleceği nasıl belirliyor?" |
| 8 | Structural / Geometric | **Geometrist** | "Verinin şekli ve bağlantıları ne?" |

---

## SÜTUN 0 — METODOLOJİK TEMELLER (Cross-Cutting)
*Her sütunun altında çalışan yatay katman. v1'de yoktu — en büyük yapısal eksikti.*

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Resampling & Validation** | Bootstrap, Jackknife, Permutation/Randomization Tests, k-Fold Cross-Validation, Leave-One-Out CV, Nested CV, Time-Series CV (rolling/expanding window) |
| **Optimizasyon** | Gradient Descent (SGD, Momentum, Adam, RMSProp), Newton/Quasi-Newton (BFGS, L-BFGS), Coordinate Descent, EM Algorithm, Simulated Annealing, Genetic/Evolutionary Algorithms, Bayesian Optimization, Convex Optimization (LP/QP) |
| **Model Seçimi & Karşılaştırma** | AIC, BIC, DIC, WAIC, Mallows' Cp, Likelihood Ratio Test, Cross-Entropy/Log-Loss, Regularization Path |
| **Çoklu Karşılaştırma Düzeltmeleri** | Bonferroni, Holm, Šidák, Benjamini-Hochberg (FDR), Tukey HSD, Scheffé, Dunnett |
| **Hesaplama & Etki Büyüklüğü** | Power Analysis, Sample Size Estimation, Effect Sizes (Cohen's d, η², Cliff's delta), Confidence/Credible Intervals |

---

## SÜTUN 1 — FREQUENTIST INFERENCE (Yargıç)

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Parametrik Testler** | Z-test, One-sample / Independent / Paired t-test, **Welch's t-test**, ANOVA (One-way, Two-way, Repeated Measures), MANOVA, ANCOVA, MANCOVA, Pearson Correlation, F-test |
| **Varyans Homojenliği** | Levene's, Bartlett's, Brown-Forsythe, Fligner-Killeen |
| **Non-Parametrik Testler** | Mann-Whitney U, Wilcoxon Signed-Rank, Kruskal-Wallis H, Friedman, Sign Test, Mood's Median, Jonckheere-Terpstra, Page's Trend, Cochran's Q, Spearman's Rho, Kendall's Tau |
| **Kategorik / Sayım Verisi** | Chi-Square (Goodness-of-fit & Independence), Fisher's Exact, McNemar's, Cochran-Mantel-Haenszel, G-test |
| **Dağılım & Normallik (GoF)** ⚙️*düzeltildi* | Shapiro-Wilk, Anderson-Darling, Kolmogorov-Smirnov, Lilliefors, Jarque-Bera, Runs Test (*v1'de Non-Parametrik altındaydı; bunlar uyum-iyiliği testleridir*) |
| **Regresyon & Karma Modeller** | OLS/GLM, **Linear Mixed Models (LMM)**, GEE, GAM, WLS, Robust Regression (M-estimators) |
| **Survival & Reliability** | Kaplan-Meier, Nelson-Aalen, Log-Rank, Cox Proportional Hazards, AFT, Weibull / Exponential / Log-Normal Regression, Gompertz, **Fine-Gray (competing risks)**, Frailty Models |

---

## SÜTUN 2 — PREDICTIVE / ALGORITHMIC ML (Kâhin)

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Lineer / Regularize Modeller** | OLS, Ridge, Lasso, ElasticNet, Quantile Regression, Logistic, Probit, Tobit, Poisson, Negative Binomial, **GAM** |
| **Diskriminant & Çekirdek** ➕*eklendi* | **LDA / QDA (Linear/Quadratic Discriminant Analysis)**, Support Vector Machines (SVM), Kernel Methods, k-NN, Naive Bayes |
| **Ağaç Tabanlı (Temel)** ➕*eklendi* | **Decision Tree (CART, C4.5, CHAID)** |
| **Ensemble Learning** | Bagging, Random Forest, Extra Trees, AdaBoost, Gradient Boosting (XGBoost, LightGBM, CatBoost), Stacking, Blending, Voting |
| **Deep Learning (ANN)** | MLP, CNN (ResNet, EfficientNet), RNN (LSTM, GRU), Transformers (Attention, BERT, GPT), Autoencoders / VAE, GANs, **Diffusion Models**, **Normalizing Flows**, GNN, PINNs |
| **Unsupervised — Kümeleme** | K-Means, Hierarchical, DBSCAN, OPTICS, GMM, **Spectral Clustering**, **Mean-Shift**, **Affinity Propagation** |
| **Unsupervised — Boyut İndirgeme** | PCA, Kernel PCA, ICA, **NMF**, **Factor Analysis**, t-SNE, UMAP, ISOMAP, LLE, **SOM** |
| **Anomali & Birliktelik** ➕*eklendi* | Isolation Forest, One-Class SVM, LOF, **Apriori / FP-Growth (association rules)** |

---

## SÜTUN 3 — CAUSAL INFERENCE (Mühendis)

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Yapısal Modeller** | DAGs, SCM, Front-door / Back-door Criterion, D-separation, Do-Calculus, Pearl's Structural Models |
| **Tahmin Motorları** | EconML, DoWhy, Double Machine Learning (DML), Orthogonal Random Forest, Meta-learners (S/T/X/R), Generalized Random Forest (GRF), **TMLE** |
| **Quasi-Experiments** | IV / 2SLS, Difference-in-Differences (DiD), **Event Study**, Regression Discontinuity (RDD), Propensity Score Matching (PSM), Inverse Probability Weighting (IPW), Synthetic Control |
| **Longitudinal / G-Methods** ➕*eklendi* | Marginal Structural Models, G-computation, G-estimation, **Mediation Analysis**, Mendelian Randomization |
| **Causal Discovery** | PC Algorithm, FCI, GES, LiNGAM, NOTEARS |

---

## SÜTUN 4 — BAYESIAN PROBABILITY (Filozof)

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Örnekleme & VI** | MCMC, Metropolis-Hastings, Gibbs Sampling, Hamiltonian Monte Carlo (HMC), NUTS, Importance Sampling, **Sequential Monte Carlo / Particle MCMC**, Variational Inference (VI), Laplace Approximation, **ABC (Approximate Bayesian Computation)**, **Expectation Propagation** |
| **Model Tipleri** | Bayesian Linear/GLM Regression, Hierarchical / Multilevel Modeling, Gaussian Processes (GP), Bayesian Networks, LDA (Latent Dirichlet Allocation), HMM, Kalman & Particle Filters |
| **İleri Bayesçi** ➕*eklendi* | **Empirical Bayes**, **Bayesian Model Averaging**, **Dirichlet Process / Nonparametric Bayes**, Conjugate Priors |

---

## SÜTUN 5 — INFORMATION THEORY (Sinyalci)
*v1'de en zayıf sütundu; ikinci alt sınıf ve metrikler eklendi.*

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Entropi & Metrikler** | Shannon / Joint / Conditional Entropy, **Rényi & Tsallis Entropy**, Mutual Information, KL Divergence, Jensen-Shannon Divergence, Cross-Entropy, Transfer Entropy, Symbolic Transfer Entropy |
| **Karmaşıklık & Kodlama** | Kolmogorov Complexity, Minimum Description Length (MDL), **Fisher Information**, **Information Bottleneck**, **Partial Information Decomposition (PID)**, Rate-Distortion |

---

## SÜTUN 6 — CYBERNETICS / DYNAMIC (Karar Verici)

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Reinforcement Learning** | Q-Learning, SARSA, **TD-Learning**, DQN (+Rainbow), Policy Gradient (REINFORCE), Actor-Critic (A3C/A2C), PPO, SAC, DDPG, **TD3**, **Model-Based RL**, MCTS |
| **Bandits & Online** ➕*eklendi* | Multi-Armed Bandits, UCB, **Thompson Sampling**, Contextual Bandits |
| **Kontrol & Sistemler** | PID, Model Predictive Control (MPC), LQR / LQG, State-Space Models, **Optimal Control (Pontryagin)**, **Adaptive / H∞ Control**, Lyapunov Stability, Bellman Equations |
| **Oyun Teorisi** | Nash Equilibrium, Shapley Values, Minimax, Mean-Field Games |

---

## SÜTUN 7 — TIME SERIES & STOCHASTIC PROCESSES (Tarihçi)
*v1'de eksik olan kritik sütun. Finans ve longitudinal tıbbi izlem için olmazsa olmaz.*

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Klasik & Ekonometrik** | AR, MA, ARMA, ARIMA, SARIMA, ARIMAX/SARIMAX, Exponential Smoothing (Holt-Winters), Theta |
| **Çok Değişkenli** | VAR, VECM, Cointegration (Engle-Granger, Johansen), **Granger Causality**, Impulse Response |
| **Volatilite (Finans)** | ARCH, GARCH (E/GJR/IGARCH), Stochastic Volatility |
| **Durağanlık & Tanı** | ADF, KPSS, Phillips-Perron, ACF/PACF, Ljung-Box, Durbin-Watson |
| **Spektral & Dalgacık** | Fourier Analysis, Periodogram, Wavelet Transform, Hilbert-Huang (EMD) |
| **Modern / ML** | Prophet, N-BEATS, DeepAR, Temporal Fusion Transformer, TCN |
| **Stokastik Süreçler** | Markov Chains, Poisson/Hawkes Processes, Brownian Motion, Itô Calculus, Ornstein-Uhlenbeck |

---

## SÜTUN 8 — STRUCTURAL / GEOMETRIC (Geometrist)

| ALT SINIF | ATOMİK YÖNTEMLER |
|-----------|------------------|
| **Graph Theory** | Degree / Betweenness / Eigenvector / Closeness Centrality, PageRank, Community Detection (Louvain, Leiden, **Modularity**), Path Analysis, Assortativity |
| **Ağ Modelleri** | Erdős-Rényi, **Watts-Strogatz (small-world)**, Scale-Free (Barabási-Albert), **Stochastic Block Models** |
| **Graph Embeddings** ➕*eklendi* | **Node2Vec, DeepWalk**, Spectral Embedding (GNN ile köprü) |
| **Topology (TDA)** | Persistent Homology, Mapper Algorithm, Betti Numbers |
| **Chaos & Fractals** | Lyapunov Exponents, Hurst Exponent, Fractal Dimension, Phase Space Reconstruction, **Recurrence Quantification Analysis** |
| **Spatial Statistics** ➕*eklendi* | Kriging, Moran's I, Geary's C, GWR (Geographically Weighted Regression) |

---

## v1 → v2 Değişiklik Özeti

**🟢 Eklenen sütunlar**
- **Sütun 0 — Metodolojik Temeller** (Bootstrap, CV, optimizasyon, AIC/BIC, çoklu karşılaştırma)
- **Sütun 7 — Time Series & Stochastic Processes** (ARIMA, GARCH, VAR, Granger, Wavelet)

**🔧 Düzeltilen sınıflandırmalar**
- Normallik/GoF testleri (Shapiro-Wilk, A-D, K-S) → Non-Parametrik'ten **ayrı GoF alt sınıfına** taşındı
- **Decision Tree (CART)** temel öğrenici olarak eklendi (ensemble'dan önce)
- **LDA/QDA (Linear Discriminant Analysis)** eklendi — "LDA = Latent Dirichlet Allocation" ile karışmasın diye netleştirildi

**➕ Genişletilen ailaler**
- ML: GAM, NMF, Spectral/Mean-Shift clustering, Diffusion, Apriori/FP-Growth
- Causal: G-methods, TMLE, Mediation, Mendelian Randomization
- Bayesian: ABC, Empirical Bayes, BMA, Dirichlet Process
- Info-Theory: Fisher Information, Rényi/Tsallis, Information Bottleneck, PID
- Cybernetics: Thompson Sampling, TD3, Model-Based RL, optimal/adaptif kontrol
- Structural: Graph embeddings, Spatial statistics, small-world modelleri

**🔭 Felsefi düzeltme**
- "Eksiksiz / 5 milyonuncu yöntem" iddiası → "kapsamlı ve genişletilebilir referans" olarak yeniden çerçevelendi.
