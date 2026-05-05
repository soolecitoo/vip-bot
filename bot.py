print("🚨 ESTE ES BOT.PY REAL 🚨")
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
    print("🔥 WEBHOOK HIT")

    event = request.get_json()

    obj = event.get("data", {}).get("object", {})

    print("📌 EVENT TYPE:", event.get("type"))
    print("📦 OBJECT:", obj)
    print("🧾 METADATA:", obj.get("metadata"))

    telegram_id = obj.get("metadata", {}).get("telegram_id")

    print("👤 TELEGRAM ID:", telegram_id)

    if telegram_id:
        import requests

        url = f"https://api.telegram.org/botTU_BOT_TOKEN/sendMessage"

        data = {
            "chat_id": telegram_id,
            "text": "💰 Pago confirmado. Bienvenido VIP 🚀"
        }

        requests.post(url, json=data)

        print("📨 MENSAJE ENVIADO A TELEGRAM")

    return "ok", 200

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = getattr(session, "metadata", None)

        print("🔥 EVENT TYPE:", event["type"])
        print("📦 METADATA:", metadata)

        if not metadata:
            print("❌ No metadata")
            return "ok", 200

        if "telegram_id" not in metadata:
            print("❌ No telegram_id")
            return "ok", 200
        
        user_id = metadata["telegram_id"]

        if not user_id:
            print("❌ telegram_id vacío")
            return "ok", 200

        print("👤 USER ID:", user_id)
            
        
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
    data = request.get_json()
    telegram_id = data.get("telegram_id")

    if not telegram_id:
        return {"error": "missing telegram_id"}, 400
    
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

@app.route("/ping")
def ping():
    print("🔥 PING FUNCIONA")
    return "ok", 200
    
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
