import os
from flask import Flask, request
import vonage
import pkg_resources # Add this import!

main = Flask(__name__)

# ... (your existing code)

# 🧠 Mostrar de dónde se carga la librería
print("🔍 vonage se carga desde:", vonage.__file__)

try:
    vonage_version = pkg_resources.get_distribution("vonage").version
    print(f"📦 Versión de la librería 'vonage' instalada y cargada: {vonage_version}")
except Exception as e:
    print(f"❌ No se pudo obtener la versión de 'vonage' en tiempo de ejecución: {e}")

# 🚀 Inicializar cliente y sistema de mensajería
try:
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    # ... (rest of your Vonage initialization and logic)