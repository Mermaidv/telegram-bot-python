import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import anthropic
from openai import OpenAI

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME", "claude-sonnet-5")

client_anthropic = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
client_openai = OpenAI(api_key=OPENAI_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        # 1. Claude generiert die Textantwort
        response = client_anthropic.messages.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": user_text}
            ]
        )
        bot_reply = response.content[0].text
        
        # 2. OpenAI wandelt den Text in eine warme Männerstimme ("onyx") um
        speech_response = client_openai.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=bot_reply
        )
        
        audio_path = "reply.mp3"
        speech_response.stream_to_file(audio_path)
        
        # 3. Als echte Sprachnachricht an Telegram senden (funktioniert auf PC & Handy perfekt!)
        with open(audio_path, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file)
            
        # Temporäre Datei wieder löschen
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        await update.message.reply_text(f"Ein Fehler ist aufgetreten: {str(e)}")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN fehlt!")
    if not ANTHROPIC_KEY:
        raise ValueError("ANTHROPIC_API_KEY fehlt!")
    if not OPENAI_KEY:
        raise ValueError("OPENAI_API_KEY fehlt!")
        
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print(f"Bot startet mit Claude und OpenAI Sprach-Modul!")
    app.run_polling(drop_pending_updates=True)
