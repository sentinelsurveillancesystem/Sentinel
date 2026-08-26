from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.tokens import TokenExpired, TokenInvalid, verify_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(401, "Not authenticated",
                            headers={"WWW-Authenticate": "Bearer"})
    try:
        return verify_access_token(credentials.credentials)
    except TokenExpired:
        raise HTTPException(401, "Session expired",
                            headers={"WWW-Authenticate": "Bearer"})
    except TokenInvalid:
        raise HTTPException(401, "Invalid token",
                            headers={"WWW-Authenticate": "Bearer"})


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")
    return user