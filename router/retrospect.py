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


# 공통 요청 모델
class RetroRequest(BaseModel):
    retroId: int
    tempName: str
    answer: Union[str, dict]


# 조언 요청 모델
class AdviceRequest(BaseModel):
    tempName: str
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


# # 공통 템플릿 필드 업데이트 함수
# def update_template_fields(template_data, answer):
#     if isinstance(answer, str):
#         # 텍스트 형식의 answer를 통째로 저장
#         setattr(template_data, "SUMMARY", answer)
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="updated_template_fields error"
#         )
        

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

# 템플릿 내용(answer) 파싱하여 데이터 추출
def parse_template(content: str, section_headers: dict) -> dict:
    lines = content.splitlines()
    current_section = None
    parsed_data = {key: "" for key in section_headers.values()} 

    for line in lines:
        stripped_line = line.strip()
        # 섹션 시작
        for header, db_field in section_headers.items():
            if stripped_line == header:
                current_section = db_field
                break

        # 섹션 내용을 저장
        if current_section and stripped_line and not stripped_line.startswith("##"):
            parsed_data[current_section] += stripped_line + "\n"

        # 섹션 종료
        if stripped_line.startswith("## ") and stripped_line != header:
            current_section = None

    # 공백 제거
    return {key: value.strip() for key, value in parsed_data.items()}



# 파싱 함수(조언)
def extract_section(content: str, section_header: str) -> str:
    lines = content.splitlines()
    section_found = False
    section_content = []

    for line in lines:
        # 섹션 시작
        if line.strip() == section_header:
            section_found = True
            continue
        # 다음 섹션으로 이동
        if section_found and line.startswith("## "):
            break
        # 현재 섹션의 내용을 수집
        if section_found:
            section_content.append(line.strip())
    
    extracted = "\n".join(section_content).strip()
    return extracted


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

    # 템플릿별 섹션 정의
    TEMPLATE_HEADERS = {
        "KPT": {"## Keep": "KEEP", "## Problem": "PROBLEM", "## Try": "TRY"},
        "CSS": {"## Continue": "CSS_CONTINUE", "## Stop": "CSS_STOP", "## Start": "CSS_START"},
        "FOUR_LS": {"## Liked": "LIKED", "## Learned": "LEARNED", "## Lacked": "LACKED", "## LoggedFor": "LOGGED_FOR"}
    }

    if request.tempName not in TEMPLATE_HEADERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template name"
        )


    # 템플릿별 처리 내용 수집: 스프린트 회고 요약에 사용
    template_data = get_template_data(db, request.retroId, request.tempName)

    # 템플릿 파싱 및 필드 업데이트
    section_headers = TEMPLATE_HEADERS[request.tempName]
    parsed_data = parse_template(request.answer, section_headers)
    for field, value in parsed_data.items():
        setattr(template_data, field, value)

    db.commit()

    # 요약 생성 및 업데이트
    summary = summarize_sprint_content(request.tempName, parsed_data)
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
        answer = (
            f"# {sprint.SPRINT_NAME} 회고록\n\n"
            f"## Keep\n### 본 스프린트에서 잘된 점 또는 계속 유지해야 할 부분은 무엇인가요?\n"
            f"{retrospect.kpt.KEEP or '-'}\n\n"
            f"## Problem\n### 본 스프린트에서 문제점 또는 개선이 필요한 부분은 무엇인가요?\n"
            f"{retrospect.kpt.PROBLEM or '-'}\n\n"
            f"## Try\n### 본 스프린트에서 시도해보고 싶은 새로운 아이디어나 방법은 무엇인가요?\n"
            f"{retrospect.kpt.TRY or '-'}"
        )
    elif retrospect.css:
        temp_name = "CSS"
        answer = (
            f"# {sprint.SPRINT_NAME} 회고록\n\n"
            f"## Continue\n### 프로젝트에 좋은 영향을 끼쳤거나 계속 유지하고 싶은 행동은 무엇이었나요?\n"
            f"{retrospect.css.CSS_CONTINUE or '-'}\n\n"
            f"## Stop\n### 프로젝트에 부정적인 영향을 주거나 비효율적인 행동은 무엇이었나요?\n"
            f"{retrospect.css.CSS_STOP or '-'}\n\n"
            f"## Start\n### 개선에 필요한 행동을 작성해주세요!\n"
            f"{retrospect.css.CSS_START or '-'}"
        )
    elif retrospect.four_ls:
        temp_name = "FOUR_LS"
        answer = (
            f"# {sprint.SPRINT_NAME} 회고록\n\n"
            f"## Liked\n### 프로젝트를 진행하며 좋았던 부분과 그 이유는 무엇인가요?\n"
            f"{retrospect.four_ls.LIKED or '-'}\n\n"
            f"### 남은 프로젝트 동안 지속되었으면 하는 것은 무엇인가요?\n"
            f"{retrospect.four_ls.LIKED_EXTRA or '-'}\n\n"
            f"## Learned\n### 프로젝트를 진행하며 배운 점은 무엇인가요?\n"
            f"{retrospect.four_ls.LEARNED or '-'}\n\n"
            f"## Laked\n### 프로젝트 진행중 본인 또는 팀이 부족했던 점을 작성해주세요\n"
            f"{retrospect.four_ls.LACKED or '-'}\n\n"
            f"## Logged For\n### 프로젝트에서 희망하는 점을 작성해주세요\n"
            f"{retrospect.four_ls.LOGGED_FOR or '-'}\n\n"
            f"### 프로젝트에서 얻어가고 싶은 점을 작성해주세요\n"
            f"{retrospect.four_ls.LOGGED_FOR_EXTRA or '-'}"
        )
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
            "answer": answer.strip()
        },
        "error": None
    }

    return response


@router.post("/advice", response_model=dict)
async def get_advice(request: AdviceRequest):
    # 템플릿별 추출할 섹션 정의
    valid_templates = {
        "KPT": "## Problem",
        "CSS": "## Stop",
        "FOUR_LS": "## Lacked"
    }
    section_header = valid_templates.get(request.tempName)
    if not section_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid template name"
        )

    # fieldValue 유효성 검증
    if not request.fieldValue or request.fieldValue.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="fieldValue cannot be empty"
        )
    
    # 섹션 추출
    extracted_content = extract_section(request.fieldValue, section_header)
    if not extracted_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No content found under {section_header} section"
        )

    # ChatGPT 조언
    advice = field_advice(request.tempName, section_header, extracted_content)
    if not advice:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate advice from OpenAI"
        )

    response = {
        "success": True,
        "response": {
            "advice": advice
            }, 
        "error": None
    }
    
    return response


