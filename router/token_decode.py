import jwt
import base64
from fastapi import HTTPException, status, Header
from core.config import settings
from jwt import PyJWTError
from typing import Dict

def get_decoded_secret_key() -> str:

    return base64.urlsafe_b64decode(settings.SECRET_KEY)

def decode_access_token(token: str) -> Dict:
    try:
        secret_key = get_decoded_secret_key()
        # 토큰 디코딩
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except PyJWTError:
        # 유효하지 않은 토큰 처리
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

def get_user_id_from_token(authorization: str = Header(...)) -> int:
    # Authorization 헤더 검증
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )

    # Bearer 토큰에서 추출
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return user_id