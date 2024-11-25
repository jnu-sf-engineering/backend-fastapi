from fastapi import HTTPException, status

# 이메일이 일치 유무
class EmailNotMatch(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "1001",
                    "reason": "이메일이 일치하지 않습니다.",
                    "status": "400"
                }
            }
        )

# 비밀번호 일치 유무
class PasswordNotMatch(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "1002",
                    "reason": "비밀번호가 일치하지 않습니다.",
                    "status": "400"
                }
            }
        )

# 인증 확인
class AuthenticationFailed(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "1003",
                    "reason": "인증 실패입니다.",
                    "status": "401"
                }
            }
        )


# 유저 존재 유무
class UserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "1005",
                    "reason": "요청한 user_id에 해당하는 유저가 존재하지 않습니다.",
                    "status": "404"
                }
            }
        )


# 요청: user_id 누락 확인
class UserIDMissing(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "2001",
                    "reason": "user_id 누락입니다.",
                    "status": "400"
                }
            }
        )


# 프로젝트 생성시 필드 데이터(project_name, manager) 누락
class MissingFieldData(HTTPException):
    def __init__(self, fields):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "2002",
                    "reason": f"필드 데이터 누락입니다({', '.join(fields)}).",
                    "status": "400"
                }
            }
        )

# 프로젝트명 중복 확인
class DuplicateProjectName(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "2003",
                    "reason": "중복된 프로젝트명입니다.",
                    "status": "400"
                }
            }
        )

# 프로젝트 존재 유무 
class ProjectNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "2002",
                    "reason": "존재하지 않은 프로젝트입니다.",
                    "status": "404"
                }
            }
        )


# 요청: 프로젝트 ID 유효성 확인
class InvalidProjectIDFormat(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "2005",
                    "reason": "유효하지 않은 프로젝트 ID 형식입니다.",
                    "status": "400"
                }
            }
        )


# 동일한 프로젝트 데이터 검증
class DuplicateProjectData(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "response": None,
                "error": {
                    "code": "2006",
                    "reason": "기존 프로젝트 정보와 동일한 데이터입니다.",
                    "status": "400"
                }
            }
        )

# 템플릿 선택 시 필드 데이터 누락 오류
class TemplateMissingFieldData(HTTPException):
    def __init__(self, missing_fields: list):
        detail = {
            "success": False,
            "response": None,
            "error": {
                "code": "5001",
                "reason": f"필드 데이터 누락입니다.({', '.join(missing_fields)})",
                "status": "400"
            }
        }
        super().__init__(status_code=400, detail=detail)

# 템플릿 선택 시 스프린트 존재하지 않음 오류
class TemplateSprintNotFound(HTTPException):
    def __init__(self):
        detail = {
            "success": False,
            "response": None,
            "error": {
                "code": "5002",
                "reason": "존재(유효)하지 않은 스프린트입니다.",
                "status": "404"
            }
        }
        super().__init__(status_code=404, detail=detail)

# 템플릿 존재하지 않음 오류
class TemplateNotFound(HTTPException):
    def __init__(self):
        detail = {
            "success": False,
            "response": None,
            "error": {
                "code": "5003",
                "reason": "존재(유효)하지 않은 템플릿입니다.",
                "status": "400"
            }
        }
        super().__init__(status_code=400, detail=detail)

# 유효하지 않은 템플릿 타입일 때 발생하는 예외
class InvalidTemplateTypeException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid template type. Valid types are 'KPT', 'CSS', or '4Ls'.")


#회고 필드 데이터 누락
class RetrospectMissingFieldData(HTTPException):
    def __init__(self, fields):
        super().__init__(status_code=400, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "5004",
                "reason": f"필드 데이터 누락입니다.({', '.join(fields)})",
                "status": "400"
            }
        })

#회고 작성 시 존재하지 않은 템플릿
class InvalidSprintException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "5002",
                "reason": "존재(유효)하지 않은 스프린트입니다.",
                "status": "404"
            }
        })

#회고 작성시 존재하지 않은 질문
class InvalidQuestionIDException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "5005",
                "reason": "존재(유효)하지 않은 회고 질문입니다.",
                "status": "404"
            }
        })

#중복된 회고 작성 시도
class DuplicateRetrospectException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "5006",
                "reason": "동일한 스프린트에 대해 중복 작성 불가입니다.",
                "status": "409"
            }
        })

    # 예외 클래스 정의

#회고 목록 조회시 존재하지 않은 프로젝트
class RetrospectProjectNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "2002",
                "reason": "존재하지 않은 프로젝트입니다.",
                "status": "404"
            }
        })

#존재하지 않는 회고록
class NoRetrospectsFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "5007",
                "reason": "요청한 프로젝트에는 작성된 회고록이 없습니다.",
                "status": "404"
            }
        })

#유효하지 않은 프로젝트 ID형식
class InvalidProjectIDFormat(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "2003",
                "reason": "유효하지 않은 프로젝트 ID 형식입니다.",
                "status": "400"
            }
        })

# 존재하지 않은 회고록 ID
class RetrospectNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "5008",
                "reason": "존재하지 않은 회고록 ID입니다.",
                "status": "404"
            }
        })

#유효하지 않은 회고록 ID형식
class InvalidRetrospectIDFormat(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail={
            "success": False,
            "response": None,
            "error": {
                "code": "5009",
                "reason": "유효하지 않은 회고록 ID 형식입니다.",
                "status": "400"
            }
        })