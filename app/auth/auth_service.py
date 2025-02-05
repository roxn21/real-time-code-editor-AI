import jwt
import datetime
from passlib.context import CryptContext
from decouple import config

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(user_id: int, role: str) -> str:
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    # Store user_id as an integer in the payload
    payload = {"sub": user_id, "role": role, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Ensure that 'sub' is an integer. Convert if it's a string.
        if isinstance(payload.get("sub"), str):
            try:
                payload["sub"] = int(payload["sub"])
            except ValueError:
                return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None