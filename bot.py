import os
import requests
import stripe
from flask import Flask, request
import json
from datetime import datetime, timedelta

VIP_FILE = "vip_users.json"

def load_vips():
    try:
        with open(VIP_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_vips(data):
    with open(VIP_FILE, "w") as f:
        json.dump(data, f)

def is_vip(user_id):
    vips = load_vips()

    if user_id not in vips:
        return False

    expires = datetime.fromisoformat(vips[user_id]["expires"])

    if datetime.utcnow() > expires:
        return False

    return True

def kick_user(telegram_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/kickChatMember"

    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "user_id": telegram_id
    })

def check_expired_users():
    vips = load_vips()

    for user_id in list(vips.keys()):
        expires = datetime.fromisoformat(vips[user_id]["expires"])

        if datetime.utcnow() > expires:
            telegram_id = vips[user_id].get("telegram_id")

            if telegram_id:
                kick_user(telegram_id)

            del vips[user_id]

    save_vips(vips)
    
app = Flask(__name__)

# ======================
# CONFIG (Render ENV)
# ======================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ======================
# TELEGRAM MESSAGE
# ======================
def send_vip_message(user_id):
    print("ENVIANDO A TELEGRAM...")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    text = "Pago confirmado ✅ Bienvenido VIP 🔥 Aquí tienes tu acceso:\nhttps://t.me/soolecitooVIP"

    response = requests.post(
        url,
        data={
            "chat_id": user_id,
            "text": text
        }
    )

    print("TELEGRAM RESPONSE:", response.text)


# ======================
# STRIPE WEBHOOK
# ======================
@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    print("🚀 WEBHOOK LLEGÓ")
    print("DATA:", request.data)
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )

        print("🔥EVENTO STRIPE:", event["type"])
              
    except Exception as e:
        print("Webhook error:", str(e))
        return "invalid", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = session.get("metadata", {})
        user_id = metadata.get("telegram_id")

        if not user_id:
            print("❌ No telegram_id en metadata")
            return "ok", 200

        if not user_id:
            print("NO HAY EMAIL")
            return "ok", 200
        
        vips = load_vips()

        # LIMPIAR VIP EXPIRADOS
        for uid in list(vips.keys()):
            expires = datetime.fromisoformat(vips[uid]["expires"])

            if datetime.utcnow() > expires:
                del vips[uid]

        # crear VIP nuevo
        vips[user_id] = {
            "expires": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

        save_vips(vips)

        send_vip_message(user_id)

    check_expired_users()

    return "ok", 200

@app.route("/create-checkout", methods=["POST"])
def create_checkout():
    data = request.json
    telegram_id = data["telegram_id"]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "VIP Access"
                },
                "unit_amount": 1000
            },
            "quantity": 1
        }],
        mode="payment",
        success_url="https://tusitio.com/success",
        cancel_url="https://tusitio.com/cancel",

        metadata={
            "telegram_id": telegram_id
        }
    )

    return {"url": session.url}


# ======================
# HOME
# ======================
@app.route("/")
def home():
    return "Bot activo 🚀", 200


# ======================
# START (RENDER)
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
