import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from src.logger import get_logger
from src.pump_monitor import PumpMonitor, TokenEvent
from src.ai_analyzer import AIAnalyzer
from src.trader import Trader
from src.database import init_db, save_token, save_trade, get_stats
from config import config

logger = get_logger(__name__)
console = Console()

VERDICT_COLORS = {
    "STRONG_BUY": "bold green",
    "BUY": "green",
    "WATCH": "yellow",
    "SKIP": "dim",
    "AVOID": "bold red",
}

VERDICT_EMOJIS = {
    "STRONG_BUY": "🟢🟢",
    "BUY": "🟢",
    "WATCH": "🟡",
    "SKIP": "🔴",
    "AVOID": "💀",
}


class NeuralPumpAgent:
    """
    Main NeuralPump agent that orchestrates monitoring, analysis, and trading.
    """

    def __init__(self, mode: str = "monitor"):
        self.mode = mode
        self.analyzer = AIAnalyzer()
        self.trader = Trader(mode=mode)
        self.tokens_analyzed = 0
        self.tokens_bought = 0

    def _display_analysis(self, event: TokenEvent, analysis: dict):
        """Pretty-print the AI analysis result to the console."""
        score = analysis.get("total_score", 0)
        verdict = analysis.get("verdict", "SKIP")
        color = VERDICT_COLORS.get(verdict, "white")
        emoji = VERDICT_EMOJIS.get(verdict, "")

        table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1))
        table.add_column("Key", style="dim", width=18)
        table.add_column("Value")

        table.add_row("Token", f"[bold]{event.name}[/bold] ({event.symbol})")
        table.add_row("Mint", f"[dim]{event.mint[:16]}...[/dim]")
        table.add_row("Socials", "✅ Yes" if event.has_socials() else "❌ None")
        table.add_row("Creator", f"[dim]{event.creator[:12]}...[/dim]")
        table.add_row("AI Score", f"[{color}]{score}/100[/{color}]")
        table.add_row("Verdict", f"[{color}]{emoji} {verdict}[/{color}]")
        table.add_row("Reasoning", analysis.get("reasoning", "N/A"))

        positives = analysis.get("positives", [])
        red_flags = analysis.get("red_flags", [])

        if positives:
            table.add_row("Positives", "\n".join(f"+ {p}" for p in positives[:3]))
        if red_flags:
            table.add_row("Red Flags", "\n".join(f"⚠ {f}" for f in red_flags[:3]))

        panel = Panel(
            table,
            title=f"[bold]{emoji} NeuralPump Analysis #{self.tokens_analyzed}[/bold]",
            border_style=color
        )
        console.print(panel)

    async def _handle_token(self, event: TokenEvent):
        """Process a new token event: analyze, decide, and optionally trade."""
        self.tokens_analyzed += 1
        logger.info(f"New token detected: {event.name} ({event.symbol}) | #{self.tokens_analyzed}")

        # Run AI analysis
        analysis = await self.analyzer.analyze(event.to_dict())
        if not analysis:
            logger.warning(f"Could not analyze {event.name}, skipping.")
            return

        # Display result
        self._display_analysis(event, analysis)

        # Save to database
        await save_token(event.mint, event.to_dict(), analysis)

        # Decide to buy
        score = analysis.get("total_score", 0)
        verdict = analysis.get("verdict", "SKIP")

        if score >= config.MIN_SCORE_TO_BUY and verdict in ("STRONG_BUY", "BUY"):
            logger.info(
                f"Score {score}/100 meets threshold ({config.MIN_SCORE_TO_BUY}). "
                f"Initiating buy for {event.symbol}..."
            )
            success, tx_or_err = await self.trader.buy(
                event.mint, event.symbol, config.BUY_AMOUNT_SOL
            )
            if success:
                self.tokens_bought += 1
                await save_trade(
                    mint=event.mint,
                    symbol=event.symbol,
                    action="buy",
                    amount_sol=config.BUY_AMOUNT_SOL,
                    ai_score=score,
                    mode=self.mode,
                    tx_sig=tx_or_err,
                    entry_mc=event.market_cap_sol
                )
                console.print(f"[bold green]Trade executed! Tx: {tx_or_err[:20]}...[/bold green]")
            else:
                logger.error(f"Trade failed: {tx_or_err}")
        else:
            logger.debug(f"Score {score}/100 below threshold. No trade.")

    async def _print_stats_loop(self):
        """Print agent stats every 5 minutes."""
        while True:
            await asyncio.sleep(300)
            stats = await get_stats()
            console.print(
                f"\n[dim]📊 Stats | Analyzed: {stats['total_tokens_analyzed']} | "
                f"Bought: {stats['total_buys']} | Avg Score: {stats['avg_ai_score']}/100[/dim]\n"
            )

    async def run(self):
        """Start the NeuralPump agent."""
        await init_db()

        monitor = PumpMonitor(on_new_token=self._handle_token)

        logger.info("NeuralPump agent started. Press Ctrl+C to stop.")

        await asyncio.gather(
            monitor.run(),
            self._print_stats_loop()
        )
