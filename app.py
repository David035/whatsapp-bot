from flask import Flask, request
import vonage

app = Flask(__name__)

# 🔐 Tu clave y secreto de Vonage
VONAGE_API_KEY = "tu_api_key"
VONAGE_API_SECRET = "tu_api_secret"

client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
whatsapp = vonage.Messages(client)

@app.route('/webhook/inbound', methods=['POST'])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from")  # ejemplo: 'whatsapp:+34649586273'
    if sender:
        response = whatsapp.send_message({
            "from": "whatsapp:+14157386102",  # Número del sandbox
            "to": sender,
            "message_type": "text",
            "text": {
                "body": "Hola, soy un bot 🤖. ¿En qué puedo ayudarte?"
            }
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
