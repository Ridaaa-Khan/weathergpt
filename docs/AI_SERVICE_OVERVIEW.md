# WeatherGPT AI — Overview

## Architecture

```text
MERN app
   │  POST /chat
   ▼
FastAPI AI service
   ├── Gemini (understand question, choose tools, write answer)
   ├── Location API (Open-Meteo Geocoding)
   └── Weather API (Open-Meteo)
```

## Request flow

1. User asks a weather question in the MERN UI
2. MERN sends `{ message, location? }` to AI service
3. Gemini may call tools:
   - `search_location`
   - `get_current_weather`
   - `get_forecast`
4. Python executes tools against real APIs
5. Gemini returns a natural answer
6. AI service responds with `{ response, language, status }`

## Design principles

- LLM is not a weather model
- Weather facts come from meteorological/weather APIs
- Location logic is separate from weather logic
- Tools are separate from HTTP routes
- Easy to add teammate tools later
