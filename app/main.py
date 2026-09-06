from fastapi import FastAPI

from app.api.chat import router as chat_router

app = FastAPI(
    title="WeatherGPT AI Service",
    description="Conversational weather AI service for SIH 2026",
    version="0.1.0",
)

app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "WeatherGPT AI service is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "weathergpt-ai",
    }