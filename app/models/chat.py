from typing import Literal, Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float = Field(..., description="Latitude in decimal degrees")
    lon: float = Field(..., description="Longitude in decimal degrees")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's natural-language message")
    location: Optional[Location] = Field(
        default=None,
        description="Optional device/user coordinates from the client",
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="Assistant reply for the UI")
    language: Literal["en", "hi"] = Field(
        ...,
        description="Detected reply language code",
    )
    status: Literal["ok"] = "ok"