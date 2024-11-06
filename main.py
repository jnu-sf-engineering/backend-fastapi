from fastapi import FastAPI, status
from router import auth


app = FastAPI()

# 인증 라우터
app.include_router(auth.router)


# API Server Test
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"Hello" : "World"}