from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Project
from error.exceptions import MissingFieldData, DuplicateProjectName, ProjectNotFound, DuplicateProjectData
from router.token_decode import decode_access_token

# 프로젝트 라우터
router = APIRouter(prefix="/v1/project", tags=["프로젝트"])

# 프로젝트 생성/수정/삭제 요청 검증
class ProjectRequest(BaseModel):
    projectName: str
    manager: str

# 프로젝트 조회 요청 검증
class ProjectListResponse(BaseModel):
    projectId: int
    projectName: str
    sprintCount: int
    manager: str


# Authorization 헤더에서 토큰 추출 및 디코딩
def get_user_from_token(authorization: str = Header(...)):
    # Bearer 토큰에서 실제 토큰 값 추출
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    return payload.get("user_id")  # 토큰에서 user_id 추출


# 프로젝트 소유 여부 로직
def validate_project_access(user_id: int, projectId: int, db: Session):
    project = db.query(Project).filter(
        Project.PROJECT_ID == projectId,
        Project.USER_ID == user_id
    ).first()

    if not project:
        raise ProjectNotFound()
    return project


# 프로젝트 목록 조회
@router.get("/", response_model=dict)
async def get_projects(user_id: int = Depends(get_user_from_token), db: Session = Depends(get_db)):

    # 프로젝트 조회
    projects = db.query(Project).filter(Project.USER_ID == user_id).all()

    # 프로젝트 존재 하지 않을 경우 로직
    if not projects:
        raise ProjectNotFound()
    
    # 반환값 구성
    response = [
        {
            "projectId": project.PROJECT_ID,
            "projectName": project.PROJECT_NAME,
            "sprintCount": project.SPRINT_COUNT,
            "manager": project.MANAGER
        }
        for project in projects
    ]

    result = {
        "success": True,
        "response": response,
        "error": None
    }
    
    return result


# 프로젝트 생성
@router.post("/", response_model=dict)
async def create_project(request: ProjectRequest,
                         user_id: int = Depends(get_user_from_token), 
                         db: Session = Depends(get_db)):
    
    # 프로젝트 생성 시 필드 누락 검증
    if not request.projectName or not request.manager:
        raise MissingFieldData(['projectName', "manager"])
    
    # 프로젝트명 중복 확인
    duplcate_project = db.query(Project).filter(Project.PROJECT_NAME == request.projectName, 
                                                Project.USER_ID == user_id).first()
    if duplcate_project:
        raise DuplicateProjectName()

    # 프로젝트 생성 후 데이터베이스 적재
    new_project = Project(
        PROJECT_NAME=request.projectName, MANAGER=request.manager, 
        USER_ID=user_id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # 프로젝트 ID 반환값 설정
    response = {
        "success": True,
        "response": {
            "projectId": new_project.PROJECT_ID
        },
        "error": None
    }

    return response


# 프로젝트 수정
@router.put("/{projectId}", response_model=dict)
async def update_project(projectId: int,
                         request: ProjectRequest,
                         user_id: int = Depends(get_user_from_token), 
                         db: Session = Depends(get_db)):
    
    # 프로젝트 소유 여부 확인
    project = validate_project_access(user_id, projectId, db)
    
    # 기존 프로젝트 데이터와 동일할 경우 예외 처리
    if project.PROJECT_NAME == request.projectName and project.MANAGER == request.manager:
        raise DuplicateProjectData()
    
    
    # 프로젝트 정보 수정 후 업데이트
    project.PROJECT_NAME = request.projectName
    project.MANAGER = request.manager
    db.commit()
    db.refresh(project)
    
    # 프로젝트 정보 수정 후 프로젝트 ID 반환값 설정
    response = {
        "success": True,
        "response": {
            "projectId": project.PROJECT_ID
        },
        "error": None
    }

    return response


# 프로젝트 삭제
@router.delete("/{projectId}", response_model=dict)
async def delete_project(projectId: int,
                         user_id: int = Depends(get_user_from_token), 
                         db: Session = Depends(get_db)):
    
    # 프로젝트 소유 여부 확인
    project = validate_project_access(user_id, projectId, db)
    
    # 프로젝트 정보 삭제 
    db.delete(project)
    db.commit()

    # 프로젝트 정보 삭제 후 메시지 전달
    response = {
        "success" : True,
        "response": {
            "message": "프로젝트 삭제 완료"
        },
        "error": None
    }
    
    return response