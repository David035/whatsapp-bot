import os
from flask import Flask, request
import pkg_resources # Necesario para obtener la versión de la librería

# --- CAMBIO CLAVE AQUÍ ---
# Intentamos importar Client directamente del módulo vonage.
# Esto es para forzar la carga de la clase si el 'import vonage' general no la expone.
try:
    from vonage import Client, VonageError # Importa Client y VonageError directamente
    _vonage_imported_successfully = True
except ImportError as e:
    print(f"❌ Error crítico: No se pudo importar 'Client' o 'VonageError' directamente de 'vonage'. {e}")
    print("Esto indica un problema grave con la instalación o compatibilidad del módulo 'vonage'.")
    _vonage_imported_successfully = False
    # Definimos un cliente dummy para evitar NameError más abajo si la importación falla.
    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass
        def messages(self):
            return DummyMessages()
    class DummyMessages:
        def send_message(self, *args, **kwargs):
            print("❌ ATENCIÓN: El cliente Vonage no se pudo inicializar. Los mensajes no se enviarán.")
            raise Exception("Vonage Client not initialized due to import error.")
    client = DummyClient() # Asignamos un cliente dummy si la importación falla.


# -----------------------------------------------------------------------------
# Inicialización de la Aplicación Flask
# -----------------------------------------------------------------------------
main = Flask(__name__)

# 🔐 Variables de entorno
VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
VONAGE_BRAND_NAME = os.environ.get("VONAGE_BRAND_NAME")

# -----------------------------------------------------------------------------
# Verificación de la Librería Vonage (para depuración)
# -----------------------------------------------------------------------------
# Re-importamos vonage aquí solo para el vonage.__file__ y pkg_resources.
# La importación de Client ya se hizo arriba.
import vonage as _vonage_check_module # Usamos un alias para evitar conflictos
try:
    print("🔍 vonage se carga desde:", _vonage_check_module.__file__)
    vonage_version = pkg_resources.get_distribution("vonage").version
    print(f"📦 Versión de la librería 'vonage' instalada y cargada: {vonage_version}")
except Exception as e:
    print(f"❌ Error al obtener la info de la librería 'vonage' durante la depuración: {e}")

# -----------------------------------------------------------------------------
# Inicialización del Cliente Vonage
# -----------------------------------------------------------------------------
# Solo intentamos inicializar si la importación directa fue exitosa
if _vonage_imported_successfully:
    try:
        # Esto imprimirá todos los atributos disponibles en el módulo 'vonage'
        print(f"👀 Atributos disponibles en el módulo 'vonage' antes de inicializar cliente: {dir(_vonage_check_module)}")

        # Esta línea es correcta para la versión moderna del SDK de Vonage (3.x.x o superior)
        # Se inicializa el cliente con la API Key y Secret
        client = Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET) # Usamos Client importado directamente
        print("✅ Cliente de Vonage inicializado.")
    except Exception as e:
        print(f"❌ Error inicializando Vonage: {e}. "
              f"Asegúrate de que VONAGE_API_KEY y VONAGE_API_SECRET estén configuradas correctamente en tus variables de entorno.")
else:
    print("⚠️ Cliente de Vonage no se pudo inicializar debido a un error de importación previo.")

# -----------------------------------------------------------------------------
# Webhook de Mensajes Entrantes
# -----------------------------------------------------------------------------
@main.route("/webhook/inbound", methods=["POST"])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)

    sender = data.get("from")
    message_body = data.get("message", {}).get("content", {}).get("text")

    if sender and message_body and VONAGE_BRAND_NAME:
        text = message_body.lower()
        if "hola" in text:
            response = "¡Hola! Soy tu bot 🤖. ¿En qué puedo ayudarte?"
        elif "ayuda" in text:
            response = "Claro, puedo ayudarte con preguntas como 'horarios', 'contacto', etc."
        else:
            response = "No entendí bien. Escribe 'ayuda' para ver opciones."

        try:
            # Llamada para enviar el mensaje usando client.messages
            client.messages.send_message({
                "channel": "whatsapp",
                "to": sender,
                "from": VONAGE_BRAND_NAME,
                "message_type": "text",
                "text": response
            })
            print("📤 Mensaje enviado correctamente.")
        except Exception as e:
            print(f"❌ Error al enviar el mensaje de WhatsApp: {e}")
    else:
        print("⚠️ Faltan datos necesarios (sender, message_body o VONAGE_BRAND_NAME). No se pudo procesar el mensaje entrante.")

    return "OK", 200

# -----------------------------------------------------------------------------
# Webhook para el Estado de los Mensajes
# -----------------------------------------------------------------------------
@main.route("/webhook/status", methods=["POST"])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

# -----------------------------------------------------------------------------
# Ruta Principal del Servidor Web
# -----------------------------------------------------------------------------
@main.route("/")
def home():
    return "Bot de WhatsApp con Vonage activo y esperando webhooks.", 200

# -----------------------------------------------------------------------------
# Inicio de la Aplicación Flask
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    main.run(host="0.0.0.0", port=port)