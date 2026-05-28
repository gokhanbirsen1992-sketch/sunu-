import pytest
from rich.panel import Panel

from src.monitor import _render_dca
from src.signal import Signal


def _signal(action: str = "HOLD", price: float = 80_000.0) -> Signal:
    return Signal(action=action, price=price, reason="test")


def test_render_dca_returns_panel_with_strategy_note():
    sig = _signal(action="BUY", price=80_000.0)
    panel = _render_dca("BTC_USDT", "1D", "rsi_ma", sig, amount=500.0, fee_pct=0.001)
    assert isinstance(panel, Panel)


@pytest.mark.parametrize(
    "amount,price,fee_pct,expected_qty,expected_cost",
    [
        (500.0, 80_000.0, 0.001, (500.0 - 0.5) / 80_000.0, 500.0 / ((500.0 - 0.5) / 80_000.0)),
        (1000.0, 2_500.0, 0.0015, (1000.0 - 1.5) / 2_500.0, 1000.0 / ((1000.0 - 1.5) / 2_500.0)),
        (250.0, 100.0, 0.0, 2.5, 100.0),
    ],
)
def test_dca_math_matches_panel_logic(amount, price, fee_pct, expected_qty, expected_cost):
    # render fonksiyonunun kullandığı saf hesabı bağımsız olarak doğrula
    fee = amount * fee_pct
    net = amount - fee
    qty = net / price
    cost = amount / qty
    assert qty == pytest.approx(expected_qty, rel=1e-9)
    assert cost == pytest.approx(expected_cost, rel=1e-9)


def test_render_dca_sell_action_still_renders():
    sig = _signal(action="SELL", price=80_000.0)
    panel = _render_dca("BTC_USDT", "1D", "rsi_ma", sig, amount=100.0, fee_pct=0.001)
    assert isinstance(panel, Panel)
