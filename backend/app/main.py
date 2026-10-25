"""Application factory entrypoint; business logic belongs to M1-M5."""
from fastapi import FastAPI
from app.core.config import APP_NAME, APP_VERSION
from app.api.routes import router

app = FastAPI(title=APP_NAME, version=APP_VERSION, description="Connected M1-M5 resume and job-description skill analysis pipeline")
app.include_router(router)
