import os
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Konfiguration aus Railway-Variablen laden
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME", "claude-3-haiku-20240307")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # URL für die offizielle Anthropic-API
    url = "https://api.anthropic.com/v1/messages"
    
    # Korrekter Header mit x-api-key und der geforderten Anthropic-Version
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": user_text}
        ]
    }
    
    try:
        # Anfrage an Anthropic senden (synchron via requests, in async eingebettet)
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_json = response.json()
        
        if response.status_code == 200:
            # Antwort aus der Anthropic-Struktur extrahieren
            bot_reply = res_json["content"][0]["text"]
        else:
            # Fehlerausgabe direkt von Anthropic lesbar machen
            error_msg = res_json.get("error", {}).get("message", str(res_json))
            bot_reply = f"Fehler von Anthropic ({response.status_code}): {error_msg}"
            
    except Exception as e:
        bot_reply = f"Ein technischer Fehler ist aufgetreten: {str(e)}"
        
    await update.message.reply_text(bot_reply)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN fehlt!")
    if not ANTHROPIC_KEY:
        raise ValueError("ANTHROPIC_API_KEY fehlt!")
        
    # Telegram Bot initialisieren
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot läuft und lauscht auf Nachrichten...")
    app.run_polling()
