import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GPT_MODEL: str = os.getenv("GPT_MODEL", "gpt-4o-mini")
    GPT_MAX_TOKENS: int = int(os.getenv("GPT_MAX_TOKENS", "500"))

    # Solana
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    WALLET_PRIVATE_KEY: str = os.getenv("WALLET_PRIVATE_KEY", "")

    # Trading
    BUY_AMOUNT_SOL: float = float(os.getenv("BUY_AMOUNT_SOL", "0.1"))
    MIN_SCORE_TO_BUY: int = int(os.getenv("MIN_SCORE_TO_BUY", "75"))
    TAKE_PROFIT_PCT: float = float(os.getenv("TAKE_PROFIT_PCT", "100"))
    STOP_LOSS_PCT: float = float(os.getenv("STOP_LOSS_PCT", "30"))
    MAX_POSITIONS: int = int(os.getenv("MAX_POSITIONS", "5"))

    # PumpFun
    PUMP_WS_URL: str = os.getenv("PUMP_WS_URL", "wss://pumpportal.fun/api/data")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "true").lower() == "true"

    def validate(self) -> list[str]:
        """Returns a list of missing required fields."""
        errors = []
        if not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        return errors

config = Config()
