# DanAI — Telegram Bot Starter

A minimal Telegram bot for DanAI with two modes:
1) **LLM mode** (optional): uses OpenAI API if `OPENAI_API_KEY` is set.
2) **Lite mode**: fast rule-based replies with DanAI persona (no external API).

> **Disclaimer**: Educational only. Not financial advice.

## 1) Create Bot & Get Token
1. Open Telegram, chat with **@BotFather**
2. `/newbot` → set name `DanAI` and username like `DanAI_HelperBot`
3. Copy the token → set it in `.env` (`TELEGRAM_TOKEN=`)

## 2) Run Locally (polling)
```bash
cd examples/telegram
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # put your TELEGRAM_TOKEN, optional OPENAI_API_KEY
python bot.py
```
The bot will run with long polling. Press CTRL+C to stop.

## 3) Webhook (optional, for cloud)
- Set `WEBHOOK_URL` in `.env` (e.g., from your hosting).
- Then run: `python bot.py --webhook`
- Expose port 8080 and ensure public HTTPS endpoint.

## 4) Commands
- `/start` — greet + brief intro
- `/help` — what DanAI can do
- `/bio` — short bio
- `/risk` — risk checklist for crypto
- Free chat — Q&A (LLM mode if available, else lite mode)

## 5) Username/URL for Recall
Paste your bot link in **Telegram (optional)** field:
```
https://t.me/<YourBotUsername>
```
Example: `https://t.me/DanAI_HelperBot`

---
Made for Imam Qolandani (Dani).