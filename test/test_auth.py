import os
import sys
import pytest

# Root directory를 Project Root로 설정
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(project_root)
os.chdir(project_root)

from fastapi.testclient import TestClient
from main import app

# 클라이언트 설정
client = TestClient(app)

# 테스트용 회원가입 데이터 설정
test_user = {
    "email" : "testuser@example.com",
    "password": "testpassword"
}

@pytest.fixture(scope="module")
def setup_user():
    # 회원가입 진행 후 사용자 등록
    response = client.post("/v1/auth/register", json=test_user)
    assert response.status_code == 201
    assert response.json() == {
        "success": True,
        "response": {
            "message": "회원가입 성공"
        },
        "error": None
    }
    yield  

def test_login_user(setup_user):
    # 회원가입된 사용자를 이용하여 로그인 성공 유무 테스트
    response = client.post("/v1/auth/login", json=test_user)
    assert response.status_code == 200
    # 응답 성공 유무
    assert response.json()["success"] is True
    # 응답에 user_id 포함 유무 
    assert "user_id" in response.json()["response"]
