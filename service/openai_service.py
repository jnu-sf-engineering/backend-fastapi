import openai
import logging
from typing import List, Optional

# 직접 API 키 설정
openai.api_key = "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"

# 모델 이름 상수화
MODEL_NAME = "gpt-3.5-turbo"

# 개별 스프린트 회고 요약 함수
def summarize_individual_sprint(retrospect_text: str, bullet_points: bool = True, lines: int = 3) -> Optional[str]:
    """
    개별 스프린트 회고를 요약합니다.

    Args:
        retrospect_text (str): 회고 텍스트
        bullet_points (bool): 불렛 포인트로 요약할지 여부
        lines (int): 요약할 문장의 수

    Returns:
        Optional[str]: 요약된 텍스트. 오류 발생 시 None 반환
    """
    bullet_instruction = "bullet point로 " if bullet_points else ""
    system_instruction = f"assistant는 user의 입력을 {bullet_instruction}{lines}줄로 요약해준다."
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": retrospect_text}
    ]

    try:
        response = openai.ChatCompletion.create(model=MODEL_NAME, messages=messages)
        result = response['choices'][0]['message']['content']
        return result
    except Exception as e:
        logging.error(f"Error in summarize_individual_sprint: {e}")
        return None

# 모든 스프린트 회고 통합 요약 함수
def summarize_all_sprints(retrospect_texts: List[str], bullet_points: bool = True, lines: int = 3) -> Optional[str]:
    """
    모든 스프린트 회고를 통합하여 요약합니다.

    Args:
        retrospect_texts (List[str]): 각 스프린트 회고 텍스트의 리스트
        bullet_points (bool): 불렛 포인트로 요약할지 여부
        lines (int): 요약할 문장의 수

    Returns:
        Optional[str]: 통합하여 요약된 텍스트. 오류 발생 시 None 반환
    """
    combined_text = "\n\n".join(retrospect_texts)
    bullet_instruction = "bullet point로 " if bullet_points else ""
    system_instruction = f"assistant는 user의 모든 입력을 통합하여 {bullet_instruction}{lines}줄로 요약해준다."
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": combined_text}
    ]

    try:
        response = openai.ChatCompletion.create(model=MODEL_NAME, messages=messages)
        result = response['choices'][0]['message']['content']
        return result
    except Exception as e:
        logging.error(f"Error in summarize_all_sprints: {e}")
        return None





