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

    text = "Pago confirmado ✅ Bienvenido VIP 🔥\n\nAquí tienes tu acceso:\nhttps://t.me/soolecitooVIP"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)

# =========================
# WEBHOOK STRIPE
# =========================

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print("Webhook inválido:", e)
        return "error", 400

    if event["type"] == "checkout.session.completed":
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
