from typing import Any

import httpx

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# Open-Meteo weather codes → short human-readable labels
WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm (possible light hail)",
    99: "Thunderstorm (possible heavy hail)",
}


def _describe_weather_code(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return WEATHER_CODE_MAP.get(code, f"Unknown weather code ({code})")


def get_current_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """
    Fetch current weather for the given coordinates from Open-Meteo.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "rain",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
            ]
        ),
        "timezone": "auto",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return {"error": "Weather service unavailable", "detail": str(exc)}

    if isinstance(data, dict) and data.get("error"):
        return data

    current = data.get("current") or {}
    units = data.get("current_units") or {}
    weather_code = current.get("weather_code")

    return {
        "latitude": data.get("latitude", latitude),
        "longitude": data.get("longitude", longitude),
        "timezone": data.get("timezone"),
        "temperature_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "rain_mm": current.get("rain"),
        "weather_code": weather_code,
        "condition": _describe_weather_code(weather_code),
        "cloud_cover_percent": current.get("cloud_cover"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "wind_direction_deg": current.get("wind_direction_10m"),
        "units": {
            "temperature": units.get("temperature_2m", "°C"),
            "precipitation": units.get("precipitation", "mm"),
            "wind_speed": units.get("wind_speed_10m", "km/h"),
        },
    }


def get_forecast(
    latitude: float,
    longitude: float,
    days: int = 3,
) -> dict[str, Any]:
    """
    Fetch a short-range forecast for the given coordinates.
    `days` is clamped between 1 and 7 for the MVP.
    """
    days = max(1, min(int(days), 7))

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ",".join(
            [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
            ]
        ),
        "hourly": ",".join(
            [
                "temperature_2m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
            ]
        ),
        "forecast_days": days,
        "timezone": "auto",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(WEATHER_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return {"error": "Weather service unavailable", "detail": str(exc)}

    if isinstance(data, dict) and data.get("error"):
        return data

    daily = data.get("daily") or {}
    hourly = data.get("hourly") or {}

    daily_forecast = []
    dates = daily.get("time") or []
    for i, date in enumerate(dates):
        code = (daily.get("weather_code") or [None])[i]
        daily_forecast.append(
            {
                "date": date,
                "weather_code": code,
                "condition": _describe_weather_code(code),
                "temp_max_c": (daily.get("temperature_2m_max") or [None])[i],
                "temp_min_c": (daily.get("temperature_2m_min") or [None])[i],
                "precipitation_mm": (daily.get("precipitation_sum") or [None])[i],
                "precipitation_probability_max": (
                    daily.get("precipitation_probability_max") or [None]
                )[i],
                "wind_speed_max_kmh": (daily.get("wind_speed_10m_max") or [None])[i],
            }
        )

    # Keep a compact hourly sample (first 24 hours) so responses stay readable.
    hourly_forecast = []
    hourly_times = hourly.get("time") or []
    for i, timestamp in enumerate(hourly_times[:24]):
        code = (hourly.get("weather_code") or [None])[i]
        hourly_forecast.append(
            {
                "time": timestamp,
                "temperature_c": (hourly.get("temperature_2m") or [None])[i],
                "precipitation_mm": (hourly.get("precipitation") or [None])[i],
                "precipitation_probability": (
                    hourly.get("precipitation_probability") or [None]
                )[i],
                "weather_code": code,
                "condition": _describe_weather_code(code),
            }
        )

    return {
        "latitude": data.get("latitude", latitude),
        "longitude": data.get("longitude", longitude),
        "timezone": data.get("timezone"),
        "forecast_days": days,
        "daily": daily_forecast,
        "hourly_next_24h": hourly_forecast,
    }
