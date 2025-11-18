import datetime
import jwt
from config import Config

def create_access_token(user_id: str, expires_minutes: int = 60 * 24):
    payload = {
        "sub": str(user_id),
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes),
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGO)
    # PyJWT returns string in recent versions
    return token if isinstance(token, str) else token.decode("utf-8")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGO])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
