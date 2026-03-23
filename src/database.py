import aiosqlite
import json
from datetime import datetime
from src.logger import get_logger

logger = get_logger(__name__)

DB_PATH = "neuralpump.db"


async def init_db():
    """Initialize the SQLite database and create tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mint TEXT UNIQUE NOT NULL,
                name TEXT,
                symbol TEXT,
                description TEXT,
                creator TEXT,
                has_socials INTEGER DEFAULT 0,
                ai_score INTEGER,
                ai_verdict TEXT,
                ai_reasoning TEXT,
                red_flags TEXT,
                positives TEXT,
                analyzed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mint TEXT NOT NULL,
                symbol TEXT,
                action TEXT NOT NULL,
                amount_sol REAL,
                price_sol REAL,
                ai_score INTEGER,
                mode TEXT,
                status TEXT DEFAULT 'open',
                entry_market_cap REAL,
                exit_market_cap REAL,
                pnl_sol REAL,
                tx_signature TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                closed_at TEXT
            )
        """)
        await db.commit()
    logger.info("Database initialized.")


async def save_token(mint: str, token_data: dict, analysis: dict):
    """Save a token and its AI analysis to the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("""
                INSERT OR IGNORE INTO tokens 
                (mint, name, symbol, description, creator, has_socials,
                 ai_score, ai_verdict, ai_reasoning, red_flags, positives, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mint,
                token_data.get("name"),
                token_data.get("symbol"),
                token_data.get("description", "")[:500],
                token_data.get("creator"),
                1 if token_data.get("has_socials") else 0,
                analysis.get("total_score"),
                analysis.get("verdict"),
                analysis.get("reasoning"),
                json.dumps(analysis.get("red_flags", [])),
                json.dumps(analysis.get("positives", [])),
                datetime.utcnow().isoformat()
            ))
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to save token {mint}: {e}")


async def save_trade(mint: str, symbol: str, action: str, amount_sol: float,
                     ai_score: int, mode: str, tx_sig: str = "", entry_mc: float = 0):
    """Record a trade in the database."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO trades (mint, symbol, action, amount_sol, ai_score, mode, tx_signature, entry_market_cap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (mint, symbol, action, amount_sol, ai_score, mode, tx_sig, entry_mc))
        await db.commit()


async def get_stats() -> dict:
    """Get overall agent statistics."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM tokens") as cursor:
            total_tokens = (await cursor.fetchone())[0]

        async with db.execute("SELECT COUNT(*) FROM trades WHERE action='buy'") as cursor:
            total_buys = (await cursor.fetchone())[0]

        async with db.execute("SELECT AVG(ai_score) FROM tokens WHERE ai_score IS NOT NULL") as cursor:
            avg_score = (await cursor.fetchone())[0] or 0

        return {
            "total_tokens_analyzed": total_tokens,
            "total_buys": total_buys,
            "avg_ai_score": round(avg_score, 1),
        }
