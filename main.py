import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
# Liest das Modell direkt aus Railway aus, Standard ist Haiku
MODEL_NAME = os.environ.get("MODEL_NAME", "claude-3-haiku-20240307")

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

async def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN fehlt!")
    if not ANTHROPIC_KEY:
        raise ValueError("ANTHROPIC_API_KEY fehlt!")
        
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Killt jegliche alten Telegram-Verbindungen sofort
    await app.bot.delete_webhook(drop_pending_updates=True)
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print(f"Bot startet mit Modell: {MODEL_NAME}")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
