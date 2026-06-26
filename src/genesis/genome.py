"""Genesis evrim mimarisinin genom tanımları.

İki katman:

* ``RobotGenome``  — Arena'daki bir trader robotunun (Titan) DNA'sı.
  Hangi indikatörlere ne ağırlık verdiği, eşikleri vb.
* ``GodGenome``    — Olimpos'taki bir Tanrı'nın yarattığı *evrenin fizik
  kuralları*: hangi indikatörlere izin var, kaldıraç, agresiflik ve
  robotların bu evrende ne hızda mutasyona uğradığı (meta-optimizasyon).

Genomlar saf veri sınıflarıdır; rastgele üretim, mutasyon ve çaprazlama
operatörleri buradadır. Determinism için tüm rastgelelik dışarıdan verilen
``random.Random`` örneği üzerinden akar.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

# Sistemde tanınan indikatör "oy" kaynakları. God maskesi bu anahtarları kullanır.
INDICATORS: tuple[str, ...] = ("rsi", "trend", "bb", "macd")


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _jitter(rng: random.Random, value: float, lo: float, hi: float, scale: float) -> float:
    """Değeri aralık genişliğinin ``scale`` oranında gauss gürültüsüyle oynatır."""
    span = hi - lo
    return _clamp(value + rng.gauss(0.0, span * scale), lo, hi)


# --------------------------------------------------------------------------- #
# Katman 2: Robot (Titan)
# --------------------------------------------------------------------------- #
@dataclass
class RobotGenome:
    """Tek bir trader robotunun parametre seti.

    Ağırlıklar *işaretlidir*: pozitif ağırlık indikatörün klasik yorumunu
    (RSI düşükse al), negatif ağırlık ters/ortalamaya-dönüş yorumunu temsil
    eder. Böylece robotlar trend-takipçisi veya kontrasyon olarak evrimleşebilir.
    """

    # indikatör -> ağırlık [-2, 2]
    weights: dict[str, float] = field(default_factory=dict)
    rsi_period: int = 14
    rsi_low: float = 30.0
    rsi_high: float = 70.0
    ema_fast: int = 20
    ema_slow: int = 100
    bb_period: int = 20
    bb_std: float = 2.0
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    entry_threshold: float = 0.6  # |skor| bu eşiği aşınca pozisyon açılır

    def min_bars(self) -> int:
        # En yavaş indikatörün ısınması için gereken bar sayısı.
        return max(self.ema_slow, self.macd_slow + self.macd_signal, self.bb_period) + 2

    @staticmethod
    def random(rng: random.Random) -> "RobotGenome":
        return RobotGenome(
            weights={ind: rng.uniform(-2.0, 2.0) for ind in INDICATORS},
            rsi_period=rng.randint(5, 30),
            rsi_low=rng.uniform(10.0, 40.0),
            rsi_high=rng.uniform(60.0, 90.0),
            ema_fast=rng.randint(5, 50),
            ema_slow=rng.randint(60, 250),
            bb_period=rng.randint(10, 40),
            bb_std=rng.uniform(1.5, 3.0),
            macd_fast=rng.randint(6, 16),
            macd_slow=rng.randint(20, 40),
            macd_signal=rng.randint(5, 14),
            entry_threshold=rng.uniform(0.2, 1.5),
        )

    def mutate(self, rng: random.Random, rate: float) -> "RobotGenome":
        """``rate`` evrenin (Tanrı'nın) belirlediği mutasyon şiddeti.

        Her gen ``rate`` olasılıkla ve aralığının ``rate`` oranında oynatılır.
        """

        def maybe(value, mutate_fn):
            return mutate_fn() if rng.random() < rate else value

        new_weights = {
            ind: maybe(w, lambda w=w: _clamp(w + rng.gauss(0, 2.0 * rate), -2.0, 2.0))
            for ind, w in self.weights.items()
        }
        return RobotGenome(
            weights=new_weights,
            rsi_period=int(maybe(self.rsi_period, lambda: _jitter(rng, self.rsi_period, 5, 30, rate))),
            rsi_low=maybe(self.rsi_low, lambda: _jitter(rng, self.rsi_low, 10, 40, rate)),
            rsi_high=maybe(self.rsi_high, lambda: _jitter(rng, self.rsi_high, 60, 90, rate)),
            ema_fast=int(maybe(self.ema_fast, lambda: _jitter(rng, self.ema_fast, 5, 50, rate))),
            ema_slow=int(maybe(self.ema_slow, lambda: _jitter(rng, self.ema_slow, 60, 250, rate))),
            bb_period=int(maybe(self.bb_period, lambda: _jitter(rng, self.bb_period, 10, 40, rate))),
            bb_std=maybe(self.bb_std, lambda: _jitter(rng, self.bb_std, 1.5, 3.0, rate)),
            macd_fast=int(maybe(self.macd_fast, lambda: _jitter(rng, self.macd_fast, 6, 16, rate))),
            macd_slow=int(maybe(self.macd_slow, lambda: _jitter(rng, self.macd_slow, 20, 40, rate))),
            macd_signal=int(maybe(self.macd_signal, lambda: _jitter(rng, self.macd_signal, 5, 14, rate))),
            entry_threshold=maybe(
                self.entry_threshold, lambda: _jitter(rng, self.entry_threshold, 0.2, 1.5, rate)
            ),
        )

    @staticmethod
    def crossover(a: "RobotGenome", b: "RobotGenome", rng: random.Random) -> "RobotGenome":
        """Uniform crossover — her gen ebeveynlerden rastgele seçilir."""
        pick = lambda x, y: x if rng.random() < 0.5 else y  # noqa: E731
        weights = {
            ind: pick(a.weights[ind], b.weights[ind]) for ind in a.weights
        }
        return RobotGenome(
            weights=weights,
            rsi_period=pick(a.rsi_period, b.rsi_period),
            rsi_low=pick(a.rsi_low, b.rsi_low),
            rsi_high=pick(a.rsi_high, b.rsi_high),
            ema_fast=pick(a.ema_fast, b.ema_fast),
            ema_slow=pick(a.ema_slow, b.ema_slow),
            bb_period=pick(a.bb_period, b.bb_period),
            bb_std=pick(a.bb_std, b.bb_std),
            macd_fast=pick(a.macd_fast, b.macd_fast),
            macd_slow=pick(a.macd_slow, b.macd_slow),
            macd_signal=pick(a.macd_signal, b.macd_signal),
            entry_threshold=pick(a.entry_threshold, b.entry_threshold),
        )


# --------------------------------------------------------------------------- #
# Katman 1: Tanrı (Evren Mimarı)
# --------------------------------------------------------------------------- #
@dataclass
class GodGenome:
    """Bir evrenin fizik kuralları — robot evriminin sınırlarını çizer.

    * ``mask``          : hangi indikatörler bu evrende *aktif* (0/1).
    * ``leverage``      : kaldıraç çarpanı; 1.0 = kaldıraç yok ("yasak").
    * ``aggression``    : eşikleri ölçekler; yüksek = daha çok/erken işlem.
    * ``mutation_rate`` : bu evrende robotların mutasyon şiddeti (meta-gen).
    """

    mask: dict[str, int] = field(default_factory=dict)
    leverage: float = 1.0
    aggression: float = 1.0
    mutation_rate: float = 0.2

    def active_indicators(self) -> list[str]:
        return [ind for ind, on in self.mask.items() if on]

    def describe(self) -> str:
        inds = ",".join(self.active_indicators()) or "yok"
        lev = "yasak" if self.leverage <= 1.0 else f"{self.leverage:.1f}x"
        return (
            f"indikatörler=[{inds}] kaldıraç={lev} "
            f"agresiflik={self.aggression:.2f} mut={self.mutation_rate:.2f}"
        )

    @staticmethod
    def random(rng: random.Random, max_leverage: float, allow_leverage: bool) -> "GodGenome":
        # En az bir indikatör daima açık olmalı.
        mask = {ind: rng.randint(0, 1) for ind in INDICATORS}
        if not any(mask.values()):
            mask[rng.choice(INDICATORS)] = 1
        lev = rng.uniform(1.0, max_leverage) if allow_leverage else 1.0
        return GodGenome(
            mask=mask,
            leverage=lev,
            aggression=rng.uniform(0.5, 2.0),
            mutation_rate=rng.uniform(0.05, 0.5),
        )

    def mutate(
        self, rng: random.Random, rate: float, max_leverage: float, allow_leverage: bool
    ) -> "GodGenome":
        new_mask = dict(self.mask)
        for ind in new_mask:
            if rng.random() < rate:
                new_mask[ind] ^= 1  # indikatörü aç/kapat
        if not any(new_mask.values()):
            new_mask[rng.choice(INDICATORS)] = 1

        lev = self.leverage
        if allow_leverage and rng.random() < rate:
            lev = _jitter(rng, self.leverage, 1.0, max_leverage, rate)
        elif not allow_leverage:
            lev = 1.0

        return GodGenome(
            mask=new_mask,
            leverage=lev,
            aggression=_jitter(rng, self.aggression, 0.5, 2.0, rate)
            if rng.random() < rate
            else self.aggression,
            mutation_rate=_jitter(rng, self.mutation_rate, 0.05, 0.5, rate)
            if rng.random() < rate
            else self.mutation_rate,
        )

    @staticmethod
    def crossover(a: "GodGenome", b: "GodGenome", rng: random.Random) -> "GodGenome":
        pick = lambda x, y: x if rng.random() < 0.5 else y  # noqa: E731
        mask = {ind: pick(a.mask[ind], b.mask[ind]) for ind in a.mask}
        if not any(mask.values()):
            mask[rng.choice(list(mask))] = 1
        return GodGenome(
            mask=mask,
            leverage=pick(a.leverage, b.leverage),
            aggression=pick(a.aggression, b.aggression),
            mutation_rate=pick(a.mutation_rate, b.mutation_rate),
        )


__all__ = ["INDICATORS", "RobotGenome", "GodGenome"]
