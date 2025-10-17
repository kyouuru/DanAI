# -*- coding: utf-8 -*-
import os
import asyncio
import logging
import argparse
from dataclasses import dataclass
from typing import Optional

try:
    from telegram import Update  # type: ignore
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters  # type: ignore
except Exception as e:
    raise RuntimeError(
        "Missing dependency 'python-telegram-bot'. Install with: "
        "pip install 'python-telegram-bot>=20.0'"
    ) from e
import httpx
from textwrap import dedent

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
log = logging.getLogger("danai-tg")

DANAI_BIO_SHORT = (
    "DanAI bantu trading kripto & coding: ngobrol santai, insight pasar, "
    "skrip siap pakai—jelas, aman, tanpa janji profit."
)
DISCLAIMER = "Bukan nasihat keuangan. Edukasi saja. Lakukan riset mandiri & kelola risiko."
PERSONA_PRIMER = (
    "You are DanAI: a friendly assistant focused on crypto trading (no signals), "
    "social/chat, and programming/coding. Be concise, action-first, and emphasize "
    "risk management and key security. Avoid guarantees or profit claims."
)

@dataclass
class Config:
    token: str
    openai_key: Optional[str] = None
    webhook_url: Optional[str] = None
    port: int = int(os.getenv("PORT", "8080"))

def get_config() -> Config:
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    key = os.getenv("OPENAI_API_KEY", "").strip() or None
    wh  = os.getenv("WEBHOOK_URL", "").strip() or None
    if not token:
        raise RuntimeError("Missing TELEGRAM_TOKEN in environment (.env)")
    return Config(token=token, openai_key=key, webhook_url=wh)

# ---------------- Commands ----------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = dedent(f"""
        Halo! Aku DanAI 👋

        {DANAI_BIO_SHORT}

        Perintah:
        /help — bantuan
        /bio — deskripsi singkat
        /risk — checklist risiko kripto

        {DISCLAIMER}
    """).strip()
    await update.message.reply_text(text)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Aku bisa bantu:\n"
        "• Ringkas konteks pasar & jelaskan indikator (tanpa klaim profit).\n"
        "• Tulis/debug skrip Python/Pine/CLI.\n"
        "• Brainstorm ide & siapkan langkah eksekusi.\n\n"
        "Ketik pertanyaanmu langsung, atau coba /risk."
    )
    await update.message.reply_text(msg)

async def cmd_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(DANAI_BIO_SHORT)

async def cmd_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    checklist = (
        "Risk checklist:\n"
        "1) Skenario utama & invalidasi jelas?\n"
        "2) Ukuran posisi sesuai risk %?\n"
        "3) Biaya/fee & slippage dipertimbangkan?\n"
        "4) Jangan bagikan private key.\n"
        "5) DYOR — ini edukasi, bukan sinyal.\n"
    )
    await update.message.reply_text(checklist)

# ---------------- Chat handling ----------------
async def llm_reply(prompt: str, api_key: str) -> Optional[str]:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": PERSONA_PRIMER},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 400,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log.warning("LLM request failed: %s", e)
        return None

def lite_reply(prompt: str) -> str:
    p = (prompt or "").lower()
    if any(k in p for k in ["indikator", "strategy", "pine"]):
        return ("Untuk indikator/strategy: mulai dari EMA/ATR dasar + invalidasi & trailing. "
                "Aku bisa beri contoh Pine v6. Sebut timeframe & pair.")
    if any(k in p for k in ["python", "script", "termux"]):
        return ("Untuk coding: jelaskan tujuan & environment (Windows/Termux/VPS). "
                "Aku bisa bikin template CLI dan langkah instalasi.")
    if any(k in p for k in ["sinyal", "signal"]):
        return ("Aku tidak memberi sinyal profit. Aku bantu kerangka evaluasi: "
                "level, risiko, dan skenario 'what-if'.")
    return "Oke, jelaskan targetmu. Aku susun langkah konkret + contoh kode jika perlu. " + DISCLAIMER

async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg: Config = context.application.bot_data["cfg"]
    user_text = update.message.text or ""
    if not user_text.strip():
        return
    if cfg.openai_key:
        reply = await llm_reply(user_text, cfg.openai_key)
        if reply:
            await update.message.reply_text(reply)
            return
    await update.message.reply_text(lite_reply(user_text))

# ---------------- App bootstrap ----------------
async def main_async():
    cfg = get_config()
    app = Application.builder().token(cfg.token).build()
    app.bot_data["cfg"] = cfg

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(CommandHandler("bio",   cmd_bio))
    app.add_handler(CommandHandler("risk",  cmd_risk))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    if cfg.webhook_url:
        log.info("Starting webhook at %s", cfg.webhook_url)
        await app.bot.set_webhook(url=cfg.webhook_url)
        await app.run_webhook(
            listen="0.0.0.0",
            port=cfg.port,          # <- penting: keyword argument
            url_path="",            # root path
            webhook_url=cfg.webhook_url,
        )
    else:
        log.info("Starting polling…")
        await app.run_polling(close_loop=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--webhook", action="store_true", help="Force webhook mode (requires WEBHOOK_URL)")
    args = parser.parse_args()
    if args.webhook and not os.getenv("WEBHOOK_URL"):
        raise SystemExit("WEBHOOK_URL is required for --webhook mode")
    asyncio.run(main_async())
