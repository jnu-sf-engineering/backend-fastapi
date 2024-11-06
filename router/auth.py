from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr, Field, BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from passlib.context import CryptContext
from db.models import User

# 인증 라우터
router = APIRouter(prefix="/v1/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 회원가입 요청 검증
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=30)

# 로그인 요청 검증
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# 비밀번호 해시 함수
def get_hashed_password(password: str):
    
    # bcrypt 적용
    hashed_password = pwd_context.hash(password)

    return hashed_password

# 비밀번호 검증 함수
def verify_password(password: str, hashed_password: str):

    # bcrypt 검증
    verified_password = pwd_context.verify(password, hashed_password)

    return verified_password


# 회원가입
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):

    # 중복 이메일 체크
    existed_user = db.query(User).filter(User.EMAIL == request.email).first()
    if existed_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="해당 이메일이 이미 존재합니다."
        )
    
    # 비밀번호 해시 및 사용자 생성
    hashed_password = get_hashed_password(request.password)
    new_user = User(EMAIL=request.email, PASSWORD=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 회원가입 성공
    response = {
        "success": True,
        "response": {
            "message": "회원가입 성공"
        },
        "error": None
    }

    return response


# 로그인
@router.post("/login")
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.EMAIL == request.email).first()
    if not user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 이메일 혹은 비밀번호입니다."
        )
    
    # 비밀번호 검증
    if not verify_password(request.password, user.PASSWORD):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "유효하지 않은 이메일 혹은 비밀번호입니다."
        )
    
    # 로그인 성공: user_id 반환
    response = {
        "success": True,
        "response": {
            "user_id": user.USER_ID
        },
        "error": None
    }

    return response