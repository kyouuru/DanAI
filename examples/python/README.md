# DanAI Example — Python Bot

Minimal skeleton for a crypto helper bot (no API keys required by default).

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit if needed
python danai_bot.py --help
```

## What it does
- Loads config from `.env`
- Shows a simple strategy skeleton (EMA cross + ATR-based stop placeholder)
- Provides a CLI to simulate signals on CSV data (drop your OHLCV CSV as `data.csv`)

> This is **educational**. No trading/API calls by default.