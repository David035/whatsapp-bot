from flask import Flask, request
from vonage import Client, Messaging

app = Flask(__name__)

VONAGE_API_KEY = "f9953d1d"
VONAGE_API_SECRET = "RRNs89KW6rG7qZAx"

client = Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
whatsapp = Messaging(client)

@app.route('/webhook/inbound', methods=['POST'])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from")
    if sender:
        response = whatsapp.send_message({
            "from": "whatsapp:+14157386102",
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
