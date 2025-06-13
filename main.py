import os
from flask import Flask, request
import vonage

app = Flask(__name__)

# Variables de entorno requeridas
VONAGE_APPLICATION_ID = os.environ.get("VONAGE_APPLICATION_ID")
VONAGE_PRIVATE_KEY = os.environ.get("VONAGE_PRIVATE_KEY")  # Ruta al archivo .key
VONAGE_WHATSAPP_NUMBER = os.environ.get("VONAGE_WHATSAPP_NUMBER")

# Inicialización del cliente Vonage con JWT
client = vonage.Client(
    application_id=VONAGE_APPLICATION_ID,
    private_key=VONAGE_PRIVATE_KEY
)

@app.route("/webhook/inbound", methods=["POST"])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from")
    # Para API v1, el texto viene directamente en 'text'
    message_body = data.get("text", "")

    if sender and message_body and VONAGE_WHATSAPP_NUMBER:
        text = message_body.lower()
        if "hola" in text:
            response = "¡Hola! Soy tu bot 🤖. ¿En qué puedo ayudarte?"
        elif "ayuda" in text:
            response = "Claro, puedo ayudarte con preguntas como 'horarios', 'contacto', etc."
        else:
            response = "No entendí bien. Escribe 'ayuda' para ver opciones."

        try:
            client.messages.send_message({
                "channel": "whatsapp",
                "to": sender,
                "from": VONAGE_WHATSAPP_NUMBER,
                "message_type": "text",
                "text": response
            })
            print("📤 Mensaje enviado correctamente.")
        except Exception as e:
            print(f"❌ Error al enviar el mensaje de WhatsApp: {e}")
    else:
        print("⚠️ Faltan datos necesarios (sender, message_body o VONAGE_WHATSAPP_NUMBER). No se pudo procesar el mensaje entrante.")

    return "OK", 200

@app.route("/webhook/status", methods=["POST"])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

@app.route("/")
def home():
    return "Bot de WhatsApp con Vonage activo y esperando webhooks.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)