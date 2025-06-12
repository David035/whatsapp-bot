import os
from flask import Flask, request
import vonage
import pkg_resources # Necesario para obtener la versión de la librería

# -----------------------------------------------------------------------------
# Inicialización de la Aplicación Flask
# -----------------------------------------------------------------------------
main = Flask(__name__)

# 🔐 Variables de entorno
# Estas variables se cargan desde el entorno de Render o Google Cloud Run
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
# VONAGE_BRAND_NAME es el número de WhatsApp Business API (sin el '+')
VONAGE_BRAND_NAME = os.environ.get("VONAGE_BRAND_NAME")

# -----------------------------------------------------------------------------
# Verificación de la Librería Vonage (para depuración)
# -----------------------------------------------------------------------------
try:
    print("🔍 vonage se carga desde:", vonage.__file__)
    vonage_version = pkg_resources.get_distribution("vonage").version
    print(f"📦 Versión de la librería 'vonage' instalada y cargada: {vonage_version}")
except Exception as e:
    print(f"❌ Error al obtener la info de la librería 'vonage': {e}")

# -----------------------------------------------------------------------------
# Inicialización del Cliente Vonage
# -----------------------------------------------------------------------------
try:
    # --- LÍNEA DE DEPURACIÓN AÑADIDA ---
    # Esto imprimirá todos los atributos disponibles en el módulo 'vonage'
    print(f"👀 Atributos disponibles en el módulo 'vonage' antes de inicializar cliente: {dir(vonage)}")
    # --- FIN LÍNEA DE DEPURACIÓN ---

    # Esta línea es correcta para la versión moderna del SDK de Vonage (3.x.x o superior)
    # Se inicializa el cliente con la API Key y Secret
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    print("✅ Cliente de Vonage inicializado.")
except Exception as e:
    print(f"❌ Error inicializando Vonage: {e}. "
          f"Asegúrate de que VONAGE_API_KEY y VONAGE_API_SECRET estén configuradas correctamente en tus variables de entorno.")

# -----------------------------------------------------------------------------
# Webhook de Mensajes Entrantes
# Esta ruta recibe los mensajes de WhatsApp que Vonage envía a tu bot
# -----------------------------------------------------------------------------
@main.route("/webhook/inbound", methods=["POST"])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from") # Número del remitente del mensaje
    # Acceso robusto al texto del mensaje para webhooks de WhatsApp
    # El texto suele venir anidado en 'message' -> 'content' -> 'text'
    message_body = data.get("message", {}).get("content", {}).get("text")

    if sender and message_body and VONAGE_BRAND_NAME:
        # 🧠 Lógica básica del bot para responder a mensajes
        text = message_body.lower()
        if "hola" in text:
            response = "¡Hola! Soy tu bot 🤖. ¿En qué puedo ayudarte?"
        elif "ayuda" in text:
            response = "Claro, puedo ayudarte con preguntas como 'horarios', 'contacto', etc."
        else:
            response = "No entendí bien. Escribe 'ayuda' para ver opciones."

        try:
            # ✅ CAMBIO CLAVE: Llamada para enviar el mensaje usando client.messages
            # El mensaje se envía de vuelta al remitente a través del canal de WhatsApp
            client.messages.send_message({
                "channel": "whatsapp",
                "to": sender,
                "from": VONAGE_BRAND_NAME, # Tu número de WhatsApp Business API
                "message_type": "text",
                "text": response # El contenido de la respuesta
            })
            print("📤 Mensaje enviado correctamente.")
        except Exception as e:
            print(f"❌ Error al enviar el mensaje de WhatsApp: {e}")
            # Puedes añadir aquí una lógica para registrar este error o notificar
    else:
        print("⚠️ Faltan datos necesarios (sender, message_body o VONAGE_BRAND_NAME). No se pudo procesar el mensaje entrante.")

    return "OK", 200 # Siempre devuelve un 200 OK para que Vonage no reintente

# -----------------------------------------------------------------------------
# Webhook para el Estado de los Mensajes
# Esta ruta recibe actualizaciones sobre el estado de los mensajes enviados
# (por ejemplo, entregado, leído, fallido)
# -----------------------------------------------------------------------------
@main.route("/webhook/status", methods=["POST"])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    # Aquí puedes añadir lógica para registrar el estado de los mensajes
    return "OK", 200

# -----------------------------------------------------------------------------
# Ruta Principal del Servidor Web
# Esta ruta es para verificar que la aplicación está en ejecución al visitar la URL principal
# -----------------------------------------------------------------------------
@main.route("/")
def home():
    return "Bot de WhatsApp con Vonage activo y esperando webhooks.", 200

# -----------------------------------------------------------------------------
# Inicio de la Aplicación Flask
# Se ejecuta solo si el script se corre directamente (no cuando se importa)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Cloud Run (y Render) inyectan la variable de entorno 'PORT'
    # La aplicación debe escuchar en este puerto
    port = int(os.environ.get("PORT", 5000))
    main.run(host="0.0.0.0", port=port)