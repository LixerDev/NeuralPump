import asyncio
import json
import websockets
from typing import Callable, Awaitable
from src.logger import get_logger
from config import config

logger = get_logger(__name__)


class TokenEvent:
    """Represents a new token launch event from PumpFun."""

    def __init__(self, data: dict):
        self.mint = data.get("mint", "")
        self.name = data.get("name", "Unknown")
        self.symbol = data.get("symbol", "???")
        self.description = data.get("description", "")
        self.image_uri = data.get("image_uri", "")
        self.metadata_uri = data.get("metadata_uri", "")
        self.twitter = data.get("twitter", "")
        self.telegram = data.get("telegram", "")
        self.website = data.get("website", "")
        self.creator = data.get("traderPublicKey", "")
        self.initial_buy = data.get("initialBuy", 0)
        self.market_cap_sol = data.get("marketCapSol", 0)
        self.timestamp = data.get("timestamp", 0)

    def has_socials(self) -> bool:
        return bool(self.twitter or self.telegram or self.website)

    def to_dict(self) -> dict:
        return {
            "mint": self.mint,
            "name": self.name,
            "symbol": self.symbol,
            "description": self.description,
            "twitter": self.twitter,
            "telegram": self.telegram,
            "website": self.website,
            "creator": self.creator,
            "initial_buy": self.initial_buy,
            "market_cap_sol": self.market_cap_sol,
            "has_socials": self.has_socials(),
        }

    def __repr__(self):
        return f"<TokenEvent {self.symbol} ({self.mint[:8]}...)>"


class PumpMonitor:
    """
    Connects to PumpFun WebSocket and listens for new token launches.
    Calls the provided callback for each new token event.
    """

    def __init__(self, on_new_token: Callable[[TokenEvent], Awaitable[None]]):
        self.on_new_token = on_new_token
        self.ws_url = config.PUMP_WS_URL
        self._running = False

    async def run(self):
        self._running = True
        logger.info(f"Connecting to PumpFun WebSocket: {self.ws_url}")

        while self._running:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    logger.info("Connected to PumpFun. Subscribing to new token events...")

                    # Subscribe to new token creation events
                    subscribe_msg = json.dumps({"method": "subscribeNewToken"})
                    await ws.send(subscribe_msg)
                    logger.info("Subscription active. Listening for new tokens...")

                    async for message in ws:
                        try:
                            data = json.loads(message)
                            if data.get("txType") == "create":
                                event = TokenEvent(data)
                                await self.on_new_token(event)
                        except json.JSONDecodeError:
                            logger.warning("Received invalid JSON from WebSocket")
                        except Exception as e:
                            logger.error(f"Error processing token event: {e}")

            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed. Reconnecting in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"WebSocket error: {e}. Reconnecting in 10s...")
                await asyncio.sleep(10)

    def stop(self):
        self._running = False
