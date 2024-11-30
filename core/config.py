# 환경변수 설정
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # MySQL
    RDS_DATABASE_ENDPOINT = os.getenv("RDS_DATABASE_ENDPOINT")
    RDS_DATABASE_USERNAME = os.getenv("RDS_DATABASE_USERNAME")
    RDS_DATABASE_PASSWORD = os.getenv("RDS_DATABASE_PASSWORD")
    RDS_PORT = os.getenv("RDS_PORT")
    RDS_DB_NAME = os.getenv("RDS_DB_NAME")
    DB_URL=f"mysql+pymysql://{RDS_DATABASE_USERNAME}:{RDS_DATABASE_PASSWORD}@{RDS_DATABASE_ENDPOINT}:{RDS_PORT}/{RDS_DB_NAME}?charset=utf8mb4"


settings = Settings()
