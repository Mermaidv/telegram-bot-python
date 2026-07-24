import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
# Nutzt direkt den exakten Modellnamen, den wir gerade in deiner Workbench gesehen haben
MODEL_NAME = os.environ.get("MODEL_NAME", "claude-sonnet-5")

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
    
    print(f"Bot startet mit Modell: {MODEL_NAME}")
    app.run_polling(drop_pending_updates=True)
