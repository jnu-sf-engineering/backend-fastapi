from fastapi import FastAPI, status
from router import auth, project


app = FastAPI()

# 인증 라우터
app.include_router(auth.router)

# 프로젝트 라우터
app.include_router(project.router)

# API Server Test
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"Hello" : "World"}