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
    
    # Retrospect 생성(Summary는 업데이트 예정)
    retrospect = Retrospect(SPRINT_ID=request.sprintId, SUMMARY="")
    db.add(retrospect)
    db.commit()
    db.refresh(retrospect)

    # 템플릿 유형에 따라 처리
    if request.tempName == "KPT":
        kpt = KPT(RETRO_ID=retrospect.RETRO_ID, KEEP="", PROBLEM="", TRY="")
        db.add(kpt)
    elif request.tempName == "FOUR_LS":
        four_ls = FourLs(RETRO_ID=retrospect.RETRO_ID, LIKED="", LEARNED="", LACKED="", LOGGED_FOR="")
        db.add(four_ls)
    elif request.tempName == "CSS":
        css = CSS(RETRO_ID=retrospect.RETRO_ID, CSS_CONTINUE="", CSS_STOP="", CSS_START="")
        db.add(css)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template name"
        )

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