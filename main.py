import pkg_resources
import vonage
import sys

print("--- Verificación de la librería 'vonage' ---")

# Intenta obtener la versión de la librería 'vonage'
try:
    vonage_version = pkg_resources.get_distribution("vonage").version
    print(f"📦 Versión de la librería 'vonage' instalada: {vonage_version}")
except pkg_resources.DistributionNotFound:
    print("❌ La librería 'vonage' no parece estar instalada en este entorno.")
    print("Asegúrate de ejecutar 'pip install vonage' o 'pip install -r requirements.txt'.")
    sys.exit(1) # Salir si no está instalada
except Exception as e:
    print(f"❌ Error al intentar obtener la versión de 'vonage': {e}")
    sys.exit(1)

# Muestra la ruta desde donde se carga la librería
try:
    print(f"🔍 'vonage' se carga desde: {vonage.__file__}")
except AttributeError:
    print("❌ No se pudo determinar la ruta de carga de 'vonage'.")

print("--- Fin de la verificación ---")