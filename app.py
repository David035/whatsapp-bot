from flask import Flask, request, jsonify
import os # Importar para acceder a variables de entorno
import vonage # Necesitarás instalar esta librería para enviar mensajes de vuelta

app = Flask(__name__)

# Configura las credenciales de Vonage desde variables de entorno
# Es una buena práctica no poner las claves directamente en el código
VONAGE_API_KEY = os.getenv('f9953d1d')
VONAGE_API_SECRET = os.getenv('RRNs89KW6rG7qZAx')
VONAGE_BRAND_NAME = os.getenv('34649586273') # Tu número de Vonage/WhatsApp Business ID

# Inicializa el cliente de Vonage
client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
whatsapp_client = vonage.WhatsApp(client)


@app.route('/webhook/inbound', methods=['POST'])
def inbound():
    """
    Este endpoint recibe los mensajes entrantes de WhatsApp de Vonage.
    """
    data = request.json
    print("📥 Mensaje recibido:", data)

    # --- Lógica de procesamiento y respuesta ---
    # Aquí es donde puedes analizar 'data' y decidir cómo responder.
    # 'data' contendrá información como el remitente, el texto del mensaje, etc.

    # Ejemplo: Responder al mismo número que envió el mensaje
    if data and 'from' in data and 'text' in data:
        from_number = data['from']
        message_text = data['text']
        user_name = data.get('profile', {}).get('name', 'Usuario')

        print(f"Mensaje de {user_name} ({from_number}): {message_text}")

        # Ejemplo de respuesta simple: eco del mensaje
        if message_text.lower() == "hola":
            response_message = f"¡Hola, {user_name}! Has dicho: '{message_text}'. ¿En qué puedo ayudarte?"
        else:
            response_message = f"Has dicho: '{message_text}'. Estoy aprendiendo, ¿puedes ser más específico?"

        try:
            # Envía un mensaje de texto de vuelta
            # El 'to' es el número del usuario, 'from' es tu número/brand name de Vonage
            whatsapp_client.send_message(
                to=from_number,
                from_=VONAGE_BRAND_NAME,
                message_type='text',
                text=response_message
            )
            print(f"✅ Mensaje enviado a {from_number}: {response_message}")
        except Exception as e:
            print(f"❌ Error al enviar mensaje: {e}")

    return "OK", 200

@app.route('/webhook/status', methods=['POST'])
def status():
    """
    Este endpoint recibe las actualizaciones de estado de los mensajes
    enviados por Vonage (ej. entregado, leído, fallido).
    """
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

@app.route('/')
def home():
    """
    La página de inicio de tu bot.
    Render realiza comprobaciones de estado aquí.
    """
    return "Bot de WhatsApp con Vonage activo", 200

if __name__ == '__main__':
    # Para ejecutar localmente, usarás un puerto específico.
    # Render lo detectará automáticamente, pero para desarrollo local es útil.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)