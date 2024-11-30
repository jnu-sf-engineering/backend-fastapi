from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Union, Optional
from sqlalchemy.orm import Session, joinedload
from db.database import get_db
from db.models import Retrospect, KPT, CSS, FourLs, Sprint, Project, Summary
from router.token_decode import get_user_id_from_token
from router.openai_service import field_advice, summarize_sprint_content, summarize_project_retrospects


# 회고록 라우터
router = APIRouter(prefix="/v1/retrospects", tags=["회고록"])

# KPT 요청 데이터 모델
class KPTAnswer(BaseModel):
    keep: Optional[str] = None
    problem: Optional[str] = None
    Try: Optional[str] = None

# CSS 요청 데이터 모델
class CSSAnswer(BaseModel):
    Continue: Optional[str] = None
    stop: Optional[str] = None
    start: Optional[str] = None

# 4LS 요청 데이터 모델
class FourLSAnswer(BaseModel):
    liked: Optional[str] = None
    learned: Optional[str] = None
    lacked: Optional[str] = None
    loggedFor: Optional[str] = None

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

# DB에서 특정 템플릿 데이터 조회 함수
def get_template_data(db: Session, retro_id: int, temp_name: str):
    templates = {
        "KPT": KPT,
        "CSS": CSS,
        "FOUR_LS": FourLs
    }
    template_model = templates.get(temp_name)
    if not template_model:
        raise HTTPException(status_code=400, detail="Invalid template name")

    template_data = db.query(template_model).filter_by(RETRO_ID=retro_id).first()
    if not template_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{temp_name} data not found"
        )
    return template_data


# 공통 템플릿 필드 업데이트 함수
def update_template_fields(template_data, answer: dict):
    for key, value in answer.items():
        # SQLAlchemy 모델 필드 이름에 정확히 맞추어 대문자로 변환
        setattr(template_data, key.upper(), value)


# 전체 회고 요약 업데이트 함수
def update_project_summary(project_id: int, db: Session):
    # 프로젝트에 속한 모든 회고 요약 가져오기
    retrospects = (
        db.query(Retrospect.SUMMARY)
        .join(Sprint, Retrospect.SPRINT_ID == Sprint.SPRINT_ID)
        .filter(Sprint.PROJECT_ID == project_id)
        .all()
    )

    # 회고 요약이 없으면 처리 x
    summaries = [retrospect[0] for retrospect in retrospects if retrospect[0]]
    
    if not summaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No retrospects available for the project."
        )
    
    # 프로젝트 전체 회고 요약 생성
    project_summary = summarize_project_retrospects(summaries)
    if not project_summary:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate project summary"
        )
    
    # SUMMARY 테이블 업데이트 또는 새로 추가
    existing_summary = db.query(Summary).filter(Summary.PROJECT_ID == project_id).first()
    if existing_summary:
        existing_summary.SUMMARY_CONTENT = project_summary
        existing_summary.LAST_UPDATED = datetime.now()
    else:
        new_summary = Summary(
            PROJECT_ID=project_id,
            SUMMARY_CONTENT=project_summary,
            LAST_UPDATED=datetime.now()
        )
        db.add(new_summary)

    db.commit()

# 회고 내용 업데이트
@router.put("/", response_model=dict)
async def update_retrospect(
    request: RetroRequest,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    # Retrospect 확인 및 소유권 검증
    retrospect = (
        db.query(Retrospect)
        .join(Sprint, Retrospect.SPRINT_ID == Sprint.SPRINT_ID)
        .join(Project, Sprint.PROJECT_ID == Project.PROJECT_ID)
        .filter(Project.USER_ID == user_id, Retrospect.RETRO_ID == request.retroId)
        .first()
    )
    if not retrospect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retrospect not found or access denied"
        )

    # 템플릿별 처리 내용 수집: 스프린트 회고 요약에 사용
    template_data = get_template_data(db, request.retroId, request.tempName)

    # Update template fields
    update_template_fields(template_data, request.answer.dict(exclude_unset=True))
    db.commit()


    contents = {field.lower(): getattr(template_data, field.upper()) for field in request.answer.dict()}
    summary = summarize_sprint_content(request.tempName, contents)
    if not summary:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate sprint summary"
        )

    retrospect.SUMMARY = summary
    db.commit()

    update_project_summary(retrospect.sprint.PROJECT_ID, db)

    response = {
        "success": True,
        "response": {
            "retroId": retrospect.RETRO_ID
            }, 
        "error": None
    }

    return response


# 회고록 리스트 조회
@router.get("/{projectId}", response_model=dict)
async def get_project_retrospects(
    projectId: int,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    # 프로젝트 확인 및 소유권 검증
    project = (
        db.query(Project)
        .filter(Project.PROJECT_ID == projectId, Project.USER_ID == user_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )

    # 프로젝트의 회고 요약 (최신 summary 가져오기)
    latest_summary = (
        db.query(Summary.SUMMARY_CONTENT)
        .filter(Summary.PROJECT_ID == projectId)
        .order_by(Summary.LAST_UPDATED.desc())
        .first()
    )
    summary_content = latest_summary[0] if latest_summary else "No summary available."

    # 프로젝트의 모든 회고록 정보 가져오기
    retrospects_data = (
        db.query(Retrospect, Sprint.SPRINT_ID, Sprint.SPRINT_NAME, Sprint.START_DATE, Sprint.END_DATE)
        .join(Sprint, Retrospect.SPRINT_ID == Sprint.SPRINT_ID)
        .filter(Sprint.PROJECT_ID == projectId)
        .all()
    )

    if not retrospects_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No retrospects found for this project."
        )

    # 응답 데이터 구성
    retrospects_list = []
    for retro, sprint_id, sprint_name, start_date, end_date in retrospects_data:
        retrospects_list.append({
            "retroId": retro.RETRO_ID,
            "sprintId": sprint_id,
            "sprintName": sprint_name,
            "startDate": start_date.strftime("%Y.%m.%d"),
            "endDate": end_date.strftime("%Y.%m.%d"),
            "tempName": "KPT" if retro.kpt else "CSS" if retro.css else "FOUR_LS" if retro.four_ls else None,
            "manager": project.MANAGER,
        })

    response = {
        "projectId": projectId,
        "summary": summary_content,
        "retrospects": retrospects_list,
    }

    return response


# 회고록 상세보기
@router.get("/detail/{retroId}", response_model=dict)
async def get_retrospect_detail(
    retroId: int,
    db: Session = Depends(get_db)
):
    # Retrospect와 관련된 Sprint 정보 로드
    retrospect = (
        db.query(Retrospect)
        .options(
            joinedload(Retrospect.sprint),
            joinedload(Retrospect.kpt),
            joinedload(Retrospect.css),
            joinedload(Retrospect.four_ls)
        )
        .filter(Retrospect.RETRO_ID == retroId)
        .first()
    )

    if not retrospect:
        raise HTTPException(
            status_code=404,
            detail="Retrospect not found."
        )

    # Sprint 정보 로드
    sprint = retrospect.sprint
    if not sprint:
        raise HTTPException(
            status_code=500,
            detail="Sprint data is missing for the given retrospect."
        )

    # 템플릿별 데이터 구성
    temp_name = ""
    answer = {}
    if retrospect.kpt:
        temp_name = "KPT"
        answer = {
            "keep": retrospect.kpt.KEEP or "",
            "problem": retrospect.kpt.PROBLEM or "",
            "try_": retrospect.kpt.TRY or "",
        }
    elif retrospect.css:
        temp_name = "CSS"
        answer = {
            "continue_": retrospect.css.CSS_CONTINUE or "",
            "stop": retrospect.css.CSS_STOP or "",
            "start": retrospect.css.CSS_START or "",
        }
    elif retrospect.four_ls:
        temp_name = "FOUR_LS"
        answer = {
            "liked": retrospect.four_ls.LIKED or "",
            "learned": retrospect.four_ls.LEARNED or "",
            "lacked": retrospect.four_ls.LACKED or "",
            "loggedFor": retrospect.four_ls.LOGGED_FOR or "",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="No template data found for the given retrospect."
        )

    # 응답 데이터 구성
    response = {
        "success": True,
        "response": {
            "sprintName": sprint.SPRINT_NAME,
            "tempName": temp_name,
            "answer": answer
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


