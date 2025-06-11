import vonage
print("📦 vonage se carga desde:", vonage.__file__)

try:
    client = vonage.Client(key="dummy", secret="dummy")
    print("✅ vonage.Client disponible")
except AttributeError as e:
    print(f"❌ vonage.Client no está disponible: {e}")
