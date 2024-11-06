from fastapi import FastAPI, status

app = FastAPI()


# API Server Test
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"Hello" : "World"}