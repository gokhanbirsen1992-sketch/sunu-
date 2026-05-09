"""CLI giriş noktası."""
from __future__ import annotations

import logging
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from src.backtest import run_backtest
from src.exchange import Exchange
from src.risk import RiskConfig
from src.strategies import build_strategy

DEFAULT_CONFIG = Path(__file__).parent.parent / "config.yaml"


def _load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _build_strategy_from_config(cfg: dict, override: str | None = None):
    name = override or cfg["strategy"]["active"]
    params = cfg["strategy"].get(name, {})
    return build_strategy(name, params)


@click.group()
@click.option(
    "--config",
    "config_path",
    default=str(DEFAULT_CONFIG),
    show_default=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option("-v", "--verbose", is_flag=True, help="Debug logging.")
@click.pass_context
def cli(ctx: click.Context, config_path: Path, verbose: bool) -> None:
    """BTC/USDT Sinyal Botu — Crypto.com Exchange üzerinden takip."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    ctx.ensure_object(dict)
    ctx.obj["config"] = _load_config(config_path)


@cli.command()
@click.option("--strategy", "strategy_name", default=None, help="Config'i geçersiz kıl.")
@click.option("--symbol", default=None, help="Sembol (örn. BTC_USDT).")
@click.pass_context
def monitor(ctx: click.Context, strategy_name: str | None, symbol: str | None) -> None:
    """Canlı izleme döngüsünü başlat."""
    from src.monitor import run_monitor  # rich import maliyetini geciktir

    cfg = ctx.obj["config"]
    ex_cfg = cfg["exchange"]
    sym = symbol or ex_cfg["symbol"]
    tf = ex_cfg["timeframe"]
    poll = int(ex_cfg["poll_interval_sec"])
    count = int(ex_cfg.get("candle_count", 300))

    strategy = _build_strategy_from_config(cfg, strategy_name)
    risk = RiskConfig(**cfg["risk"])

    console = Console()
    console.print(
        f"[bold]Başlatılıyor:[/bold] {sym} {tf}, strateji=[cyan]{strategy.name}[/cyan], "
        f"polling={poll}s"
    )
    console.print(
        "[dim]UYARI: Bu bot yatırım tavsiyesi değildir, gerçek emir vermez.[/dim]\n"
    )

    with Exchange() as ex:
        try:
            run_monitor(
                exchange=ex,
                strategy=strategy,
                risk=risk,
                symbol=sym,
                timeframe=tf,
                candle_count=count,
                poll_interval_sec=poll,
                console=console,
            )
        except KeyboardInterrupt:
            console.print("\n[bold]Durduruldu.[/bold]")


@cli.command()
@click.option("--strategy", "strategy_name", default=None)
@click.option("--symbol", default=None)
@click.option("--candles", default=None, type=int, help="Kaç mum çekilecek.")
@click.option("--fee-pct", default=0.001, show_default=True, help="Taraf başına komisyon.")
@click.pass_context
def backtest(
    ctx: click.Context,
    strategy_name: str | None,
    symbol: str | None,
    candles: int | None,
    fee_pct: float,
) -> None:
    """Tarihsel veri üzerinde stratejiyi simüle et."""
    cfg = ctx.obj["config"]
    ex_cfg = cfg["exchange"]
    sym = symbol or ex_cfg["symbol"]
    tf = ex_cfg["timeframe"]
    count = candles or int(ex_cfg.get("candle_count", 300))

    strategy = _build_strategy_from_config(cfg, strategy_name)
    risk = RiskConfig(**cfg["risk"])

    console = Console()
    console.print(
        f"[bold]Backtest:[/bold] {sym} {tf}, {count} mum, strateji=[cyan]{strategy.name}[/cyan]"
    )
    with Exchange() as ex:
        df = ex.get_candles(sym, tf, count)

    console.print(
        f"Veri aralığı: {df['timestamp'].iloc[0].date()} → {df['timestamp'].iloc[-1].date()}"
    )

    result = run_backtest(df, strategy, risk, fee_pct=fee_pct)
    summary = result.summary()

    table = Table(title="Backtest Özeti", show_header=False)
    table.add_column(justify="right", style="dim")
    table.add_column()
    for k, v in summary.items():
        table.add_row(k, str(v))
    console.print(table)

    if result.trades:
        last = result.trades[-5:]
        trade_tbl = Table(title="Son işlemler")
        for col in ("Yön", "Giriş", "Çıkış", "PnL %", "Sebep"):
            trade_tbl.add_column(col)
        for t in last:
            color = "green" if t.pnl_pct > 0 else "red"
            trade_tbl.add_row(
                t.side,
                f"{t.entry_price:,.2f}",
                f"{t.exit_price:,.2f}",
                f"[{color}]{t.pnl_pct:+.2f}%[/{color}]",
                t.exit_reason,
            )
        console.print(trade_tbl)


@cli.command()
@click.pass_context
def signal(ctx: click.Context) -> None:
    """Tek seferlik anlık sinyal üret ve çık."""
    cfg = ctx.obj["config"]
    ex_cfg = cfg["exchange"]
    sym = ex_cfg["symbol"]
    tf = ex_cfg["timeframe"]
    count = int(ex_cfg.get("candle_count", 300))

    strategy = _build_strategy_from_config(cfg)
    risk = RiskConfig(**cfg["risk"])

    console = Console()
    with Exchange() as ex:
        df = ex.get_candles(sym, tf, count)
        ticker = ex.get_ticker(sym)

    sig = strategy.generate_signal(df, ticker["price"])

    from src.monitor import _enrich_signal, _render
    sig = _enrich_signal(sig, df, risk)
    console.print(_render(sym, tf, strategy.name, sig, None))


if __name__ == "__main__":
    cli(obj={})
