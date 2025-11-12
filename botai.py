import os
import telebot
from dotenv import load_dotenv
from google import genai

# .env fayldan API kalitlarini yuklash
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Kalitlar mavjudligini tekshirish
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY topilmadi. .env faylga API key qo'shing.")
if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN topilmadi. .env faylga bot token qo'shing.")

# Gemini va Telegram botni ishga tushirish
client = genai.Client(api_key=API_KEY)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Matnni tozalash (uzunlikni cheklash)
def clean_text(text: str) -> str:
    return text.strip()[:8000]

# /start komandasi
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(
        message,
        "Salom! AI chatbotga xush kelibsiz.\nSavolingizni yozing, men javob beraman 😊"
    )

# Har qanday matnli xabar
@bot.message_handler(func=lambda msg: msg.text is not None)
def handle_message(message):
    user_text = clean_text(message.text)
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        # Gemini modelidan javob olish
        resp = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_text
        )

        text = getattr(resp, "text", None)
        if not text:
            text = "Javob topilmadi. Iltimos, savolni aniqroq yozing."

        # Telegram limitiga moslashtirish
        MAX_LEN = 4000
        if len(text) > MAX_LEN:
            text = text[:MAX_LEN] + "\n\n(✂️ Javob qisqartirildi.)"

        bot.reply_to(message, text)

    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")

# Botni ishga tushurish
if __name__ == "__main__":
    print("Bot ishga tushdi!")
    bot.polling(none_stop=True, interval=0, timeout=20)
