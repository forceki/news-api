import hashlib
import base64
from datetime import datetime, timezone, timedelta
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.env import get_env
from app.core.exception import AppError

security_scheme = HTTPBearer()


def _prepare_password(password: str) -> bytes:
    return base64.b64encode(
        hashlib.sha256(password.encode("utf-8")).digest()
    )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare_password(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_prepare_password(plain_password), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    env = get_env()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=env.JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, env.JWT_SECRET_KEY, algorithm=env.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    env = get_env()
    try:
        return jwt.decode(token, env.JWT_SECRET_KEY, algorithms=[env.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AppError(
            message="Token has expired",
            status_code=401,
            code="TOKEN_EXPIRED",
        )
    except jwt.InvalidTokenError:
        raise AppError(
            message="Invalid token",
            status_code=401,
            code="INVALID_TOKEN",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise AppError(
            message="Invalid token payload",
            status_code=401,
            code="INVALID_TOKEN",
        )
    return payload


DepCurrentUser = Annotated[dict, Depends(get_current_user)]
