from flask import Flask, request, jsonify
import os
import vonage

app = Flask(__name__)

# --- Configuración de Credenciales de Vonage (¡IMPORTANTE!) ---
# Estas variables se cargarán desde el entorno de Render.
# NUNCA hardcodes tus claves directamente en el código de producción.
VONAGE_API_KEY = os.getenv('VONAGE_API_KEY')
VONAGE_API_SECRET = os.getenv('VONAGE_API_SECRET')
VONAGE_BRAND_NAME = os.getenv('VONAGE_BRAND_NAME') # Tu número de Vonage/WhatsApp Business ID

# Inicializa el cliente de Vonage
# Si alguna clave no está configurada, esto podría fallar.
# Asegúrate de configurar las variables de entorno en Render.
try:
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    whatsapp_client = vonage.WhatsApp(client)
    print("✅ Cliente de Vonage inicializado correctamente.")
except Exception as e:
    print(f"❌ Error al inicializar cliente de Vonage: {e}")
    # En un entorno de producción real, podrías querer que la app no inicie aquí
    # o registrar un error crítico.

@app.route('/webhook/inbound', methods=['POST'])
def inbound():
    """
    Este endpoint recibe los mensajes entrantes de WhatsApp de Vonage.
    """
    data = request.json
    print("📥 Mensaje recibido:", data)

    # --- Lógica de procesamiento y respuesta ---
    # Aquí puedes analizar el contenido de 'data' y decidir cómo responder.
    # 'data' contendrá el 'from' (remitente), 'text' (contenido del mensaje), etc.

    # Aseguramos que tenemos los datos esperados antes de procesar
    if data and 'from' in data and 'text' in data:
        from_number = data['from']
        message_text = data['text']
        # Intenta obtener el nombre del perfil, si no existe, usa 'Usuario'
        user_name = data.get('profile', {}).get('name', 'Usuario')

        print(f"Mensaje de {user_name} ({from_number}): \"{message_text}\"")

        # Ejemplo de lógica de respuesta:
        response_message = ""
        lower_message = message_text.lower()

        if lower_message == "hola":
            response_message = f"¡Hola, {user_name}! Gracias por saludarme. ¿En qué puedo ayudarte hoy?"
        elif "ayuda" in lower_message:
            response_message = "Claro, puedo ayudarte. Intenta preguntar sobre 'horarios' o 'contacto'."
        elif "horarios" in lower_message:
            response_message = "Nuestro horario es de 9:00 AM a 5:00 PM, de lunes a viernes."
        elif "contacto" in lower_message:
            response_message = "Puedes contactarnos al email info@example.com o llamando al +123456789."
        else:
            response_message = f"Recibí tu mensaje: \"{message_text}\". Soy un bot sencillo y sigo aprendiendo. ¿Podrías ser más específico?"

        # Envía el mensaje de respuesta de vuelta al usuario
        if response_message: # Asegúrate de que hay un mensaje para enviar
            try:
                whatsapp_client.send_message(
                    to=from_number,             # El número del usuario que envió el mensaje
                    from_=VONAGE_BRAND_NAME,    # Tu número/ID de Vonage para WhatsApp Business
                    message_type='text',        # Tipo de mensaje (en este caso, texto)
                    text=response_message       # El contenido del mensaje a enviar
                )
                print(f"✅ Mensaje de respuesta enviado a {from_number}: \"{response_message}\"")
            except Exception as e:
                print(f"❌ Error al enviar mensaje a {from_number}: {e}")
    else:
        print("⚠️ Mensaje entrante sin datos 'from' o 'text' esperados.")

    # Siempre devuelve un "OK" a Vonage para confirmar que el webhook se recibió.
    return "OK", 200

@app.route('/webhook/status', methods=['POST'])
def status():
    """
    Este endpoint recibe las actualizaciones de estado de los mensajes
    enviados por Vonage (ej. entregado, leído, fallido).
    Útil para depuración y monitoreo de la entrega de tus mensajes.
    """
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

@app.route('/')
def home():
    """
    La página de inicio de tu bot.
    Render la usará para comprobar que tu servicio está activo.
    """
    return "Bot de WhatsApp con Vonage activo", 200

if __name__ == '__main__':
    # Esto solo se ejecuta cuando corres el script directamente (ej. python app.py)
    # y es útil para pruebas locales. Render usará Gunicorn para ejecutarlo.
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Iniciando el bot localmente en http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)