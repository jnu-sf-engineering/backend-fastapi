from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr, Field, BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Project

# 프로젝트 라우터
router = APIRouter(prefix="/v1/project", tags=["프로젝트"])

# 프로젝트 생성/수정/삭제 요청 검증
class ProjectRequest(BaseModel):
    project_name: str
    manager: str

# 프로젝트 조회 요청 검증
class ProjectListRequest(BaseModel):
    user_id: int

# 프로젝트 응답 검증
class ProjectListResponse(BaseModel):
    project_id: int
    project_name: str
    sprint_count: int
    manager: str


# 프로젝트 목록 조회
@router.get("/", response_model=dict)
async def get_projects(request: ProjectListRequest, db: Session = Depends(get_db)):
    
    # 프로젝트 조회
    projects = db.query(Project).filter(Project.USER_ID == request.user_id).all()

    # 프로젝트 존재 하지 않을 경우 로직
    if not projects:
        return {"success": False, "response": [], "error": "No projects found for this user."}
    
    
    response = [
        {
            "project_id": project.PROJECT_ID,
            "project_name": project.PROJECT_NAME,
            "sprint_count": project.SPRINT_COUNT,
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
async def create_project(request: ProjectRequest, db: Session = Depends(get_db)):
    
    # 프로젝트 생성 후 데이터베이스 적재
    new_project = Project(
        PROJECT_NAME=request.project_name,
        MANAGER=request.manager
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # 프로젝트 ID 반환값 설정
    response = {
        "success": True,
        "response": {
            "project_id": new_project.PROJECT_ID
        },
        "error": None
    }

    return response


# 프로젝트 수정
@router.put("/{project_id}", response_model=dict)
async def update_project(project_id: int, request: ProjectRequest, db: Session = Depends(get_db)):
    
    # path parameter에 해당하는 프로젝트 조회
    project = db.query(Project).filter(Project.PROJECT_ID == project_id).first()
    
    # 해당하는 프로젝트 존재 하지 않을 경우 로직
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # 프로젝트 정보 수정 후 업데이트
    project.PROJECT_NAME = request.project_name
    project.MANAGER = request.manager
    db.commit()
    db.refresh(project)
    
    # 프로젝트 정보 수정 후 프로젝트 ID 반환값 설정
    response = {
        "success": True,
        "response": {
            "project_id": project.PROJECT_ID
        },
        "error": None
    }

    return response


# 프로젝트 삭제
@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    
    # path parameter에 해당하는 프로젝트 조회
    project = db.query(Project).filter(Project.PROJECT_ID == project_id).first()

    # 해당하는 프로젝트 존재 하지 않을 경우 로직
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
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