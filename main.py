import os
from flask import Flask

main = Flask(__name__)

@main.route("/")
def index():
    return "✅ main.py funciona correctamente", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    main.run(host="0.0.0.0", port=port)
