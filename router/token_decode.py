import jwt
from fastapi import HTTPException, status
from core.config import settings
from jwt import PyJWTError
from typing import Dict

def decode_access_token(token: str) -> Dict:
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except PyJWTError as e:
        # 유효하지 않은 토큰 처리
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
