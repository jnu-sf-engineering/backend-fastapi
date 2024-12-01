import os
import sys
from unittest.mock import patch
import pytest

# Root directory를 Project Root로 설정
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(project_root)  # 프로젝트 루트를 sys.path에 추가

# Mock된 OpenAI 응답 데이터
MOCK_CHAT_COMPLETION_RESPONSE = {
    "choices": [
        {"message": {"content": "Mocked response content"}}
    ]
}

# router 모듈에서 함수들 임포트
from router.openai_service import field_advice, summarize_sprint_content, summarize_project_retrospects


@pytest.fixture
def mock_openai_chat():
    """OpenAI ChatCompletion.create를 mock으로 대체"""
    with patch("openai.ChatCompletion.create") as mock_create:
        # Mock된 응답을 설정
        mock_create.return_value = MOCK_CHAT_COMPLETION_RESPONSE
        yield mock_create  # 테스트에서 mock_create를 사용할 수 있도록 반환


def test_field_advice(mock_openai_chat):
    """field_advice 함수 테스트"""
    temp_name = "KPT"
    field_name = "problem"
    field_value = "팀워크 부족"

    # field_advice 함수 실행
    result = field_advice(temp_name, field_name, field_value)

    # OpenAI ChatCompletion.create가 한 번 호출되었는지 확인
    mock_openai_chat.assert_called_once()

    # 결과를 로그로 확인
    print("field_advice result:", result)

    # 결과가 mock 응답과 일치하는지 확인
    assert result == "Mocked response content"


def test_summarize_sprint_content(mock_openai_chat):
    """summarize_sprint_content 함수 테스트"""
    temp_name = "CSS"
    contents = {
        "continue": "정기 회의",
        "stop": "비효율적인 코드 리뷰",
        "start": "자동화 도구 사용"
    }

    # summarize_sprint_content 함수 실행
    result = summarize_sprint_content(temp_name, contents)

    # OpenAI ChatCompletion.create가 한 번 호출되었는지 확인
    mock_openai_chat.assert_called_once()

    # 결과를 로그로 확인
    print("summarize_sprint_content result:", result)

    # 결과가 mock 응답과 일치하는지 확인
    assert result == "Mocked response content"


def test_summarize_project_retrospects(mock_openai_chat):
    """summarize_project_retrospects 함수 테스트"""
    summaries = [
        "스프린트 1: 정기 회의가 효과적이었음",
        "스프린트 2: 코드 리뷰 개선 필요"
    ]

    # summarize_project_retrospects 함수 실행
    result = summarize_project_retrospects(summaries)

    # OpenAI ChatCompletion.create가 한 번 호출되었는지 확인
    mock_openai_chat.assert_called_once()

    # 결과를 로그로 확인
    print("summarize_project_retrospects result:", result)

    # 결과가 mock 응답과 일치하는지 확인
    assert result == "Mocked response content"




