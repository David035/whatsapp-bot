import os
from flask import Flask, request, jsonify
import vonage

print("🔍 vonage se está cargando desde:", vonage.__file__)

main = Flask(__name__)

# --- Vonage Credentials (from Environment Variables) ---
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_BRAND_NAME = os.environ.get("VONAGE_BRAND_NAME")

# Inicializa el cliente de Vonage con la NUEVA SINTAXIS (v3.x.x)
try:
    # La forma correcta de inicializar el cliente en versiones recientes es vonage.VonageClient
    # Y luego usar client.messages para enviar mensajes
    client = vonage.VonageClient(
        api_key=VONAGE_API_KEY,
        api_secret=VONAGE_API_SECRET
    )
    # Ya no se necesita un 'whatsapp_client' separado si usas client.messages
    # (Aunque si quieres mantenerlo, también puedes hacerlo así:
    #  whatsapp_client = vonage.messages.WhatsApp(client))

    print("✅ Cliente de Vonage inicializado correctamente con la nueva sintaxis.")
except Exception as e:
    print(f"❌ Error al inicializar cliente de Vonage: {e}. Asegúrate de que VONAGE_API_KEY y VONAGE_API_SECRET estén configurados y de usar la sintaxis correcta para la versión de la librería.")

@main.route('/webhook/inbound', methods=['POST'])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)
    sender_number = data.get("from")
    message_text = data.get("text")

    if sender_number and message_text and VONAGE_BRAND_NAME:
        print(f"Mensaje de {sender_number}: \"{message_text}\"")

        response_message = "Hola, soy un bot 🤖. ¿En qué puedo ayudarte?"
        if "hola" in message_text.lower():
            response_message = "¡Hola! ¿Cómo estás? Soy tu bot de WhatsApp."
        elif "ayuda" in message_text.lower():
            response_message = "Claro, puedo ayudarte con información básica. Intenta preguntar por 'horarios' o 'contacto'."

        try:
            # Envía el mensaje usando client.messages
            # La estructura del payload para WhatsApp también cambia ligeramente
            client.messages.send_message({
                "channel": "whatsapp",
                "to": sender_number,
                "from": VONAGE_BRAND_NAME,
                "message_type": "text",
                "text": response_message
            })
            print("📤 Respuesta enviada.")
        except Exception as e:
            print(f"❌ Error al enviar mensaje: { {e} }. Verifica que VONAGE_BRAND_NAME esté configurado correctamente.")
    else:
        print("⚠️ No se pudo procesar el mensaje: faltan datos 'from' o 'text' o VONAGE_BRAND_NAME no está configurado.")

    return "OK", 200

@main.route('/webhook/status', methods=['POST'])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

@main.route('/')
def home():
    return "Bot de WhatsApp con Vonage activo", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando bot localmente en http://0.0.0.0:{port}")
    main.run(host="0.0.0.0", port=port, debug=True)