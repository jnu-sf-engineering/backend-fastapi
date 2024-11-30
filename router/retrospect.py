from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Union, Optional
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Retrospect, KPT, CSS, FourLs, Sprint, Project
from router.token_decode import get_user_id_from_token
from openai_service import field_advice

# 회고록 라우터
router = APIRouter(prefix="/v1/retrospects", tags=["회고록"])

# KPT 요청 데이터 모델
class KPTAnswer(BaseModel):
    keep: Optional[str] = None
    problem: Optional[str] = None
    try_: Optional[str] = Field(None, alias="try")

# CSS 요청 데이터 모델
class CSSAnswer(BaseModel):
    continue_: Optional[str] = Field(None, alias="continue")
    stop: Optional[str] = None
    start: Optional[str] = None

# 4LS 요청 데이터 모델
class FourLSAnswer(BaseModel):
    liked: Optional[str] = None
    learned: Optional[str] = None
    lacked: Optional[str] = None
    loggedFor: Optional[str] = Field(None, alias="loggedFor")

# 공통 요청 모델
class RetroRequest(BaseModel):
    retroId: int
    tempName: str
    answer: Union[KPTAnswer, CSSAnswer, FourLSAnswer]


# 조언 요청 모델
class AdviceRequest(BaseModel):
    tempName: str
    fieldName: str
    fieldValue: Optional[str] = None  


# Retrospect 소유권 확인 로직
def validate_retro_ownership(user_id: int, retro_id: int, db: Session):
    retrospect = (
        db.query(Retrospect)
        .join(Sprint, Retrospect.SPRINT_ID == Sprint.SPRINT_ID)
        .join(Project, Sprint.PROJECT_ID == Project.PROJECT_ID)
        .filter(Project.USER_ID == user_id, Retrospect.RETRO_ID == retro_id)
        .first()
    )
    if not retrospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retrospect not found or access denied"
        )
    return retrospect


@router.put("/", response_model=dict)
async def update_retrospect(
    request: RetroRequest,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    # Retrospect 확인
    retrospect = db.query(Retrospect).filter_by(RETRO_ID=request.retroId).first()
    if not retrospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retrospect not found"
        )

    # Retrospect 소유권 확인
    retrospect = validate_retro_ownership(user_id, request.retroId, db)

    # 템플릿별 처리
    if request.tempName == "KPT":
        kpt = db.query(KPT).filter_by(RETRO_ID=request.retroId).first()
        if not kpt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPT data not found"
            )
        kpt.KEEP = request.answer.keep
        kpt.PROBLEM = request.answer.problem
        kpt.TRY = request.answer.try_
        db.commit()
        db.refresh(kpt)

    elif request.tempName == "CSS":
        css = db.query(CSS).filter_by(RETRO_ID=request.retroId).first()
        if not css:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CSS data not found"
            )
        css.CSS_CONTINUE = request.answer.continue_
        css.CSS_STOP = request.answer.stop
        css.CSS_START = request.answer.start
        db.commit()
        db.refresh(css)

    elif request.tempName == "FOUR_LS":
        four_ls = db.query(FourLs).filter_by(RETRO_ID=request.retroId).first()
        if not four_ls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FourLs data not found"
            )
        four_ls.LIKED = request.answer.liked
        four_ls.LEARNED = request.answer.learned
        four_ls.LACKED = request.answer.lacked
        four_ls.LOGGED_FOR = request.answer.loggedFor
        db.commit()
        db.refresh(four_ls)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template name"
        )

    response = {
        "success": True,
        "response": {
            "retroId": retrospect.RETRO_ID
            }, 
        "error": None
    }

    return response


@router.post("/advice", response_model=dict)
async def get_advice(request: AdviceRequest):
    # 템플릿 유효성 검증
    valid_templates = {
        "KPT": ["keep", "problem", "try"],
        "CSS": ["continue", "stop", "start"],
        "FOUR_LS": ["liked", "learned", "lacked", "loggedFor"]
    }
    if request.tempName not in valid_templates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template name"
        )

    if request.fieldName not in valid_templates[request.tempName]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field name for {request.tempName} template"
        )
    
    # fieldValue 유효성 검증
    if not request.fieldValue or request.fieldValue.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fieldValue cannot be empty"
        )

    # ChatGPT 조언
    advice = field_advice(request.tempName, request.fieldName, request.fieldValue)
    if not advice:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate advcie from OpenAI"
        )

    response = {
        "success": True,
        "response": {
            "advice": advice
            }, 
        "error": None
    }
    
    return response
