from flask import Flask, request, jsonify
import os
import vonage # Asegúrate de que 'nexmo' esté en requirements.txt

app = Flask(__name__)

# --- Configuración de Credenciales de Vonage ---
# NUNCA incluyas tus claves directamente aquí en producción.
# Estas se leerán de las variables de entorno de Render.
VONAGE_API_KEY = os.getenv('VONAGE_API_KEY')
VONAGE_API_SECRET = os.getenv('VONAGE_API_SECRET')
VONAGE_BRAND_NAME = os.getenv('VONAGE_BRAND_NAME') # Tu número/ID de Vonage WhatsApp Business

# Inicializa el cliente de Vonage al inicio.
# Es buena práctica verificar si las claves se cargaron, aunque Render fallaría
# si no están presentes antes de ejecutar.
try:
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    whatsapp_client = vonage.WhatsApp(client)
    print("✅ Cliente de Vonage inicializado.")
except Exception as e:
    print(f"❌ Error al inicializar cliente de Vonage. Asegúrate de configurar las variables de entorno: {e}")
    # Considera una forma de manejar esto si la app no puede funcionar sin las claves

# --- Funciones Auxiliares para la Lógica del Bot ---
def generate_bot_response(message_text, user_name="Usuario"):
    """
    Genera una respuesta del bot basada en el texto del mensaje recibido.
    """
    lower_message = message_text.lower().strip() # Convertir a minúsculas y quitar espacios extra

    if lower_message == "hola":
        return f"¡Hola, {user_name}! Gracias por contactarnos. ¿En qué puedo ayudarte hoy?"
    elif "ayuda" in lower_message:
        return "Claro, puedo ayudarte. Intenta preguntar sobre 'horarios' o 'contacto'."
    elif "horarios" in lower_message:
        return "Nuestro horario de atención es de 9:00 AM a 5:00 PM, de lunes a viernes."
    elif "contacto" in lower_message:
        return "Puedes contactarnos al email info@example.com o llamando al +123456789."
    else:
        return f"Recibí tu mensaje: \"{message_text}\". Soy un bot en desarrollo y aún estoy aprendiendo. ¿Podrías ser más específico?"

def send_whatsapp_message(to_number, text_message):
    """
    Envía un mensaje de texto de WhatsApp usando el cliente de Vonage.
    """
    if not VONAGE_BRAND_NAME:
        print("❌ Error: VONAGE_BRAND_NAME no configurado. No se puede enviar mensaje.")
        return False

    try:
        whatsapp_client.send_message(
            to=to_number,
            from_=VONAGE_BRAND_NAME,
            message_type='text',
            text=text_message
        )
        print(f"✅ Mensaje enviado a {to_number}: \"{text_message}\"")
        return True
    except Exception as e:
        print(f"❌ Error al enviar mensaje a {to_number}: {e}")
        return False

# --- Rutas de la Aplicación Flask ---

@app.route('/')
def home():
    """
    La página de inicio de tu bot. Render la usará para comprobar su estado.
    """
    return "Bot de WhatsApp con Vonage activo y esperando webhooks.", 200

@app.route('/webhook/inbound', methods=['POST'])
def handle_inbound_message():
    """
    Endpoint para recibir mensajes entrantes de WhatsApp.
    Vonage enviará los datos del mensaje a esta URL.
    """
    try:
        data = request.json
        print("📥 Mensaje entrante recibido:", data)

        from_number = data.get('from')
        message_text = data.get('text')
        user_name = data.get('profile', {}).get('name', 'Usuario')

        if from_number and message_text:
            print(f"Procesando mensaje de {user_name} ({from_number}): \"{message_text}\"")
            response_text = generate_bot_response(message_text, user_name)
            send_whatsapp_message(from_number, response_text)
        else:
            print("⚠️ Mensaje entrante incompleto o inesperado (faltan 'from' o 'text').")

    except Exception as e:
        print(f"❌ Error al procesar mensaje entrante: {e}")
        # Considera devolver un 500 si es un error grave para que Vonage pueda reintentar
        return "Internal Server Error", 500

    return "OK", 200 # Siempre devuelve OK si el webhook se recibió correctamente

@app.route('/webhook/status', methods=['POST'])
def handle_message_status():
    """
    Endpoint para recibir actualizaciones de estado de mensajes enviados.
    """
    try:
        data = request.json
        print("📈 Actualización de estado de mensaje:", data)
    except Exception as e:
        print(f"❌ Error al procesar estado del mensaje: {e}")
        return "Internal Server Error", 500
    return "OK", 200

# --- Ejecución del Servidor Flask ---
if __name__ == '__main__':
    # Esto se ejecuta cuando el script se inicia directamente (ej. python app.py)
    # y es útil para desarrollo y pruebas locales. Render usará Gunicorn.
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando bot localmente en http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=True) # debug=True es solo para desarrollo local