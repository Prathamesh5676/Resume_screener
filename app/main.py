from fastapi import FastAPI

from app.api.routes import router
from app.core.database import engine
from app.models.evaluation import Base

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router)

@app.get("/")
async def health_check():
    return {"status": "ok"}