import os
import stripe
from flask import Flask, request

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


def send_vip_message():
    import requests
    import os

    TELEGRAM_BOT_TOKEN = os.getenv("8143019679:AAHCymeh8b-P8aoRtL8NOVzWocKQbqK3vO4")
    TELEGRAM_CHAT_ID = os.getenv("6072718946")

    print("TOKEN:", TELEGRAM_BOT_TOKEN)
    print("CHAT_ID:" TELEGRAM_CHAT_ID)

    text = "Pago confirmado ✅ Bienvenido VIP 🔥\nAquí tienes tu acceso 👇\nhttps://t.me/soolecitooVIP"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    response =  requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    })

    print("RESPONSE:". response.text) 

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
        print("Webhook inválido:", e)
        return "error", 400

    # SOLO PAGOS REALES
    if event["type"] == "checkout.session.completed":
        send_vip_message()

    return "ok", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
