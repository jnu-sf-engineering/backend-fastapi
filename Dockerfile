# Python 3.9 slim 버전을 사용하여 이미지 최적화
FROM python:3.12.7-slim

# 작업 디렉터리 설정
WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 애플리케이션 파일 복사
COPY . .

# FastAPI 실행 포트 노출
EXPOSE 8000

# FastAPI 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
