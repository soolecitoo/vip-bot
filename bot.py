from flask import Flask, request
import requests

app = Flask(__name__)

# =========================
# CONFIGURACIÓN
# =========================

TELEGRAM_BOT_TOKEN = "8143019679:AAHCymeh8b-P8aoRtL8NOVzWocKQbqK3vO4"
TELEGRAM_CHAT_ID = "6072718946"

# =========================
# FUNCIÓN TELEGRAM
# =========================

def send_vip_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "Pago confirmado ✅ Bienvenido a VIP 🔥"
    }

    requests.post(url, data=data)

# =========================
# WEBHOOK STRIPE
# =========================

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    print("Evento recibido de Stripe")

    # AQUÍ SE ACTIVARÍA EL VIP
    send_vip_message()

    return "ok", 200

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "Bot activo"

# =========================
# RUN SERVER
# =========================

if name == "__main__":
    app.run(host="0.0.0.0", port=3000)
