import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User

SECRET_KEY = "quesy-secure-secret-key-2025-2026-circular32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(32)
    iterations = 600000
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(pwd_hash).decode("utf-8")
    return f"pbkdf2:sha256:{iterations}${salt_b64}${hash_b64}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        algo_info, salt_b64, hash_b64 = parts
        _, _, iter_str = algo_info.split(":")
        iterations = int(iter_str)
        salt = base64.b64decode(salt_b64)
        expected_hash = base64.b64decode(hash_b64)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(pwd_hash, expected_hash)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": int(expire.timestamp())})
    header = {"alg": "HS256", "typ": "JWT"}
    
    def base64url_encode(data_bytes: bytes) -> str:
        return base64.urlsafe_b64encode(data_bytes).rstrip(b"=").decode("utf-8")
    
    header_encoded = base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_encoded = base64url_encode(json.dumps(to_encode, separators=(",", ":")).encode("utf-8"))
    message = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(SECRET_KEY.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    signature_encoded = base64url_encode(signature)
    return f"{message}.{signature_encoded}"

def decode_access_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_encoded, payload_encoded, signature_encoded = parts
        message = f"{header_encoded}.{payload_encoded}"
        
        def base64url_decode(input_str: str) -> bytes:
            padding = 4 - (len(input_str) % 4)
            if padding < 4:
                input_str += "=" * padding
            return base64.urlsafe_b64decode(input_str.encode("utf-8"))
        
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
        actual_sig = base64url_decode(signature_encoded)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        payload_bytes = base64url_decode(payload_encoded)
        payload = json.loads(payload_bytes.decode("utf-8"))
        if payload.get("exp", 0) < int(datetime.utcnow().timestamp()):
            return None
        return payload
    except Exception:
        return None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)) -> Optional[User]:
    if not credentials or not credentials.credentials:
        return None
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    return user

def get_current_active_user(current_user: Optional[User] = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role == "ADMIN":
            return current_user
        if current_user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Required role: {required_role}")
        return current_user
    return role_dependency
