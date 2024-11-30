from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Project, Sprint, Retrospect, KPT, CSS, FourLs
from router.token_decode import get_user_id_from_token

# 프로젝트 라우터
router = APIRouter(prefix="/v1/templates", tags=["회고록 템플릿"])

# 요청 바디 모델
class TemplateRequest(BaseModel):
    sprintId: int
    tempName: str


# 템플릿 선택 API
@router.post("/", response_model=dict)
async def select_template(
    request: TemplateRequest,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):

    # sprintId 유효성 검사 및 소유 확인
    sprint = (
        db.query(Sprint)
        .join(Project, Sprint.PROJECT_ID == Project.PROJECT_ID)
        .filter(Sprint.SPRINT_ID == request.sprintId, Project.USER_ID == user_id)
        .first()
    )
    
    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint not found"
        )
    
    # Retrospect 생성 및 커밋
    retrospect = Retrospect(SPRINT_ID=request.sprintId, SUMMARY="")
    db.add(retrospect)
    db.commit()  
    db.refresh(retrospect)
    

    # 템플릿 유형에 따라 처리
    template_map = {
        "KPT": KPT,
        "FOUR_LS": FourLs,
        "CSS": CSS
    }
    TemplateModel = template_map.get(request.tempName)
    if not TemplateModel:
        raise HTTPException(status_code=400, detail="Invalid template name")

    template_data = TemplateModel(RETRO_ID=retrospect.RETRO_ID)
    db.add(template_data)
    db.commit()

    response = {
        "success": True,
        "response": {
            "retroId": retrospect.RETRO_ID, 
            "template": request.tempName
            }, 
        "error": None
    }

    return response