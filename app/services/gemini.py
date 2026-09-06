import os
from datetime import date
from pathlib import Path
from typing import Any, Optional
from app.core.exceptions import GeminiUnavailableError
from app.services.language import detect_language

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError

from app.tools.definitions import get_gemini_tools
from app.tools.executor import execute_tool

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Create a .env file and set GEMINI_API_KEY."
    )

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are WeatherGPT, a helpful weather assistant.

Rules:
1. NEVER invent weather facts. Use tools for real data.
2. Language:
   - Reply in the SAME language as the user (English or Hindi only for MVP).
   - If the user switches language, switch with them.
3. Choose tools carefully:
   - get_current_weather: weather right now / currently.
   - get_forecast: tomorrow, upcoming days, "will it rain", evening/later plans.
4. Date understanding:
   - Use the provided current date to interpret today/tomorrow.
   - For tomorrow questions, answer tomorrow from forecast data.
5. Location handling:
   - If the user named a place, call search_location first, then the weather tool.
   - If client coordinates are provided and no place is named, use those coordinates.
   - If there is no place name and no coordinates, ask which location to check
     in the user's language.
6. Answer style:
   - 2-4 short natural sentences.
   - First answer the user's question clearly.
   - Then, when useful, add ONE short practical advisory line based on the data.
7. Basic advisory examples (only if supported by tool data):
   - Rain / high rain chance: suggest carrying an umbrella or raincoat.
   - Very hot conditions: suggest water, shade, or avoiding peak afternoon heat.
   - Strong wind: suggest caution for outdoor / travel plans.
   - Pleasant/clear weather: optional light note is fine; do not force advice.
8. Advisory limits (important):
   - Do NOT invent floods, disasters, or extreme certainty.
   - Do NOT give medical, legal, or advanced farming prescriptions.
   - Do NOT claim "definitely" when the data only shows likelihood.
   - Keep advice basic and cautious.
   - Weather codes can be coarse. If a condition says "possible hail",
     mention hail only as a possibility, and focus on rain/thunderstorms
     unless the user asks specifically about hail.
9. If a tool fails or a place is not found, say so honestly.
""".strip()


def ask_gemini(prompt: str) -> str:
    """Simple text-only call (no tools). Useful for basic checks."""
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        ),
    )
    return response.text

def _build_user_payload(
    message: str,
    location: Optional[dict[str, float]] = None,
    language: str = "en",
) -> str:
    """Attach useful context so Gemini interprets the question better."""
    language_name = "Hindi" if language == "hi" else "English"
    parts = [
        message.strip(),
        "",
        f"[Current date: {date.today().isoformat()}]",
        f"[Detected language: {language} ({language_name})]",
        f"[Respond in {language_name}.]",
        "[Interpret relative words like today/tomorrow using the current date above.]",
    ]

    if location is not None:
        parts.append(
            f"[Client-provided coordinates: lat={location['lat']}, lon={location['lon']}]"
        )

    return "\n".join(parts)


def chat_with_tools(
    message: str,
    location: Optional[dict[str, float]] = None,
    max_tool_rounds: int = 5,
) -> tuple[str, str]:
    """
    Chat with Gemini using explicit tool calling.
    Returns: (reply_text, detected_language)
    """
    language = detect_language(message)
    user_text = _build_user_payload(message, location=location, language=language)

    try:
        chat = client.chats.create(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=get_gemini_tools(),
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True  # we handle tools ourselves so we can learn the flow
                ),
            ),
        )

        response = chat.send_message(user_text)

        for _ in range(max_tool_rounds):
            function_calls = response.function_calls
            if not function_calls:
                break

            function_response_parts: list[types.Part] = []
            for fc in function_calls:
                print(f"[tool call] {fc.name}({dict(fc.args)})")  # visible learning aid
                result: dict[str, Any] = execute_tool(fc.name, dict(fc.args))
                function_response_parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response={"result": result},
                    )
                )

            response = chat.send_message(function_response_parts)

        if not response.text:
            return (
                "I could not generate a weather response right now. Please try again.",
                language,
            )

        return response.text, language

    except ClientError as exc:
        print(
            f"[gemini error] code={exc.code} status={exc.status} message={exc.message}"
        )
        if exc.code == 429:
            raise GeminiUnavailableError(
                "The weather AI is temporarily rate-limited. Please wait about a minute and try again."
            ) from exc
        raise GeminiUnavailableError() from exc
