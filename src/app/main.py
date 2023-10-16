import uvicorn
from fastapi import FastAPI

from app.routers import router

app = FastAPI()

app.include_router(router)


@app.get("/")
async def index():
    return "Hello, world!"


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)
