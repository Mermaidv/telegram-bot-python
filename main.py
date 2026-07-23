import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Wir holen jetzt deinen neuen Anthropic-Key aus Railway:
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME") or "claude-3-5-sonnet-20241022"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Die offiziellen Anthropic-API-Header und die richtige URL:
    headers = {
        "Authorization": f"Bearer {ANTHROPIC_KEY}",
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    }
    
    data = {
        "model": MODEL_NAME,
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": user_text}]
    }

    loop = asyncio.get_running_loop()
    try:
        # Direkter Aufruf der Anthropic Messages API
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
        )
        
        res_json = response.json()
        
        if response.status_code == 200:
            # Anthropic gibt die Antwort in einer Liste von Content-Blöcken zurück
            bot_reply = res_json["content"][0]["text"]
        else:
            bot_reply = f"Fehler bei Anthropic ({response.status_code}): {res_json}"

    except Exception as e:
        bot_reply = f"Ein Fehler ist aufgetreten: {str(e)}"

    await update.message.reply_text(bot_reply)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN fehlt!")
    if not ANTHROPIC_KEY:
        raise ValueError("ANTHROPIC_API_KEY fehlt!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot läuft und lauscht auf Nachrichten...")
    app.run_polling()
