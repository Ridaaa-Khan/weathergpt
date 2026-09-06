from typing import Any

from app.services.location import search_location
from app.services.weather import get_current_weather, get_forecast


def execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Run a tool requested by the LLM and return a JSON-serializable result."""
    if name == "search_location":
        result = search_location(args["location_name"])
        if result is None:
            return {
                "error": "Location not found",
                "location_name": args["location_name"],
            }
        return result

    if name == "get_current_weather":
        return get_current_weather(args["latitude"], args["longitude"])

    if name == "get_forecast":
        days = args.get("days", 3)
        return get_forecast(args["latitude"], args["longitude"], days=days)

    return {"error": f"Unknown tool: {name}"}
