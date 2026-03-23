import logging
import os
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text
from config import config

console = Console()


def get_logger(name: str) -> logging.Logger:
    handlers = [RichHandler(console=console, rich_tracebacks=True, show_path=False)]

    if config.LOG_TO_FILE:
        os.makedirs("logs", exist_ok=True)
        log_file = f"logs/neuralpump_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        ))
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        handlers=handlers,
        format="%(message)s",
        datefmt="[%H:%M:%S]",
    )
    return logging.getLogger(name)


def print_banner():
    banner = """
[bold purple]
 ███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ██╗     ██████╗ ██╗   ██╗███╗   ███╗██████╗ 
 ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗██║     ██╔══██╗██║   ██║████╗ ████║██╔══██╗
 ██╔██╗ ██║█████╗  ██║   ██║██████╔╝███████║██║     ██████╔╝██║   ██║██╔████╔██║██████╔╝
 ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██╔══██║██║     ██╔═══╝ ██║   ██║██║╚██╔╝██║██╔═══╝ 
 ██║ ╚████║███████╗╚██████╔╝██║  ██║██║  ██║███████╗██║     ╚██████╔╝██║ ╚═╝ ██║██║     
 ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝     ╚═╝╚═╝     
[/bold purple]
[bold cyan]         AI-Powered PumpFun Token Agent | Built by LixerDev[/bold cyan]
[dim]         v1.0.0 | Solana Mainnet[/dim]
    """
    console.print(banner)
