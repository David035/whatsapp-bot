from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/inbound', methods=['POST'])
def inbound():
    data = request.json
    print("📥 Mensaje recibido:", data)
    # Aquí podrías procesar y responder
    return "OK", 200

@app.route('/webhook/status', methods=['POST'])
def status():
    data = request.json
    print("📈 Estado del mensaje:", data)
    return "OK", 200

@app.route('/')
def home():
    return "Bot de WhatsApp con Vonage activo", 200
