"""Canlı izleme döngüsü — Rich ile renkli terminal tablosu."""
from __future__ import annotations

import logging
import math
import time
from datetime import datetime, timezone

import pandas as pd
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.exchange import Exchange, ExchangeError
from src.indicators import atr
from src.risk import RiskConfig, compute_sl_tp, position_size_usdt
from src.signal import Signal
from src.strategies.base import Strategy

logger = logging.getLogger(__name__)


def _color_for_action(action: str) -> str:
    return {"BUY": "bold green", "SELL": "bold red", "HOLD": "yellow"}.get(action, "white")


def _render(
    symbol: str,
    timeframe: str,
    strategy_name: str,
    signal: Signal,
    last_change: datetime | None,
) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="right", style="dim")
    table.add_column()

    table.add_row("Sembol", f"[bold]{symbol}[/bold]   ({timeframe})")
    table.add_row("Strateji", strategy_name)
    table.add_row("Fiyat", f"[bold cyan]{signal.price:,.2f}[/bold cyan] USDT")

    if signal.indicators:
        ind_str = "  ".join(f"{k}={v:.2f}" for k, v in signal.indicators.items())
        table.add_row("Göstergeler", ind_str)

    table.add_row(
        "Sinyal",
        Text(signal.action, style=_color_for_action(signal.action)),
    )

    if signal.stop_loss is not None:
        table.add_row("Stop-Loss", f"[red]{signal.stop_loss:,.2f}[/red]")
    if signal.take_profit is not None:
        table.add_row("Take-Profit", f"[green]{signal.take_profit:,.2f}[/green]")
    if signal.suggested_size_usdt is not None:
        table.add_row("Önerilen boyut", f"{signal.suggested_size_usdt:,.2f} USDT")

    table.add_row("Sebep", signal.reason)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    table.add_row("Güncellenme", f"[dim]{now}[/dim]")
    if last_change:
        table.add_row(
            "Son sinyal değişimi",
            f"[dim]{last_change.strftime('%Y-%m-%d %H:%M:%S UTC')}[/dim]",
        )

    return Panel(
        table,
        title="[bold]BTC/USDT Sinyal Botu — Crypto.com[/bold]",
        subtitle="[dim]Yatırım tavsiyesi değildir. Sadece eğitim amaçlıdır.[/dim]",
        border_style=_color_for_action(signal.action),
    )


def _render_dca(
    symbol: str,
    timeframe: str,
    strategy_name: str,
    signal: Signal,
    amount: float,
    fee_pct: float,
) -> Panel:
    """DCA için anlık fiyat + alınabilir miktar + sinyal yorumu paneli."""
    fee = amount * fee_pct
    net_amount = amount - fee
    coin_qty = net_amount / signal.price if signal.price > 0 else 0.0
    effective_cost = amount / coin_qty if coin_qty > 0 else 0.0

    base_asset = symbol.split("_")[0] if "_" in symbol else symbol
    quote_asset = symbol.split("_")[1] if "_" in symbol else "USDT"

    note = {
        "BUY": "Strateji şu an alım sinyali veriyor — DCA için uygun zaman.",
        "HOLD": "Strateji belirsiz; DCA disiplini gereği yine de alabilirsin.",
        "SELL": "Strateji satış sinyalinde — istersen bir sonraki aya erteleyebilirsin (DCA disiplini ihlal etmez).",
    }.get(signal.action, "")

    table = Table.grid(padding=(0, 2))
    table.add_column(justify="right", style="dim")
    table.add_column()

    table.add_row("Sembol", f"[bold]{symbol}[/bold]   ({timeframe})")
    table.add_row("Strateji", strategy_name)
    table.add_row("Anlık Fiyat", f"[bold cyan]{signal.price:,.2f}[/bold cyan] {quote_asset}")

    if signal.indicators:
        ind_str = "  ".join(f"{k}={v:.2f}" for k, v in signal.indicators.items())
        table.add_row("Göstergeler", ind_str)

    table.add_row(
        "Sinyal",
        Text(signal.action, style=_color_for_action(signal.action)),
    )

    table.add_row("Yatırım Tutarı", f"[bold]{amount:,.2f}[/bold] {quote_asset}")
    table.add_row("Komisyon", f"[dim]{fee:,.4f} {quote_asset}  ({fee_pct*100:.3f}%)[/dim]")
    table.add_row("Net Tutar", f"{net_amount:,.4f} {quote_asset}")
    table.add_row("Alınabilir Miktar", f"[bold green]{coin_qty:.8f}[/bold green] {base_asset}")
    table.add_row("Efektif Birim Maliyet", f"{effective_cost:,.2f} {quote_asset}/{base_asset}")

    if note:
        table.add_row("Strateji Notu", f"[{_color_for_action(signal.action)}]{note}[/]")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    table.add_row("Hesaplama Zamanı", f"[dim]{now}[/dim]")

    return Panel(
        table,
        title="[bold]Aylık DCA — Maaş Kalanı Yatırımı[/bold]",
        subtitle="[dim]Yatırım tavsiyesi değildir. Gerçek emir verilmez.[/dim]",
        border_style=_color_for_action(signal.action),
    )


def _enrich_signal(
    signal: Signal,
    df: pd.DataFrame,
    risk: RiskConfig,
) -> Signal:
    """Risk parametrelerini sinyale ekler (HOLD için bile referans olarak)."""
    atr_series = atr(df["high"], df["low"], df["close"], risk.atr_period)
    atr_val = atr_series.iloc[-1]
    atr_val = float(atr_val) if not math.isnan(atr_val) else None

    side = signal.action if signal.action in ("BUY", "SELL") else "BUY"  # ref. yön
    sl, tp = compute_sl_tp(signal.price, side, atr_val, risk)
    size = position_size_usdt(signal.price, sl, risk)

    if signal.action in ("BUY", "SELL"):
        signal.stop_loss = sl
        signal.take_profit = tp
        signal.suggested_size_usdt = size
    if atr_val is not None:
        signal.indicators["atr"] = atr_val
    return signal


def run_monitor(
    exchange: Exchange,
    strategy: Strategy,
    risk: RiskConfig,
    symbol: str = "BTC_USDT",
    timeframe: str = "1D",
    candle_count: int = 300,
    poll_interval_sec: int = 30,
    console: Console | None = None,
) -> None:
    """Sonsuz döngü: ticker'ı her `poll_interval_sec`'te çek, sinyal üret, ekranı yenile."""
    console = console or Console()
    df = exchange.get_candles(symbol, timeframe, candle_count)
    last_candle_ts = df["timestamp"].iloc[-1]

    last_action: str | None = None
    last_change_at: datetime | None = None

    initial_signal = Signal(action="HOLD", price=float(df["close"].iloc[-1]), reason="Başlatılıyor...")

    with Live(
        _render(symbol, timeframe, strategy.name, initial_signal, None),
        console=console,
        refresh_per_second=2,
        screen=False,
    ) as live:
        while True:
            try:
                ticker = exchange.get_ticker(symbol)
                price = ticker["price"]

                # Yeni mum kapandıysa geçmişi yenile
                now_utc = datetime.now(timezone.utc)
                if (now_utc - last_candle_ts.to_pydatetime()).total_seconds() > 86400:
                    df = exchange.get_candles(symbol, timeframe, candle_count)
                    last_candle_ts = df["timestamp"].iloc[-1]

                signal = strategy.generate_signal(df, price)
                signal = _enrich_signal(signal, df, risk)

                if last_action is not None and signal.action != last_action:
                    last_change_at = signal.timestamp
                    console.log(
                        f"[bold]Sinyal değişti:[/bold] {last_action} → "
                        f"[{_color_for_action(signal.action)}]{signal.action}[/]"
                        f"  ({signal.reason})"
                    )
                last_action = signal.action

                live.update(_render(symbol, timeframe, strategy.name, signal, last_change_at))

            except ExchangeError as exc:
                logger.warning("Borsa hatası: %s — %ss sonra tekrar denenecek", exc, poll_interval_sec)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Beklenmeyen hata: %s", exc)

            time.sleep(poll_interval_sec)
