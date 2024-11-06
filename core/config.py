# 환경변수 설정
from dotenv import load_dotenv
import os

# APP_ENV 환경 변수에 따라 개발 / 운영 환경 설정
"""
개발 환경 : export APP_ENV=dev
운영 환경 : export APP_ENV=prod
"""
env_file = f".env.{os.getenv('APP_ENV', 'dev')}"

load_dotenv(dotenv_path=env_file)

class Settings:

    # MySQL
    RDS_DATABASE_ENDPOINT = os.getenv("RDS_DATABASE_ENDPOINT")
    RDS_DATABASE_USERNAME = os.getenv("RDS_DATABASE_USERNAME")
    RDS_DATABASE_PASSWORD = os.getenv("RDS_DATABASE_PASSWORD")
    RDS_PORT = os.getenv("RDS_PORT")
    RDS_DB_NAME = os.getenv("RDS_DB_NAME")
    DB_URL=f"mysql+pymysql://{RDS_DATABASE_USERNAME}:{RDS_DATABASE_PASSWORD}@{RDS_DATABASE_ENDPOINT}:{RDS_PORT}/{RDS_DB_NAME}?charset=utf8mb4"
    
settings = Settings()
