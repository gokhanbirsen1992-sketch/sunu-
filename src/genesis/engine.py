"""Genesis: Çift Katmanlı Evrim motoru.

Hiyerarşi (PDF'deki mimari):

    Tanrı (Olimpos)  →  Evren (fizik kuralları)  →  Robot (Arena)

* **Arena** — bir Tanrı'nın evreninde robot popülasyonunu evrimleştirir ve o
  evrenin Şampiyon Robotu'nu üretir (``evolve_arena``).
* **Olimpos** — Tanrıları evrimleştirir; her Tanrı'nın fitness'ı, kendi
  evreninden çıkardığı şampiyonun eğitim getirisidir (``evolve_olympos``).
* **Pantheon** — en iyi N Tanrı ve şampiyonları seçilip *görülmemiş* test
  verisinde (out-of-sample) HODL'a karşı sınanır (``run_genesis``).

Fitness değerlendirmesi, yol-bağımlı SL/TP ve kaldıraç içeren hızlı bir
vektörel simülatörle yapılır (``simulate``). Tüm rastgelelik tek bir tohumdan
(seed) türer; aynı tohum + aynı veri => aynı sonuç.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from src.indicators import atr as atr_indicator
from src.risk import RiskConfig

from .genome import GodGenome, RobotGenome
from .strategy import compute_scores, effective_threshold


# --------------------------------------------------------------------------- #
# Simülasyon / fitness
# --------------------------------------------------------------------------- #
@dataclass
class SimResult:
    return_pct: float          # toplam (kaldıraçlı) getiri %
    max_drawdown_pct: float    # ≤ 0
    num_trades: int
    win_rate: float
    ruined: bool               # equity ≤ 0 (likidasyon)

    def fitness(self) -> float:
        """GA'nın maksimize ettiği skor: getiri − drawdown cezası.

        Hiç işlem açmayan (atıl) robotlar hafifçe cezalandırılır ki evrim
        gerçekten alım-satım yapan genleri seçsin. Likidasyon ağır cezalıdır.
        """
        if self.ruined:
            return -1000.0 + self.return_pct
        if self.num_trades == 0:
            return -50.0
        return self.return_pct - 0.3 * abs(self.max_drawdown_pct)


def simulate(
    df: pd.DataFrame,
    scores: np.ndarray,
    threshold: float,
    atr_values: np.ndarray,
    risk: RiskConfig,
    leverage: float,
    fee_pct: float,
) -> SimResult:
    """Skor dizisinden yol-bağımlı (SL/TP, kaldıraç) bir backtest yürütür.

    ``run_backtest`` ile aynı mantık (sonraki barda SL/TP, ters sinyalde çıkış)
    ama GA için optimize edilmiş, tek geçişli bir döngüdür.
    """
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    close = df["close"].to_numpy(dtype=float)
    n = len(df)

    min_bars = int(np.argmax(~np.isnan(atr_values))) if np.isnan(atr_values).any() else 0
    min_bars = max(min_bars, risk.atr_period + 1)

    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    wins = 0
    trades = 0
    ruined = False
    position: dict | None = None

    def close_position(side: str, entry: float, exit_p: float) -> None:
        nonlocal equity, peak, max_dd, wins, trades, ruined
        raw = (exit_p / entry - 1.0) if side == "BUY" else (entry / exit_p - 1.0)
        raw -= 2 * fee_pct
        pnl = raw * leverage
        equity *= 1 + pnl
        trades += 1
        if pnl > 0:
            wins += 1
        if equity <= 0:
            equity = 0.0
            ruined = True
        peak = max(peak, equity)
        if peak > 0:
            max_dd = min(max_dd, equity / peak - 1.0)

    for i in range(min_bars, n - 1):
        if ruined:
            break
        cur_close = close[i]
        nh, nl = high[i + 1], low[i + 1]

        # 1) Açık pozisyon: sonraki bar SL/TP tetikledi mi?
        if position is not None:
            side, sl, tp = position["side"], position["sl"], position["tp"]
            exit_p = None
            if side == "BUY":
                if nl <= sl:
                    exit_p = sl
                elif nh >= tp:
                    exit_p = tp
            else:
                if nh >= sl:
                    exit_p = sl
                elif nl <= tp:
                    exit_p = tp
            if exit_p is not None:
                close_position(side, position["entry"], exit_p)
                position = None
                if ruined:
                    break

        # 2) Sinyal
        s = scores[i]
        action = "BUY" if s >= threshold else "SELL" if s <= -threshold else "HOLD"

        # 3) Ters sinyalde kapat
        if position is not None and action in ("BUY", "SELL") and action != position["side"]:
            close_position(position["side"], position["entry"], cur_close)
            position = None
            if ruined:
                break

        # 4) Pozisyon aç
        if position is None and action in ("BUY", "SELL"):
            a = atr_values[i]
            a = float(a) if not math.isnan(a) else None
            if a and a > 0:
                sl_d, tp_d = risk.atr_sl_mult * a, risk.atr_tp_mult * a
            else:
                sl_d = cur_close * risk.fallback_sl_pct
                tp_d = sl_d * (risk.atr_tp_mult / risk.atr_sl_mult)
            if action == "BUY":
                sl, tp = cur_close - sl_d, cur_close + tp_d
            else:
                sl, tp = cur_close + sl_d, cur_close - tp_d
            position = {"side": action, "entry": cur_close, "sl": sl, "tp": tp}

    # Kalan pozisyonu son kapanışta kapat
    if position is not None and not ruined:
        close_position(position["side"], position["entry"], close[-1])

    return SimResult(
        return_pct=(equity - 1.0) * 100.0,
        max_drawdown_pct=max_dd * 100.0,
        num_trades=trades,
        win_rate=(wins / trades) if trades else 0.0,
        ruined=ruined,
    )


def evaluate_robot(
    df: pd.DataFrame,
    atr_values: np.ndarray,
    robot: RobotGenome,
    god: GodGenome,
    risk: RiskConfig,
    fee_pct: float,
) -> SimResult:
    scores = compute_scores(df, robot, god)
    th = effective_threshold(robot, god)
    return simulate(df, scores, th, atr_values, risk, god.leverage, fee_pct)


# --------------------------------------------------------------------------- #
# Genel GA yardımcısı
# --------------------------------------------------------------------------- #
def _evolve(
    population: list,
    fitness_of: Callable[[object], float],
    breed: Callable[[object, object], object],
    rng: random.Random,
    generations: int,
    elite: int,
    tournament: int,
) -> list[tuple[object, float]]:
    """Elitizm + turnuva seçilimi + çaprazlama ile bir popülasyonu evrimleştirir.

    Son neslin ``(birey, fitness)`` listesini fitness'a göre azalan döndürür.
    """
    scored = [(ind, fitness_of(ind)) for ind in population]

    def tournament_pick() -> object:
        contenders = rng.sample(scored, min(tournament, len(scored)))
        return max(contenders, key=lambda t: t[1])[0]

    for _ in range(max(0, generations - 1)):
        scored.sort(key=lambda t: t[1], reverse=True)
        survivors = [ind for ind, _ in scored[:elite]]
        children: list = []
        while len(survivors) + len(children) < len(population):
            child = breed(tournament_pick(), tournament_pick())
            children.append(child)
        next_pop = survivors + children
        scored = [(ind, fitness_of(ind)) for ind in next_pop]

    scored.sort(key=lambda t: t[1], reverse=True)
    return scored


# --------------------------------------------------------------------------- #
# Arena (Katman 2): robot evrimi
# --------------------------------------------------------------------------- #
@dataclass
class ArenaResult:
    champion: RobotGenome
    train: SimResult


def evolve_arena(
    df: pd.DataFrame,
    atr_values: np.ndarray,
    god: GodGenome,
    cfg: "GenesisConfig",
    risk: RiskConfig,
    rng: random.Random,
) -> ArenaResult:
    """Tek bir Tanrı'nın evreninde robotları evrimleştirip şampiyonu döndürür."""
    pop = [RobotGenome.random(rng) for _ in range(cfg.robot_population)]

    def fitness_of(robot: RobotGenome) -> float:
        return evaluate_robot(df, atr_values, robot, god, risk, cfg.fee_pct).fitness()

    def breed(a: RobotGenome, b: RobotGenome) -> RobotGenome:
        child = RobotGenome.crossover(a, b, rng)
        return child.mutate(rng, god.mutation_rate)  # mutasyon hızı = evrenin geni

    scored = _evolve(
        pop, fitness_of, breed, rng,
        generations=cfg.robot_generations,
        elite=cfg.elite,
        tournament=cfg.tournament,
    )
    champion = scored[0][0]
    return ArenaResult(
        champion=champion,
        train=evaluate_robot(df, atr_values, champion, god, risk, cfg.fee_pct),
    )


# --------------------------------------------------------------------------- #
# Olimpos (Katman 1): tanrı evrimi
# --------------------------------------------------------------------------- #
@dataclass
class Deity:
    god: GodGenome
    champion: RobotGenome
    train: SimResult           # şampiyonun arena (eğitim) performansı
    validation: SimResult      # Tanrı'nın yargılandığı görülmemiş pencere
    test: SimResult | None = None


def evolve_olympos(
    arena_df: pd.DataFrame,
    arena_atr: np.ndarray,
    val_df: pd.DataFrame,
    val_atr: np.ndarray,
    cfg: "GenesisConfig",
    risk: RiskConfig,
    rng: random.Random,
    on_progress: Callable[[str], None] | None = None,
) -> list[Deity]:
    """Tanrıları evrimleştirir. Her Tanrı kendi Arena'sını koşturur.

    Kritik nokta (aşırı uydurmaya karşı): robotlar ``arena_df`` üzerinde
    evrimleşir, ama Tanrı'nın fitness'ı şampiyonun *görmediği* ``val_df``
    (doğrulama) penceresindeki performansıdır. Böylece Olimpos, ezber yapan
    değil **genelleyen** robotlar üreten evren kurallarını seçer.

    Son neslin tüm Tanrılarını doğrulama fitness'ına göre azalan döndürür.
    """
    gods = [
        GodGenome.random(rng, cfg.max_leverage, cfg.allow_leverage)
        for _ in range(cfg.god_population)
    ]
    arena_cache: dict[int, ArenaResult] = {}

    def arena_for(god: GodGenome) -> ArenaResult:
        key = id(god)
        if key not in arena_cache:
            arena_cache[key] = evolve_arena(arena_df, arena_atr, god, cfg, risk, rng)
        return arena_cache[key]

    def fitness_of(god: GodGenome) -> float:
        champ = arena_for(god).champion
        return evaluate_robot(val_df, val_atr, champ, god, risk, cfg.fee_pct).fitness()

    def breed(a: GodGenome, b: GodGenome) -> GodGenome:
        child = GodGenome.crossover(a, b, rng)
        return child.mutate(rng, 0.3, cfg.max_leverage, cfg.allow_leverage)

    # _evolve'i elle yürütüyoruz ki nesil başına ilerleme bildirebilelim.
    scored = [(g, fitness_of(g)) for g in gods]
    if on_progress:
        best = max(scored, key=lambda t: t[1])
        on_progress(f"Nesil 1/{cfg.god_generations}: en iyi Tanrı fitness={best[1]:+.1f}")

    def tournament_pick(pool):
        contenders = rng.sample(pool, min(cfg.tournament, len(pool)))
        return max(contenders, key=lambda t: t[1])[0]

    for gen in range(1, cfg.god_generations):
        scored.sort(key=lambda t: t[1], reverse=True)
        survivors = [g for g, _ in scored[: cfg.elite]]
        children = []
        while len(survivors) + len(children) < cfg.god_population:
            children.append(breed(tournament_pick(scored), tournament_pick(scored)))
        gods = survivors + children
        arena_cache.clear()  # yeni nesil => arenalar yeniden koşar
        scored = [(g, fitness_of(g)) for g in gods]
        if on_progress:
            best = max(scored, key=lambda t: t[1])
            on_progress(
                f"Nesil {gen + 1}/{cfg.god_generations}: "
                f"en iyi Tanrı fitness={best[1]:+.1f}"
            )

    scored.sort(key=lambda t: t[1], reverse=True)
    deities = []
    for god, _ in scored:
        ar = arena_for(god)
        val = evaluate_robot(val_df, val_atr, ar.champion, god, risk, cfg.fee_pct)
        deities.append(
            Deity(god=god, champion=ar.champion, train=ar.train, validation=val)
        )
    return deities


# --------------------------------------------------------------------------- #
# Üst seviye akış
# --------------------------------------------------------------------------- #
@dataclass
class GenesisConfig:
    god_population: int = 8
    god_generations: int = 4
    robot_population: int = 16
    robot_generations: int = 6
    elite: int = 2
    tournament: int = 3
    pantheon_size: int = 5
    train_ratio: float = 0.7      # test dışı veri oranı (geri kalan = test)
    val_ratio: float = 0.3        # eğitim verisinin doğrulamaya ayrılan son dilimi
    max_leverage: float = 5.0
    allow_leverage: bool = True
    fee_pct: float = 0.001
    seed: int = 42


@dataclass
class GenesisResult:
    pantheon: list[Deity]
    hodl_test_return_pct: float
    arena_span: tuple[pd.Timestamp, pd.Timestamp]
    val_span: tuple[pd.Timestamp, pd.Timestamp]
    test_span: tuple[pd.Timestamp, pd.Timestamp]
    log: list[str] = field(default_factory=list)


def _atr_array(df: pd.DataFrame, period: int) -> np.ndarray:
    return atr_indicator(df["high"], df["low"], df["close"], period).to_numpy(dtype=float)


def run_genesis(
    df: pd.DataFrame,
    cfg: GenesisConfig,
    risk: RiskConfig,
    on_progress: Callable[[str], None] | None = None,
) -> GenesisResult:
    """Tam Genesis akışını yürütür: eğitim/test böl, evrimleştir, sına."""
    df = df.sort_values("timestamp").reset_index(drop=True)
    split = int(len(df) * cfg.train_ratio)
    val_split = int(split * (1.0 - cfg.val_ratio))
    min_window = risk.atr_period + 10
    if (
        val_split < min_window
        or split - val_split < min_window
        or len(df) - split < min_window
    ):
        raise ValueError(
            f"Genesis için yetersiz veri: {len(df)} bar (arena/doğrulama/test "
            f"≈ {val_split}/{split - val_split}/{len(df) - split}). "
            "Daha çok mum çekin (örn. --candles 1000)."
        )
    # Üç pencere: Arena (robotlar burada evrimleşir) → Doğrulama (Tanrılar burada
    # yargılanır) → Test (Pantheon burada, hiç görülmemiş veride sınanır).
    arena = df.iloc[:val_split].reset_index(drop=True)
    val = df.iloc[val_split:split].reset_index(drop=True)
    test = df.iloc[split:].reset_index(drop=True)

    log: list[str] = []

    def progress(msg: str) -> None:
        log.append(msg)
        if on_progress:
            on_progress(msg)

    progress(
        f"Yaratılış: {cfg.god_population} Tanrı × {cfg.robot_population} robot  ·  "
        f"arena {arena['timestamp'].iloc[0].date()}→{arena['timestamp'].iloc[-1].date()}  ·  "
        f"doğrulama {val['timestamp'].iloc[0].date()}→{val['timestamp'].iloc[-1].date()}"
    )

    rng = random.Random(cfg.seed)
    arena_atr = _atr_array(arena, risk.atr_period)
    val_atr = _atr_array(val, risk.atr_period)
    deities = evolve_olympos(
        arena, arena_atr, val, val_atr, cfg, risk, rng, on_progress=progress
    )

    # Pantheon: en iyi N Tanrı'yı görülmemiş test verisinde sına
    pantheon = deities[: cfg.pantheon_size]
    test_atr = _atr_array(test, risk.atr_period)
    progress(
        f"Pantheon: en iyi {len(pantheon)} Tanrı test ediliyor "
        f"({test['timestamp'].iloc[0].date()}→{test['timestamp'].iloc[-1].date()})"
    )
    for d in pantheon:
        d.test = evaluate_robot(test, test_atr, d.champion, d.god, risk, cfg.fee_pct)

    hodl = (float(test["close"].iloc[-1]) / float(test["close"].iloc[0]) - 1.0) * 100.0

    return GenesisResult(
        pantheon=pantheon,
        hodl_test_return_pct=hodl,
        arena_span=(arena["timestamp"].iloc[0], arena["timestamp"].iloc[-1]),
        val_span=(val["timestamp"].iloc[0], val["timestamp"].iloc[-1]),
        test_span=(test["timestamp"].iloc[0], test["timestamp"].iloc[-1]),
        log=log,
    )


def export_pantheon(result: GenesisResult, path: str) -> None:
    """Pantheon'u (Tanrılar + şampiyon genomları + metrikler) JSON'a yazar.

    PDF'deki 5. aşama: laboratuvardan çıkan şampiyonları saklamak/dağıtmak.
    Kaydedilen genom, ``EvolvableStrategy`` ile yeniden kurulup canlı kullanıma
    alınabilir.
    """
    import dataclasses
    import json

    def deity_dict(d: Deity) -> dict:
        return {
            "god": dataclasses.asdict(d.god),
            "champion": dataclasses.asdict(d.champion),
            "metrics": {
                "arena": dataclasses.asdict(d.train),
                "validation": dataclasses.asdict(d.validation),
                "test": dataclasses.asdict(d.test) if d.test else None,
            },
        }

    payload = {
        "spans": {
            "arena": [str(result.arena_span[0]), str(result.arena_span[1])],
            "validation": [str(result.val_span[0]), str(result.val_span[1])],
            "test": [str(result.test_span[0]), str(result.test_span[1])],
        },
        "hodl_test_return_pct": result.hodl_test_return_pct,
        "pantheon": [deity_dict(d) for d in result.pantheon],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


__all__ = [
    "GenesisConfig",
    "GenesisResult",
    "Deity",
    "SimResult",
    "simulate",
    "evaluate_robot",
    "evolve_arena",
    "evolve_olympos",
    "run_genesis",
    "export_pantheon",
]
