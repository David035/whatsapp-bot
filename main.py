import os
from flask import Flask, request, jsonify # jsonify is good practice for APIs
import vonage # Make sure 'nexmo' is in your requirements.txt

print("🔍 vonage se está cargando desde:", vonage.__file__)

main = Flask(__name__) # Renamed app to main, consistent with your code

# --- Vonage Credentials (from Environment Variables) ---
# It's crucial these are set in Render's environment variables, NOT hardcoded.
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_BRAND_NAME = os.environ.get("34649586273") # Your Vonage WhatsApp Business ID (e.g., "34612345678")

# Initialize the Vonage client
try:
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    # For WhatsApp, it's generally cleaner to use the WhatsApp-specific client
    whatsapp_client = vonage.WhatsApp(client)
    print("✅ Cliente de Vonage inicializado.")
except Exception as e:
    print(f"❌ Error al inicializar cliente de Vonage: {e}. Asegúrate de que VONAGE_API_KEY y VONAGE_API_SECRET estén configurados.")
    # Consider adding an exit here for production if credentials are mandatory

@main.route('/webhook/inbound', methods=['POST'])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)
    sender_number = data.get("from") # The user's WhatsApp number (e.g., "whatsapp:+346...")
    message_text = data.get("text") # The text content of the message

    if sender_number and message_text and VONAGE_BRAND_NAME:
        print(f"Mensaje de {sender_number}: \"{message_text}\"")

        # Basic auto-response logic
        response_message = "Hola, soy un bot 🤖. ¿En qué puedo ayudarte?"
        if "hola" in message_text.lower():
            response_message = "¡Hola! ¿Cómo estás? Soy tu bot de WhatsApp."
        elif "ayuda" in message_text.lower():
            response_message = "Claro, puedo ayudarte con información básica. Intenta preguntar por 'horarios' o 'contacto'."

        try:
            # Send the WhatsApp message using the whatsapp_client
            response = whatsapp_client.send_message(
                to=sender_number,
                from_=VONAGE_BRAND_NAME, # Use your configured Vonage WhatsApp ID here
                message_type="text",
                text=response_message
            )
            print("📤 Respuesta enviada:", response)
        except Exception as e:
            print(f"❌ Error al enviar mensaje: {e}")
    else:
        print(⚠️ No se pudo procesar el mensaje: faltan datos o VONAGE_BRAND_NAME no está configurado.")

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
    main.run(host="0.0.0.0", port=port, debug=True) # debug=True for local development
