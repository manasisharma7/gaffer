from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from pathlib import Path
import datetime, jwt, os

# ---------- ENV CONFIG ----------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
JWT_SECRET = os.getenv("JWT_SECRET", "SUPERSECRETKEY")
JWT_ALGO = "HS256"

# ---------- FLASK ----------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------- MONGO ----------
client = MongoClient(MONGO_URI)
db = client["gaffer_db"]
users = db["users"]

# ---------- AUTH HELPERS ----------
def create_token(user_id):
    payload = {
        "sub": user_id,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def verify_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload["sub"]
    except:
        return None

# ---------- AUTH ROUTES ----------
@app.post("/api/auth/register")
def register():
    data = request.json
    name = data.get("name", "")
    email = data.get("email", "").lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"message": "All fields required"}), 400

    if users.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 409

    hashed = generate_password_hash(password)
    uid = users.insert_one({"name": name, "email": email, "password": hashed}).inserted_id

    return jsonify({"message": "Signup OK", "id": str(uid)}), 201


@app.post("/api/auth/login")
def login():
    data = request.json
    email = data.get("email", "").lower()
    password = data.get("password", "")

    user = users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid login"}), 401

    token = create_token(str(user["_id"]))
    return jsonify({"token": token, "name": user["name"], "email": user["email"]})


@app.get("/api/auth/me")
def me():
    uid = verify_token(request)
    if not uid:
        return jsonify({"message": "Unauthorized"}), 401
    user = users.find_one({"_id": ObjectId(uid)})
    return jsonify({"name": user["name"], "email": user["email"]})


# ---------- ML MODELS ----------
from ml.model0_load_data import load_tracking, load_match_metadata
from ml.model1 import run_model1
from ml.model2_real import run as run_model2
from ml.model3_fixed import run_model3


@app.post("/api/analysis/tactical-shape")
def tactical_shape():
    frames = load_tracking()
    meta = load_match_metadata()
    run_model1(frames, meta, "outputs/model1")
    return jsonify({"message": "Model 1 complete", "folder": "/outputs/model1"})


@app.post("/api/analysis/player-performance")
def player_performance():
    run_model2()  # model2_real already loads data & writes to model2_output_team
    return jsonify({
        "message": "Model 2 complete",
        "output_folder": "/model2_output_team"
    })


@app.post("/api/analysis/pitch-control")
def pitch_control():
    frames = load_tracking()
    meta = load_match_metadata()
    run_model3(frames, meta, "outputs/model3")
    return jsonify({"message": "Model 3 complete", "folder": "/outputs/model3"})


# ---------- STATIC IMAGE ROUTES (IMPORTANT) ----------
@app.route("/model2_output_team/<path:filename>")
def serve_player_performance_output(filename):
    return send_from_directory("model2_output_team", filename)


@app.get("/api/analysis/player-performance/images")
def get_player_performance_graphs():
    folder = Path("model2_output_team")
    images = []
    for img in folder.rglob("*.png"):
        rel = img.relative_to(folder)
        images.append("/model2_output_team/" + str(rel).replace("\\", "/"))
    return jsonify({"images": images})


# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=False)
