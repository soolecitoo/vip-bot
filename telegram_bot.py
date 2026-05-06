import telebot
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

BACKEND_URL = "https://vip-bot-1q8u.onrender.com/create-checkout"


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Bienvenido.\nUsa /pay para crear tu pago VIP 💳"
    )

@bot.message_handler(commands=['pay'])
def pay(message):

    telegram_id = message.chat.id
    print("Telegram ID:", telegram_id)

    response = requests.post(
        BACKEND_URL,
        json={
            "telegram_id": str(telegram_id)
        }
    )

    if response.status_code != 200:
        bot.send_message(message.chat.id, "❌ Error en servidor")
        return

    data = response.json()

    if "url" not in data:
        bot.send_message(message.chat.id, "❌ No se pudo crear el pago")
        return

    bot.send_message(
        message.chat.id,
        f"💳 Paga aquí:\n{data['url']}"
    )


# ▶️ INICIAR BOT
bot.infinity_polling(skip_pending=True)
