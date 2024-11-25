from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Retrospect, Project, Sprint, KPT, CSS, FourLs
from error.exceptions import (
    RetrospectMissingFieldData, RetrospectProjectNotFound, InvalidSprintException,
    DuplicateRetrospectException, NoRetrospectsFound,
    RetrospectNotFound, InvalidTemplateTypeException
)
from typing import List, Optional, Union
from router.project import get_user_id
from service.openai_service import summarize_individual_sprint, summarize_all_sprints

# 프로젝트 라우터
router = APIRouter(prefix="/v1/retrospects", tags=["회고록"])

# 템플릿 이름 상수 정의
TEMPLATE_KPT = "KPT"
TEMPLATE_CSS = "CSS"
TEMPLATE_4LS = "4LS"

# 회고록 작성 요청 검증 모델
class KPTAnswer(BaseModel):
    keep: str
    problem: str
    try_: str

class CSSAnswer(BaseModel):
    css_continue: str
    css_stop: str
    css_start: str

class FourLsAnswer(BaseModel):
    liked: str
    learned: str
    lacked: str
    logged_for: str

class CreateRetrospectRequest(BaseModel):
    retro_id: int
    template_name: str  # "KPT", "CSS", "4Ls"
    answers: Optional[KPTAnswer | CSSAnswer | FourLsAnswer]

# 회고록 목록 조회 응답 모델
class RetrospectSummaryResponse(BaseModel):
    project_id: int
    summary: str
    retrospects: List[dict]

# 회고록 상세 조회 응답 모델
class RetrospectDetailResponse(BaseModel):
    retro_id: int
    sprint_id: int
    sprint_name: str
    template_name: str
    answers: dict

# 요청 모델 정의
class RetrospectText(BaseModel):
    type: str  # "individual" or "all"
    retrospect_text: Union[str, None] = None
    retrospect_texts: Union[List[str], None] = None

# 헤더에서 sprint_id 추출
def get_sprint_id(sprint_id: int = Header(...)):
    return sprint_id

# 회고록 작성
@router.post("/", response_model=dict)
async def create_retrospect(request: CreateRetrospectRequest,
                            sprint_id: int = Depends(get_sprint_id),
                            db: Session = Depends(get_db)):

    # 필드 누락 검증
    if not request.retro_id or not request.template_name or not request.answers:
        raise RetrospectMissingFieldData(["retro_id", "template_name", "answers"])

    # 스프린트 유효성 검증
    sprint = db.query(Sprint).filter(Sprint.SPRINT_ID == sprint_id).first()
    if not sprint:
        raise InvalidSprintException()

    # 중복 회고 검증
    existing_retro = db.query(Retrospect).filter(Retrospect.RETRO_ID == request.retro_id).first()
    if existing_retro:
        raise DuplicateRetrospectException()

    # 새로운 회고 생성 후 데이터베이스 적재
    new_retro = Retrospect(
        RETRO_ID=request.retro_id,
        SPRINT_ID=sprint_id,
        SUMMARY="회고 요약 내용"  # 임시로 추가된 요약 내용
    )
    db.add(new_retro)
    db.commit()
    db.refresh(new_retro)

    # 템플릿에 맞춰 답변 저장
    if request.template_name.upper() == TEMPLATE_KPT:
        new_answer = KPT(
            RETRO_ID=request.retro_id,
            KEEP=request.answers.keep,
            PROBLEM=request.answers.problem,
            TRY=request.answers.try_
        )
    elif request.template_name.upper() == TEMPLATE_CSS:
        new_answer = CSS(
            RETRO_ID=request.retro_id,
            CSS_CONTINUE=request.answers.css_continue,
            CSS_STOP=request.answers.css_stop,
            CSS_START=request.answers.css_start
        )
    elif request.template_name.upper() == TEMPLATE_4LS:
        new_answer = FourLs(
            RETRO_ID=request.retro_id,
            LIKED=request.answers.liked,
            LEARNED=request.answers.learned,
            LACKED=request.answers.lacked,
            LOGGED_FOR=request.answers.logged_for
        )
    else:
        raise InvalidTemplateTypeException()

    db.add(new_answer)
    db.commit()

    response = {
        "success": True,
        "response": {
            "retro_id": new_retro.RETRO_ID
        },
        "error": None
    }

    return response

# 회고록 목록 조회
@router.get("/{project_id}", response_model=dict)
async def get_project_retrospect_summary(
        project_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    # 프로젝트 조회
    project = db.query(Project).filter(Project.PROJECT_ID == project_id, Project.USER_ID == user_id).first()
    if not project:
        raise RetrospectProjectNotFound()

    # 회고록 목록 조회
    retrospects = db.query(Retrospect).filter(Retrospect.PROJECT_ID == project_id).all()
    if not retrospects:
        raise NoRetrospectsFound()

    # 회고록 요약 정보 리스트 생성
    retrospect_details = [
        {
            "retro_id": retrospect.RETRO_ID,
            "sprint_id": retrospect.SPRINT_ID,
            "summary": retrospect.SUMMARY
        }
        for retrospect in retrospects
    ]

    summary = "모든 회고록 내용 기반 요약한 내용"  # 예시 요약

    response = {
        "success": True,
        "response": {
            "project_id": project.PROJECT_ID,
            "summary": summary,
            "retrospects": retrospect_details
        },
        "error": None
    }

    return response

# 회고록 상세 조회
@router.get("/{retro_id}", response_model=dict)
async def get_retrospect_detail(
        retro_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    retrospect = db.query(Retrospect).filter(Retrospect.RETRO_ID == retro_id).first()
    if not retrospect:
        raise RetrospectNotFound()

    sprint = db.query(Sprint).filter(Sprint.SPRINT_ID == retrospect.SPRINT_ID).first()
    if not sprint:
        raise RetrospectNotFound()
    # 템플릿에 맞춰 답변 조회
    if retrospect.SUMMARY == TEMPLATE_KPT:
        answer = db.query(KPT).filter(KPT.RETRO_ID == retro_id).first()
        answer_details = {"keep": answer.KEEP, "problem": answer.PROBLEM, "try_": answer.TRY}
    elif retrospect.SUMMARY == TEMPLATE_CSS:
        answer = db.query(CSS).filter(CSS.RETRO_ID == retro_id).first()
        answer_details = {"css_continue": answer.CSS_CONTINUE, "css_stop": answer.CSS_STOP, "css_start": answer.CSS_START}
    elif retrospect.SUMMARY == TEMPLATE_4LS:
        answer = db.query(FourLs).filter(FourLs.RETRO_ID == retro_id).first()
        answer_details = {
            "liked": answer.LIKED,
            "learned": answer.LEARNED,
            "lacked": answer.LACKED,
            "logged_for": answer.LOGGED_FOR
        }
    else:
        raise InvalidTemplateTypeException()

    response = {
        "success": True,
        "response": {
            "retro_id": retrospect.RETRO_ID,
            "sprint_id": sprint.SPRINT_ID,
            "sprint_name": sprint.SPRINT_NAME,
            "template_name": retrospect.SUMMARY,
            "answers": answer_details
        },
        "error": None
    }

    return response

# 회고 요약 엔드포인트
@router.post("/advice", response_model=dict)
async def post_retrospect_summary(request: RetrospectText):
    # 단일 스프린트 요약 요청 처리
    if request.type == "individual" and request.retrospect_text:
        summary = summarize_individual_sprint(request.retrospect_text)
    # 전체 스프린트 통합 요약 요청 처리
    elif request.type == "all" and request.retrospect_texts:
        summary = summarize_all_sprints(request.retrospect_texts)
    else:
        return {"success": False, "error": "Invalid input data. Please provide a valid type and text(s)."}

    return {"success": True, "summary": summary, "error": None}


