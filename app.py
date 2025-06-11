import os
from flask import Flask, request
import vonage

# 📍 Muestra desde dónde se carga la librería vonage
print("🔍 vonage se está cargando desde:", vonage.__file__)

# 🔐 Cargar credenciales desde variables de entorno
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_BRAND_NAME = os.environ.get("VONAGE_BRAND_NAME")  # WhatsApp Business ID

# Inicializar cliente Vonage
try:
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    messaging = vonage.Messaging(client)
    print("✅ Cliente de Vonage inicializado correctamente.")
except Exception as e:
    print(f"❌ Error al inicializar cliente de Vonage: {e}")

# Inicializar Flask
main = Flask(__name__)

# 📥 Endpoint para recibir mensajes entrantes de WhatsApp
@main.route('/webhook/inbound', methods=['POST'])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from")
    message = data.get("text")

    if sender and message and VONAGE_BRAND_NAME:
        message_lower = message.lower()
        response_text = "Hola, soy un bot 🤖. ¿En qué puedo ayudarte?"

        if "hola" in message_lower:
            response_text = "¡Hola! ¿Cómo estás? Soy tu bot de WhatsApp."
        elif "ayuda" in message_lower:
            response_text = "Puedo ayudarte con horarios, contacto, o preguntas básicas."

        try:
            messaging.send_message({
                "channel": "whatsapp",
                "to": sender,
                "from": VONAGE_BRAND_NAME,
                "message_type": "text",
                "text": {
                    "body": response_text
                }
            })
            print("📤 Respuesta enviada.")
        except Exception as e:
            print(f"❌ Error al enviar mensaje: {e}")
    else:
        print("⚠️ Faltan datos: 'from', 'text' o VONAGE_BRAND_NAME.")

    return "OK", 200

# 📈 Endpoint para recibir actualizaciones de estado de los mensajes
@main.route('/webhook/status', methods=['POST'])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

# Ruta de inicio para verificar que el bot está activo
@main.route('/')
def home():
    return "Bot de WhatsApp con Vonage activo y esperando webhooks.", 200

# Iniciar servidor Flask (usado localmente)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    main.run(host="0.0.0.0", port=port, debug=True)
