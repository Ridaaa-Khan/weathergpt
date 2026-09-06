from google.genai import types

TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="search_location",
        description=(
            "Convert a place name into geographic coordinates. "
            "Use this when the user mentions a city or place and you need lat/lon."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "location_name": types.Schema(
                    type=types.Type.STRING,
                    description="City or place name, e.g. Lucknow",
                ),
            },
            required=["location_name"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_current_weather",
        description=(
            "Get the current weather for a location using latitude and longitude. "
            "Use this for questions about weather right now / today currently."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "latitude": types.Schema(
                    type=types.Type.NUMBER,
                    description="Latitude in decimal degrees",
                ),
                "longitude": types.Schema(
                    type=types.Type.NUMBER,
                    description="Longitude in decimal degrees",
                ),
            },
            required=["latitude", "longitude"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_forecast",
        description=(
            "Get a weather forecast for upcoming days using latitude and longitude. "
            "Use this for questions about tomorrow, later today in a future sense, "
            "this week, or whether it will rain/be hot on a future day."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "latitude": types.Schema(
                    type=types.Type.NUMBER,
                    description="Latitude in decimal degrees",
                ),
                "longitude": types.Schema(
                    type=types.Type.NUMBER,
                    description="Longitude in decimal degrees",
                ),
                "days": types.Schema(
                    type=types.Type.INTEGER,
                    description="Number of forecast days from 1 to 7. Default 3.",
                ),
            },
            required=["latitude", "longitude"],
        ),
    ),
]


def get_gemini_tools() -> list[types.Tool]:
    return [types.Tool(function_declarations=TOOL_DECLARATIONS)]
