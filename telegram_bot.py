import telebot
import requests

# 🔑 PON AQUÍ TU TOKEN REAL DE TELEGRAM
BOT_TOKEN = "TU_TELEGRAM_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN)

# 🌐 URL DE TU BACKEND EN RENDER
BACKEND_URL = "https://TU-RENDER.onrender.com/create-checkout"


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Bienvenido.\nUsa /pay para crear tu pago VIP 💳"
    )


@bot.message_handler(commands=['pay'])
def pay(message):

    telegram_id = message.chat.id

    print("📲 Telegram ID:", telegram_id)

    response = requests.post(
        BACKEND_URL,
        json={
            "telegram_id": str(telegram_id)
        }
    )

    data = response.json()

    if "url" not in data:
        bot.send_message(message.chat.id, "❌ Error creando checkout")
        return

    bot.send_message(
        message.chat.id,
        f"💳 Paga aquí:\n{data['url']}"
    )


# ▶️ INICIAR BOT
bot.polling()
