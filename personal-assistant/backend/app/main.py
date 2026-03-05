from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from .api import endpoints
from .core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Personal Assistant Brain is Active", "status": "running", "docs_url": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
