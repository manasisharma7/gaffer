import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "gaffer_db")
    JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-jwt")
    JWT_ALGO = "HS256"
    OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
