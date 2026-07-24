import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import anthropic

# Konfiguration aus Railway-Variablen laden
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Das universelle, stabilste Anthropic-Modell direkt nutzen
MODEL_NAME = "claude-3-5-sonnet-latest"

# Offiziellen Anthropic Client initialisieren
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": user_text}
            ]
        )
        bot_reply = response.content[0].text
        
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
    
    print("Bot läuft mit offiziellem Anthropic-SDK und lauscht auf Nachrichten...")
    # drop_pending_updates=True löst den Telegram-Konflikt sofort
    app.run_polling(drop_pending_updates=True)
