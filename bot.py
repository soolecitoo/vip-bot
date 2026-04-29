import os
import stripe
import requests
from flask import Flask, request

app = Flask(__name__)

# ======================
# CONFIG (Render ENV)
# ======================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ======================
# TELEGRAM FUNCTION
# ======================
def send_vip_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    text = "Pago confirmado ✅ Bienvenido VIP 🔥\nAquí tienes tu acceso:\nhttps://t.me/soolecitooVIP."

    response = requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    })

    print("TELEGRAM RESPONSE:", response.text)


# ======================
# STRIPE WEBHOOK
# ======================
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )
    except Exception as e:
        print("Webhook error:", str(e))
        return "invalid", 400

    # SOLO PAGOS REALES
    if event["type"] == "checkout.session.completed":
        print("Pago confirmado por Stripe")
        send_vip_message()

    return "ok", 200


# ======================
# TEST ROUTE
# ======================
@app.route("/")
def home():
    return "Bot activo 🚀", 200


# ======================
# START SERVER (RENDER)
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
