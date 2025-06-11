import os
from flask import Flask, request, jsonify
import vonage

# Esto es para depuración: imprime la ruta de donde se carga el módulo 'vonage'
print("🔍 vonage se está cargando desde:", vonage.__file__)

# Crea la instancia de la aplicación Flask
main = Flask(__name__)

# --- Configuración de Credenciales de Vonage (desde Variables de Entorno) ---
# ¡IMPORTANTE!: Estas variables DEBEN estar configuradas en Render.
# NUNCA incluyas tus claves directamente en el código para producción.
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
# Tu Vonage WhatsApp Business ID (el número que Vonage te asigna, sin el '+')
VONAGE_BRAND_NAME = os.environ.get("VONAGE_BRAND_NAME")

# Inicializa el cliente de Vonage con la sintaxis de la versión 3.x.x+
try:
    client = vonage.VonageClient(
        api_key=VONAGE_API_KEY,
        api_secret=VONAGE_API_SECRET
    )
    print("✅ Cliente de Vonage inicializado correctamente con la nueva sintaxis.")
except Exception as e:
    # Si este error persiste, tu aplicación no podrá comunicarse con Vonage.
    print(f"❌ Error al inicializar cliente de Vonage: {e}. Asegúrate de que VONAGE_API_KEY y VONAGE_API_SECRET estén configurados y sean correctos.")

# --- Rutas de la Aplicación Flask ---

@main.route('/webhook/inbound', methods=['POST'])
def inbound():
    """
    Este endpoint recibe los mensajes entrantes de WhatsApp de Vonage.
    """
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender_number = data.get("from") # El número de WhatsApp del usuario
    message_text = data.get("text")   # El texto del mensaje del usuario

    # Asegúrate de que tenemos el número del remitente, el texto del mensaje y tu VONAGE_BRAND_NAME configurado
    if sender_number and message_text and VONAGE_BRAND_NAME:
        print(f"Mensaje de {sender_number}: \"{message_text}\"")

        # Lógica de respuesta básica del bot
        response_message = "Hola, soy un bot 🤖. ¿En qué puedo ayudarte?"
        if "hola" in message_text.lower():
            response_message = "¡Hola! ¿Cómo estás? Soy tu bot de WhatsApp."
        elif "ayuda" in message_text.lower():
            response_message = "Claro, puedo ayudarte con información básica. Intenta preguntar por 'horarios' o 'contacto'."

        try:
            # Envía el mensaje de respuesta de vuelta al usuario usando la API de Messages
            client.messages.send_message({
                "channel": "whatsapp",
                "to": sender_number,
                "from": VONAGE_BRAND_NAME,
                "message_type": "text",
                "text": response_message
            })
            print("📤 Respuesta enviada.")
        except Exception as e:
            # Este error indica un problema al enviar el mensaje (ej. VONAGE_BRAND_NAME incorrecto)
            print(f"❌ Error al enviar mensaje: {e}. Verifica que VONAGE_BRAND_NAME esté configurado correctamente y que el número de 'from' sea válido para tu cuenta de Vonage.")
    else:
        # Esto ocurre si el JSON entrante no tiene 'from' o 'text', o si VONAGE_BRAND_NAME no se cargó.
        print("⚠️ No se pudo procesar el mensaje: faltan datos 'from' o 'text' o VONAGE_BRAND_NAME no está configurado en el entorno.")

    return "OK", 200 # Siempre devuelve OK a Vonage para confirmar la recepción del webhook

@main.route('/webhook/status', methods=['POST'])
def status():
    """
    Este endpoint recibe actualizaciones de estado de los mensajes que envías
    (ej. entregado, leído, fallido). Útil para monitorear.
    """
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

@main.route('/')
def home():
    """
    La ruta raíz. Render la usa para comprobar que tu servicio está activo.
    """
    return "Bot de WhatsApp con Vonage activo y esperando webhooks.", 200

# --- Inicio del Servidor Flask (para desarrollo local o Gunicorn en producción) ---
if __name__ == "__main__":
    # Obtiene el puerto del entorno (Render lo proveerá) o usa 5000 por defecto
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Iniciando bot localmente en http://0.0.0.0:{port}")
    # debug=True es solo para desarrollo local, no recomendado en producción
    main.run(host="0.0.0.0", port=port, debug=True)