import os
from flask import Flask, request
import vonage

app = Flask(__name__)

# 🔐 Lee las claves desde variables de entorno
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")

# ✅ Crear cliente y mensajería (válido en Vonage >= 3.0)
client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
messaging = vonage.Messaging(client)

@app.route('/webhook/inbound', methods=['POST'])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from")
    if sender:
        response = messaging.send_message({
            "from": "whatsapp:+14157386102",  # Tu número del sandbox
            "to": sender,
            "message_type": "text",
            "text": {
                "body": "Hola, soy un bot 🤖. ¿En qué puedo ayudarte?"
            },
            "channel": "whatsapp"
        })
        print("📤 Respuesta enviada:", response)

    return "OK", 200

@app.route('/webhook/status', methods=['POST'])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

@app.route('/')
def home():
    return "Bot de WhatsApp con Vonage activo", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
