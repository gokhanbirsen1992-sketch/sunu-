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
@click.option("--symbol", default=None, help="Sembol (örn. BTC_USDT).")
@click.option("--candles", default=1000, show_default=True, type=int, help="Çekilecek mum sayısı.")
@click.option("--fee-pct", default=0.001, show_default=True, help="Taraf başına komisyon.")
@click.option("--seed", default=None, type=int, help="Config tohumunu geçersiz kıl.")
@click.option("--export", "export_path", default=None, help="Pantheon'u JSON'a kaydet.")
@click.pass_context
def genesis(
    ctx: click.Context,
    symbol: str | None,
    candles: int,
    fee_pct: float,
    seed: int | None,
    export_path: str | None,
) -> None:
    """Çift Katmanlı Evrim: Tanrı → Evren → Robot meta-optimizasyonu.

    Eğitim verisinde robotları ve onları yetiştiren evren kurallarını
    (Tanrıları) birlikte evrimleştirir; en iyi 5 şampiyonu görülmemiş test
    verisinde HODL'a karşı sınar.
    """
    from src.genesis import GenesisConfig, run_genesis
    from src.genesis.engine import export_pantheon

    cfg = ctx.obj["config"]
    ex_cfg = cfg["exchange"]
    sym = symbol or ex_cfg["symbol"]
    tf = ex_cfg["timeframe"]

    g = cfg.get("genesis", {})
    gen_cfg = GenesisConfig(
        god_population=int(g.get("god_population", 8)),
        god_generations=int(g.get("god_generations", 4)),
        robot_population=int(g.get("robot_population", 16)),
        robot_generations=int(g.get("robot_generations", 6)),
        elite=int(g.get("elite", 2)),
        tournament=int(g.get("tournament", 3)),
        pantheon_size=int(g.get("pantheon_size", 5)),
        train_ratio=float(g.get("train_ratio", 0.7)),
        max_leverage=float(g.get("max_leverage", 5.0)),
        allow_leverage=bool(g.get("allow_leverage", True)),
        fee_pct=fee_pct,
        seed=int(seed if seed is not None else g.get("seed", 42)),
    )
    risk = RiskConfig(**cfg["risk"])

    console = Console()
    console.print(
        f"[bold]🌌 GENESIS[/bold] — Çift Katmanlı Evrim: {sym} {tf}, {candles} mum\n"
        f"[dim]{gen_cfg.god_population} Tanrı × {gen_cfg.god_generations} nesil  ·  "
        f"{gen_cfg.robot_population} robot × {gen_cfg.robot_generations} nesil[/dim]"
    )

    with Exchange() as ex:
        df = ex.get_candles(sym, tf, candles)

    with console.status("[bold green]Evrim sürüyor...", spinner="dots"):
        result = run_genesis(df, gen_cfg, risk, on_progress=lambda m: console.log(m))

    console.print(
        f"\n[bold]🧬 PANTHEON[/bold] — Arena "
        f"{result.arena_span[0].date()}→{result.arena_span[1].date()}  ·  "
        f"Doğrulama {result.val_span[0].date()}→{result.val_span[1].date()}  ·  "
        f"Test {result.test_span[0].date()}→{result.test_span[1].date()}"
    )

    table = Table(title="En İyi Tanrılar — Şampiyon Robotların Performansı")
    table.add_column("#", justify="right")
    table.add_column("Evren (fizik kuralları)")
    table.add_column("Arena %", justify="right")
    table.add_column("Doğr. %", justify="right")
    table.add_column("Test %", justify="right")
    table.add_column("İşlem", justify="right")
    table.add_column("Kazanç%", justify="right")
    table.add_column("MaxDD%", justify="right")
    for i, d in enumerate(result.pantheon, 1):
        t = d.test
        ret_color = "green" if t.return_pct > 0 else "red"
        beats = "✓" if t.return_pct > result.hodl_test_return_pct else " "
        table.add_row(
            f"{i}{beats}",
            d.god.describe(),
            f"{d.train.return_pct:+.0f}",
            f"{d.validation.return_pct:+.1f}",
            f"[{ret_color}]{t.return_pct:+.1f}[/{ret_color}]" + (" 💀" if t.ruined else ""),
            str(t.num_trades),
            f"{t.win_rate * 100:.0f}",
            f"{t.max_drawdown_pct:.1f}",
        )
    console.print(table)

    best = max(result.pantheon, key=lambda d: d.test.return_pct)
    console.print(
        f"\n[bold]Büyük Yüzleşme:[/bold] En iyi şampiyon test getirisi "
        f"[cyan]{best.test.return_pct:+.1f}%[/cyan]  vs  HODL "
        f"[magenta]{result.hodl_test_return_pct:+.1f}%[/magenta]  "
        f"→ {'[green]Evrim kazandı[/green]' if best.test.return_pct > result.hodl_test_return_pct else '[red]HODL kazandı[/red]'}"
    )
    console.print(
        "[dim]✓ = HODL'u geçti · 💀 = likidasyon. Yatırım tavsiyesi değildir.[/dim]"
    )

    if export_path:
        export_pantheon(result, export_path)
        console.print(f"[dim]Pantheon kaydedildi → {export_path}[/dim]")


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
