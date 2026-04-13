from fastapi import FastAPI

from app.api.routes import router

app = FastAPI()
app.include_router(router)

@app.get("/")
async def health_check():
    return {"status": "ok"}