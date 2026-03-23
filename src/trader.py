"""
NeuralPump Trader - Executes trades on Solana via PumpFun.

NOTE: This module handles real money. Review all configuration carefully
before enabling trade mode. USE AT YOUR OWN RISK.
"""

import aiohttp
from src.logger import get_logger
from config import config

logger = get_logger(__name__)

PUMP_TRADE_API = "https://pumpportal.fun/api/trade-local"


class Trader:
    """
    Executes buy/sell orders on PumpFun using the PumpPortal API.
    Requires a funded Solana wallet.
    """

    def __init__(self, mode: str = "dryrun"):
        self.mode = mode
        self.wallet_key = config.WALLET_PRIVATE_KEY

    async def buy(self, mint: str, symbol: str, amount_sol: float) -> tuple[bool, str]:
        """
        Buy a token on PumpFun.

        Parameters:
        - mint (str): Token mint address.
        - symbol (str): Token symbol (for logging).
        - amount_sol (float): Amount of SOL to spend.

        Returns:
        - tuple[bool, str]: (success, tx_signature or error message)
        """
        if self.mode == "dryrun":
            logger.info(f"[DRYRUN] Would buy {amount_sol} SOL of {symbol} ({mint[:8]}...)")
            return True, "dryrun_tx_simulated"

        if self.mode == "monitor":
            return False, "Trading disabled in monitor mode"

        try:
            payload = {
                "action": "buy",
                "mint": mint,
                "amount": amount_sol,
                "denominatedInSol": "true",
                "slippage": 10,
                "priorityFee": 0.0005,
                "pool": "pump"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    PUMP_TRADE_API,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-wallet-key": self.wallet_key
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tx_sig = data.get("signature", "")
                        logger.info(f"Buy executed for {symbol}: {tx_sig}")
                        return True, tx_sig
                    else:
                        error = await resp.text()
                        logger.error(f"Buy failed for {symbol}: {error}")
                        return False, error

        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False, str(e)

    async def sell(self, mint: str, symbol: str, percentage: int = 100) -> tuple[bool, str]:
        """
        Sell a token on PumpFun.

        Parameters:
        - mint (str): Token mint address.
        - symbol (str): Token symbol (for logging).
        - percentage (int): Percentage of holdings to sell (default: 100).

        Returns:
        - tuple[bool, str]: (success, tx_signature or error message)
        """
        if self.mode == "dryrun":
            logger.info(f"[DRYRUN] Would sell {percentage}% of {symbol} ({mint[:8]}...)")
            return True, "dryrun_sell_simulated"

        if self.mode == "monitor":
            return False, "Trading disabled in monitor mode"

        try:
            payload = {
                "action": "sell",
                "mint": mint,
                "amount": f"{percentage}%",
                "denominatedInSol": "false",
                "slippage": 15,
                "priorityFee": 0.0005,
                "pool": "pump"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    PUMP_TRADE_API,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-wallet-key": self.wallet_key
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tx_sig = data.get("signature", "")
                        logger.info(f"Sell executed for {symbol}: {tx_sig}")
                        return True, tx_sig
                    else:
                        error = await resp.text()
                        logger.error(f"Sell failed for {symbol}: {error}")
                        return False, error

        except Exception as e:
            logger.error(f"Sell execution error: {e}")
            return False, str(e)
