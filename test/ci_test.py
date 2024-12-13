import os
import sys
import pytest

# 루트 디렉토리를 프로젝트 디렉토리로 변경
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(project_root)
os.chdir(project_root)

from fastapi.testclient import TestClient
from main import app
from db.models import Sprint
from db.database import SessionLocal
from core.config import settings

class TestAPI:
    # 테스트 진행에 필요한 데이터 세팅
    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        cls.token = None
        
        cls.test_user = {
            "email": "test@example.com",
            "password": "password123",
            "nickname": "tester",
            "discord" : f"{settings.DISCORD_WEBHOOK_URL}"
        }
        cls.test_project = {
            "projectName": None,
            "manager": "Manager"
        }
        # sprintId 동적 할당
        cls.test_template = {
            "sprintId": None,
            "tempName": "KPT"
        }
        # projectId 동적 할당
        cls.project_id = None
        # retroId 동적 할당
        cls.retro_id = None  

    # 스프린트 데이터 적재 
    def add_sprint_to_db(self, project_id):
        db = SessionLocal()
        try:
            # Sprint 데이터 추가
            new_sprint = Sprint(
                PROJECT_ID=project_id,
                SPRINT_NAME="Test Sprint",
                START_DATE="2024-01-01 00:00:00",
                END_DATE="2024-01-15 23:59:59"
            )
            db.add(new_sprint)
            db.commit()
            db.refresh(new_sprint)
            return new_sprint.SPRINT_ID
        finally:
            db.close()

    # 회원가입 API 테스트
    def test_01_register_user(self):
        response = self.client.post("/v1/auth/register", json=self.test_user)
        assert response.status_code == 201
        assert response.json()["success"] == True

    # 로그인 API 테스트
    def test_02_login_user(self):
        if not self.token:
            response = self.client.post("/v1/auth/login", json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            })
            assert response.status_code == 200
            self.token = response.json()["response"]["accessToken"]
        assert self.token is not None
        return self.token

    # 프로젝트 생성 API 테스트(Sprint 데이터 추가 진행)
    def test_03_create_project(self):
        if not self.project_id:
            self.test_project["projectName"] = f"Test Project {os.urandom(4).hex()}"  # 고유한 이름 생성
            token = self.test_02_login_user()
            headers = {"Authorization": f"Bearer {token}"}
            response = self.client.post("/v1/project/", headers=headers, json=self.test_project)
            assert response.status_code == 200
            self.project_id = response.json()["response"]["projectId"]

            # 이후 API 테스트 진행을 위한 DB에 Sprint 데이터 추가
            sprint_id = self.add_sprint_to_db(self.project_id)
            assert sprint_id is not None
            self.test_template["sprintId"] = sprint_id
        assert self.project_id is not None


    # 프로젝트 조회 API 테스트
    def test_04_get_projects(self):
        self.test_03_create_project()
        token = self.test_02_login_user()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/v1/project/", headers=headers)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["response"]) > 0

    # 템플릿 선택 API 테스트
    def test_05_select_template(self):
        self.test_03_create_project()
        token = self.test_02_login_user()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/v1/templates/", headers=headers, json=self.test_template)
        print("Select Template Response:", response.json())
        assert response.status_code == 200
        assert response.json()["success"] == True
        self.retro_id = response.json()["response"]["retroId"]
        assert self.retro_id is not None

    # 회고록 리스트 API 테스트
    def test_06_get_retrospects(self):
        self.test_05_select_template()
        token = self.test_02_login_user()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(f"/v1/retrospects/{self.project_id}", headers=headers)
        assert response.status_code == 200
        assert "summary" in response.json()

    # 회고록 작성 API 테스트
    def test_07_update_retrospect(self):
        self.test_05_select_template()
        token = self.test_02_login_user()
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "retroId": self.retro_id,
            "tempName": "KPT",
            "answer": "# 스프린트1 회고록\n\n## Keep\n### 본 스프린트에서 잘된 점 또는 계속 유지해야 할 부분은 무엇인가요?\n- 모든 팀원들이 PR 내용을 꼼꼼히 확인하고 리뷰를 작성해주고 있다.\n\n## Problem\n### 본 스프린트에서 문제점 또는 개선이 필요한 부분은 무엇인가요?\n- 스프린트 마감일이 닥쳐서야 일을 진행하는 경향이 있는 것 같다.\n  - 이렇게 되면 PR 리뷰 과정이 원활하지 않으니 미리미리 구현해서 PR을 날리는 것이 바람직할 것 같다.\n\n## Try\n### 본 스프린트에서 시도해보고 싶은 새로운 아이디어나 방법은 무엇인가요?\n- 데일리 스크럼 진행하기\n  - 매일 자신이 무슨 일을 했는지 간단히 채팅방에 남기면 서로 상황 공유가 잘 되는 효과를 예상한다.\n  - 약간의 긴장감을 가지고 일을 진행하게 되어 계획대로 일의 진행이 빨라질 것 같다."
        }
        response = self.client.put("/v1/retrospects/", headers=headers, json=update_data)
        print("Update Retrospect Response:", response.json())
        assert response.status_code == 200
        assert response.json()["success"] == True

    # 회고록 상세보기 API 테스트
    def test_08_get_retrospect_detail(self):
        self.test_07_update_retrospect()
        token = self.test_02_login_user()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(f"/v1/retrospects/detail/{self.retro_id}", headers=headers)
        print("Get Retrospect Detail Response:", response.json())
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main(["-v", "--disable-warnings"])
