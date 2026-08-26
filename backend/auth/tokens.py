import os
from datetime import datetime, timedelta, timezone

import jwt

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

SECRET_KEY = os.environ.get("JWT_SECRET", "").strip()

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET is not set. Add it to backend/.env")
if len(SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET is too short — use at least 32 characters.")


class TokenError(Exception): pass
class TokenExpired(TokenError): pass
class TokenInvalid(TokenError): pass


def create_access_token(user_id: int, username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenExpired("Session expired")
    except jwt.InvalidTokenError:
        raise TokenInvalid("Invalid token")