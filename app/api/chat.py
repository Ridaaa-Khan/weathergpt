from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.gemini import chat_with_tools

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    location = None
    if request.location is not None:
        location = {
            "lat": request.location.lat,
            "lon": request.location.lon,
        }

    reply, language = chat_with_tools(request.message, location=location)
    return ChatResponse(
        response=reply,
        language=language,  # "en" or "hi"
        status="ok",
    )