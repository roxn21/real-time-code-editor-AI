from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.auth.auth_service import decode_jwt_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Extracts and verifies the JWT token.
    """
    token = credentials.credentials
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        payload["sub"] = int(payload["sub"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    return payload


def require_role(required_role: str):
    """
    Dependency function to enforce role-based access control.
    """
    def role_dependency(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    
    return role_dependency