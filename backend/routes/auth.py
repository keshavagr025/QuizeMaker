from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from backend.config import Config
from backend.utils.auth_utils import create_token, token_required
import datetime

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

def get_db():
    client = MongoClient(Config.MONGO_URI)
    return client.get_database()

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not all([name, email, password]):
        return jsonify({"error": "All fields required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()
    if db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = {
        "name": name,
        "email": email,
        "password": hashed,
        "created_at": datetime.datetime.utcnow(),
        "total_quizzes": 0,
        "avg_score": 0
    }
    result = db.users.insert_one(user)
    token = create_token(result.inserted_id, name)
    return jsonify({"token": token, "name": name, "email": email}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    db = get_db()
    user = db.users.find_one({"email": email})
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_token(user["_id"], user["name"])
    return jsonify({"token": token, "name": user["name"], "email": user["email"]}), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    from bson import ObjectId
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(request.user_id)}, {"password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    user["created_at"] = user["created_at"].isoformat()
    return jsonify(user), 200
