#!/usr/bin/env python3
"""
NeuralPump - AI-powered PumpFun token agent
Built by LixerDev
"""

import asyncio
import argparse
import sys
from config import config
from src.logger import get_logger, print_banner
from src.agent import NeuralPumpAgent

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="NeuralPump - AI agent for PumpFun token analysis and trading"
    )
    parser.add_argument(
        "--mode",
        choices=["monitor", "trade", "dryrun"],
        default="monitor",
        help=(
            "monitor: analyze tokens only, no trading | "
            "trade: full auto-trading mode | "
            "dryrun: simulate trades without real money"
        )
    )
    return parser.parse_args()


async def main():
    print_banner()
    args = parse_args()

    # Validate config
    errors = config.validate()
    if errors:
        for err in errors:
            logger.error(f"Config error: {err}")
        logger.error("Fix your .env file and try again.")
        sys.exit(1)

    if args.mode == "trade" and not config.WALLET_PRIVATE_KEY:
        logger.error("WALLET_PRIVATE_KEY is required for trade mode.")
        sys.exit(1)

    logger.info(f"Starting NeuralPump in [{args.mode.upper()}] mode")
    logger.info(f"AI Model: {config.GPT_MODEL}")
    logger.info(f"Min score to buy: {config.MIN_SCORE_TO_BUY}/100")

    agent = NeuralPumpAgent(mode=args.mode)
    await agent.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("NeuralPump stopped by user.")
