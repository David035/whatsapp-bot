import os
from flask import Flask, request
import vonage

main = Flask(__name__)

# 🔐 Variables de entorno
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_BRAND_NAME = os.environ.get("VONAGE_BRAND_NAME")

# 🧠 Mostrar de dónde se carga la librería
print("🔍 vonage se carga desde:", vonage.__file__)

# 🚀 Inicializar cliente y sistema de mensajería
try:
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    messaging = vonage.Messaging(client)
    print("✅ Cliente de Vonage inicializado.")
except Exception as e:
    print(f"❌ Error inicializando Vonage: {e}")

# 📥 Webhook de mensajes entrantes
@main.route("/webhook/inbound", methods=["POST"])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from")
    message = data.get("text")

    if sender and message and VONAGE_BRAND_NAME:
        # 🧠 Lógica básica del bot
        text = message.lower()
        if "hola" in text:
            response = "¡Hola! Soy tu bot 🤖. ¿En qué puedo ayudarte?"
        elif "ayuda" in text:
            response = "Claro, puedo ayudarte con preguntas como 'horarios', 'contacto', etc."
        else:
            response = "No entendí bien. Escribe 'ayuda' para ver opciones."

        try:
            messaging.send_message({
                "channel": "whatsapp",
                "to": sender,
                "from": VONAGE_BRAND_NAME,
                "message_type": "text",
                "text": {"body": response}
            })
            print("📤 Mensaje enviado.")
        except Exception as e:
            print(f"❌ Error al enviar el mensaje: {e}")
    else:
        print("⚠️ Faltan datos: sender, text o VONAGE_BRAND_NAME.")

    return "OK", 200

# 📈 Webhook para estado de los mensajes
@main.route("/webhook/status", methods=["POST"])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

# 🌐 Ruta principal para Render
@main.route("/")
def home():
    return "Bot de WhatsApp con Vonage activo y esperando webhooks.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    main.run(host="0.0.0.0", port=port)
