# 🧠 NeuralPump

An AI-powered agent that monitors [PumpFun](https://pump.fun) token launches in real-time, analyzes them using GPT, scores them automatically, and optionally executes trades on Solana.

**Built by LixerDev**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-purple)
![Solana](https://img.shields.io/badge/network-Solana-9945FF)

---

## 🚀 What is NeuralPump?

NeuralPump connects to PumpFun's real-time WebSocket feed, captures every new token launch, and runs it through an AI analysis pipeline:

1. **Monitor** — Listens to PumpFun WebSocket for new token events
2. **Analyze** — Sends token metadata to GPT for deep analysis
3. **Score** — Rates the token from 0–100 based on multiple signals
4. **Act** — Optionally buys high-scoring tokens automatically
5. **Manage** — Tracks positions and sells based on profit/loss targets

---

## 📋 Table of Contents
- [Features](#-features)
- [Setup](#️-setup)
- [Configuration](#-configuration)
- [How It Works](#-how-it-works)
- [Scoring System](#-scoring-system)
- [Risk Warning](#️-risk-warning)
- [License](#-license)

---

## ✨ Features

- 🔴 **Real-time monitoring** via PumpFun WebSocket API
- 🤖 **GPT-powered analysis** of token name, symbol, description & social signals
- 📊 **0-100 scoring system** with configurable buy threshold
- 💸 **Auto-trading** on Solana (optional, requires wallet)
- 🎯 **Take-profit / Stop-loss** management
- 📝 **Detailed logging** with color-coded terminal output
- 💾 **SQLite persistence** for token history and trades
- ⚙️ **Fully configurable** via `.env` file

---

## 🛠️ Setup

### 1. Clone the repository
```bash
git clone https://github.com/LixerDev/NeuralPump.git
cd NeuralPump
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run the agent
```bash
# Monitor-only mode (no trading)
python main.py --mode monitor

# Full auto-trading mode
python main.py --mode trade

# Dry run (simulate trades, no real money)
python main.py --mode dryrun
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in:

| Variable | Description | Required |
|---|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ |
| `SOLANA_RPC_URL` | Solana RPC endpoint | For trading |
| `WALLET_PRIVATE_KEY` | Your Solana wallet private key | For trading |
| `BUY_AMOUNT_SOL` | Amount of SOL per trade (default: 0.1) | For trading |
| `MIN_SCORE_TO_BUY` | Minimum AI score to trigger buy (default: 75) | No |
| `TAKE_PROFIT_PCT` | Take profit percentage (default: 100) | No |
| `STOP_LOSS_PCT` | Stop loss percentage (default: 30) | No |
| `GPT_MODEL` | OpenAI model to use (default: gpt-4o-mini) | No |

---

## 🧠 How It Works

### Token Analysis Pipeline

When a new token is detected on PumpFun, NeuralPump runs it through this pipeline:

```
PumpFun WebSocket
       ↓
   Token Event
       ↓
  AI Analyzer (GPT)
       ↓
  Score Calculator
       ↓
  [score >= threshold?]
       ↓ YES
  Trade Executor
       ↓
  Position Manager
```

### AI Prompt

The agent sends the following context to GPT for each token:
- Token name and symbol
- Token description (if available)
- Creator wallet address
- Launch timestamp
- Initial market cap and liquidity

GPT evaluates the token and returns a structured JSON with scores per category.

---

## 📊 Scoring System

Tokens are scored from **0 to 100** across multiple dimensions:

| Category | Weight | Description |
|---|---|---|
| Name Quality | 20% | Originality, memorability, meme potential |
| Narrative | 25% | Story strength, relevance to current trends |
| Red Flags | 25% | Suspicious patterns, copy-paste descriptions |
| Community Potential | 20% | Viral potential, community appeal |
| Timing | 10% | Market conditions, launch timing |

**Score interpretation:**
- 🟢 **75-100**: Strong buy signal
- 🟡 **50-74**: Watchlist — monitor closely
- 🔴 **0-49**: Skip — low potential or red flags

---

## ⚠️ Risk Warning

> **NeuralPump is for educational and research purposes only.**
>
> Meme coin trading is extremely high risk. Most tokens launched on PumpFun go to zero. Never invest more than you are willing to lose completely. The AI scoring system is not financial advice. Past performance does not guarantee future results.
>
> **USE AT YOUR OWN RISK.**

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
