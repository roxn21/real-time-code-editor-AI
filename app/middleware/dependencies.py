from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.auth.auth_service import decode_jwt_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Extracts and verifies the JWT token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    token = credentials.credentials
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Ensure user ID is an integer
    try:
        payload["sub"] = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    return payload

def require_role(required_roles: list[str]):
    """Dependency function to enforce role-based access control."""
    def role_dependency(user: dict = Depends(get_current_user)):
        if user.get("role") not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_dependency