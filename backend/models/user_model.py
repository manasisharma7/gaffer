from utils.db import get_users_collection
from utils.password_utils import hash_password, verify_password
from bson.objectid import ObjectId
import datetime

users_col = get_users_collection()

def find_user_by_email(email: str):
    return users_col.find_one({"email": email})

def find_user_by_id(user_id: str):
    try:
        return users_col.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None

def create_user(name: str, email: str, password: str):
    if find_user_by_email(email):
        return None  # already exists

    user_doc = {
        "name": name,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.datetime.utcnow(),
    }
    result = users_col.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc

def check_user_credentials(email: str, password: str):
    user = find_user_by_email(email)
    if not user:
        return None
    if verify_password(password, user["password"]):
        return user
    return None
