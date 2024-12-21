from fastapi import FastAPI
from .routers import review

app = FastAPI()

app.include_router(review.router)


@app.get("/")
async def toor():
    return {"message": "Hello World"}
