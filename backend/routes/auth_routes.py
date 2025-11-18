from flask import Blueprint, request, jsonify
from models.user_model import create_user, check_user_credentials, find_user_by_id
from utils.jwt_utils import create_access_token, decode_token

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    user = create_user(name, email, password)
    if not user:
        return jsonify({"message": "User already exists"}), 409

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = check_user_credentials(email, password)
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(str(user["_id"]))
    return jsonify({"message": "Login successful", "token": token}), 200

@auth_bp.get("/me")
def me():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid token"}), 401

    token = auth_header.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    user = find_user_by_id(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }), 200
