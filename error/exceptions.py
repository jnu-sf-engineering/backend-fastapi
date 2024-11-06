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
class DuplicateProjectNameException(HTTPException):
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