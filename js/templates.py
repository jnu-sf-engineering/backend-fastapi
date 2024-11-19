from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import get_db
from db.models import Retrospect, Sprint, KPT, FourLs, CSS
from error.exceptions import TemplateMissingFieldData, TemplateSprintNotFound, TemplateNotFound

# 템플릿 라우터
router = APIRouter(prefix="/v1/template", tags=["템플릿"])


# 템플릿 생성 요청 검증
class TemplateRequest(BaseModel):
    sprint_id: int
    temp_name: str


# 템플릿 생성 응답 모델
class TemplateResponse(BaseModel):
    success: bool
    response: dict
    error: dict = None


# 템플릿 생성
@router.post("/", response_model=TemplateResponse)
async def create_template(request: TemplateRequest, db: Session = Depends(get_db)):
    # 필드 누락 검증
    if not request.sprint_id or not request.temp_name:
        raise TemplateMissingFieldData(['sprint_id', 'temp_name'])

    # 스프린트 존재 확인
    sprint = db.query(Sprint).filter(Sprint.SPRINT_ID == request.sprint_id).first()
    if not sprint:
        raise TemplateSprintNotFound()

    # 템플릿 이름 검증 및 Retrospect 생성
    retrospect = Retrospect(SPRINT_ID=request.sprint_id, SUMMARY=request.temp_name)
    db.add(retrospect)
    db.commit()  # Retrospect 객체가 데이터베이스에 저장되어 RETRO_ID가 생성됨
    db.refresh(retrospect)

    # 템플릿 생성 및 Retrospect와 연결
    try:
        if request.temp_name.upper() == "KPT":
            template_instance = KPT(RETRO_ID=retrospect.RETRO_ID)
        elif request.temp_name.upper() == "CSS":
            template_instance = CSS(RETRO_ID=retrospect.RETRO_ID)
        elif request.temp_name.upper() == "4LS":
            template_instance = FourLs(RETRO_ID=retrospect.RETRO_ID)
        else:
            raise TemplateNotFound()

        db.add(template_instance)
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()  # 오류 발생 시 롤백
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 성공 응답 반환
    response = {
        "success": True,
        "response": {
            "retro_id": retrospect.RETRO_ID
        },
        "error": None
    }

    return response


