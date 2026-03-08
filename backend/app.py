import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory, Response
from flask_cors import CORS
from flask_bcrypt import Bcrypt

from backend.routes.auth import auth_bp, bcrypt
from backend.routes.quiz import quiz_bp
from backend.routes.dashboard import dashboard_bp

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR     = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
PAGES_DIR    = os.path.join(FRONTEND_DIR, "pages")

app = Flask(__name__)
CORS(app)
bcrypt.init_app(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.route("/")
def index():
    return Response(read_file(os.path.join(PAGES_DIR, "index.html")), mimetype="text/html")

@app.route("/<path:filename>")
def serve_file(filename):
    # HTML pages
    if filename.endswith(".html"):
        path = os.path.join(PAGES_DIR, filename)
        if os.path.isfile(path):
            return Response(read_file(path), mimetype="text/html")

    # CSS
    if filename.endswith(".css"):
        path = os.path.join(FRONTEND_DIR, filename)
        if os.path.isfile(path):
            return Response(read_file(path), mimetype="text/css")

    # JS
    if filename.endswith(".js"):
        path = os.path.join(FRONTEND_DIR, filename)
        if os.path.isfile(path):
            return Response(read_file(path), mimetype="application/javascript")

    return "Not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)