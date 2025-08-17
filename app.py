import os
from flask import Flask

app = Flask(__name__)

@app.get("/")
def index():
    return "Hello from Flask demo"

@app.get("/health")
def health():
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    # host=0.0.0.0 pour être atteignable depuis le conteneur ZAP
    app.run(host="0.0.0.0", port=port)
