from openai import OpenAI
from core.config import settings
from typing import List, Optional


# 모델 이름
MODEL_NAME = "gpt-4o-mini"

# Chatgpt API 사용
client = OpenAI(api_key = settings.OPENAI_API_KEY)

# 회고 필드 조언
def field_advice(temp_name: str, field_name: str, field_value: str):
    try:
        # 조언을 받을 필드와 섹션 헤더 정의
        valid_advice_fields = {
            "KPT": "## Problem",
            "CSS": "## Stop",
            "FOUR_LS": "## Lacked"
        }

        # 템플릿이 유효한지 확인
        if temp_name not in valid_advice_fields:
            return "Invalid template name. Advice not available for this template."

        # 필드가 유효한지 확인
        if field_name not in valid_advice_fields[temp_name]:
            return f"Advice is not provided for the '{field_name}' field in the '{temp_name}' template."

        # 템플릿별 가이드
        template_guides = {
            "KPT": (
                "KPT 템플릿은 Keep(성공적으로 진행된 점), Problem(개선이 필요한 점), "
                "Try(앞으로 시도할 것)로 구성됩니다. 각각의 필드는 팀의 성장과 발전을 목표로 합니다."
            ),
            "CSS": (
                "CSS 템플릿은 Continue(계속해야 할 것), Stop(중단해야 할 것), "
                "Start(새롭게 시작해야 할 것)로 구성됩니다. 각 필드는 명확한 행동 계획을 도출하는 데 중점을 둡니다."
            ),
            "FOUR_LS": (
                "4LS 템플릿은 Liked(긍정적인 점), Learned(배운 점), "
                "Lacked(부족했던 점), LoggedFor(앞으로 활용할 점)로 구성됩니다. "
                "각 필드는 회고를 통해 교훈을 얻고 팀의 방향성을 설정하는 데 사용됩니다."
            )
        }

        # 선택된 템플릿 가이드 가져오기
        template_guide = template_guides.get(temp_name, "")

        # ChatGPT에게 전달할 프롬프트
        system_instruction = (
            "네 역할은 회고를 효과적으로 도와주는 도우미야. "
            "회고는 과거를 돌아보고 그 경험에서 배운 점을 정리하며, "
            "팀이 무엇이 잘 되었고, 무엇이 개선되어야 하는지를 학습하는 과정이야.\n\n"
            f"{template_guide}\n\n"
            "다음은 효과적인 회고를 위한 가이드야:\n"
            "- 개인화하여 말하지 않기: 마녀사냥이나 부정적인 언행을 삼가고, 사람을 비난하지 않고 실행 사실에 대해 논의하기\n"
            "- 창의적 마인드: 문제 해결에 대해 창의적으로 접근하기\n\n"
            "사용자는 템플릿의 특정 필드에 대한 회고 내용을 작성하고, 중간에 네 조언을 요청할 거야. "
            "너는 사용자가 효과적으로 회고를 진행할 수 있도록 실행 가능하고 건설적인 조언을 제공해야 해."
        )
        
        # 사용자 입력 기반 프롬프트
        prompt = (
            f"사용자는 '{temp_name}' 템플릿의 '{field_name}' 필드에 대해 다음과 같이 작성했어:\n"
            f"'{field_value}'\n\n"
            "효과적인 회고를 위해 이 작성 내용을 개선하거나 보완할 수 있는 조언을 최대 5줄로 제공해줘."
        )
        
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ]

        # OpenAI API 호출
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        advice = response.choices[0].message.content
        return advice
    
    except Exception as e:
        print(f"filed_advice 에러: {e}")
        return None


# 개별 스프린트 회고 요약
def summarize_sprint_content(temp_name: str, contents: dict):
    try:
        # 템플릿 설명
        template_descriptions = {
            "KPT": "Keep(유지할 점), Problem(개선할 점), Try(시도할 점)",
            "CSS": "Continue(계속할 점), Stop(중단할 점), Start(시작할 점)",
            "FOUR_LS": "Liked(좋았던 점), Learned(배운 점), Lacked(부족했던 점), LoggedFor(앞으로 참고할 점)"
        }
        template_description = template_descriptions.get(temp_name, "")

        # 사용자 입력 데이터 준비
        formatted_content = "\n".join([f"{field}: {value}" for field, value in contents.items() if value])

        # 프롬프트 작성
        prompt = (
            f"다음은 '{temp_name}' 템플릿을 기반으로 작성된 스프린트 회고 내용입니다:\n"
            f"{formatted_content}\n\n"
            f"템플릿 설명: {template_description}\n\n"
            "이 회고 내용을 바탕으로 요약을 작성해주세요. "
            "요약은 간결하고 중요한 점을 포함해주세요."
            "반환된 텍스트는 반드시 텍스트로만 구성되고, 줄바꿈은 한 번만 사용해주세요. 즉, \\n\\n이 아닌 필요할 때 \\n을 사용하는 것입니다."
        )

        # OpenAI 메시지 구성
        messages = [
            {"role": "system", "content": "assistant는 사용자 회고 내용을 요약합니다."},
            {"role": "user", "content": prompt},
        ]
        # OpenAI API 호출
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0
        )

        summary = response.choices[0].message.content
        return summary
    
    except Exception as e:
        print(f"summarize_sprint_content 에러: {e}")
        return None


# 종합 스프린트 회고 요약
def summarize_project_retrospects(summaries: List[str]):
    try: 
        if not summaries:
            # 회고 내용 x
            return None
        
        # OpenAI 요청을 위한 데이터 준비
        combined_text = "\n\n".join(summaries)

        # 프롬프트 작성
        prompt = (
            "다음은 특정 프로젝트의 각 스프린트에 작성된 회고 요약 내용입니다:\n"
            f"{combined_text}\n\n"
            "이 모든 회고 내용을 바탕으로 프로젝트 전체를 요약해주세요. "
            "요약은 3~5문장으로 간결하고 중요한 점만 포함해주세요."
            "반환된 텍스트는 반드시 텍스트로만 구성되고, 줄바꿈은 한 번만 사용해주세요. 즉, \\n\\n이 아닌 필요할 때 \\n을 사용하는 것입니다."
        )

        # OpenAI 메시지 구성
        messages = [
            {"role": "system", "content": "assistant는 프로젝트 전체 회고 내용을 요약합니다."},
            {"role": "user", "content": prompt},
        ]

        # OpenAI API 호출
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0
        )

        summary = response.choices[0].message.content
        return summary
    
    except Exception as e:
        print(f"summarize_projet_retrospects 에러: {e}")
        return None
