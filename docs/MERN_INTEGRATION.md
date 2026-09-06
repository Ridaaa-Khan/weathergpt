# MERN Integration Guide — WeatherGPT AI Service

## What this service is

WeatherGPT AI is a standalone FastAPI service.

- It understands natural-language weather questions (English/Hindi)
- It uses Gemini tool calling
- It fetches real location/weather data from Open-Meteo
- It returns a short natural-language answer

It does **not** handle:
- login/auth
- chat history storage
- MongoDB
- UI

Those stay in the MERN app.

## Base URL

Local:

`http://127.0.0.1:8000`

## Start the AI service

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then put GEMINI_API_KEY in .env
uvicorn app.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`

Interactive API docs: `http://127.0.0.1:8000/docs`

## Chat API

### Endpoint

`POST /chat`  
Header: `Content-Type: application/json`

### Request

```json
{
  "message": "Will it rain tomorrow in Lucknow?",
  "location": {
    "lat": 26.8467,
    "lon": 80.9462
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `message` | Yes | User text (English or Hindi). Min length 1. |
| `location` | No | Device/user coordinates from the client app |
| `location.lat` | If location sent | Latitude |
| `location.lon` | If location sent | Longitude |

**Do not send a language field.** Language is auto-detected from `message`.

### Success response

```json
{
  "response": "Rain is likely tomorrow in Lucknow. Carry an umbrella.",
  "language": "en",
  "status": "ok"
}
```

| Field | Meaning |
|-------|---------|
| `response` | Text to show in chat UI |
| `language` | `"en"` or `"hi"` |
| `status` | `"ok"` on success |

### Validation error example

Empty `message` → HTTP `422`.

### AI unavailable example

Gemini quota/outage → HTTP `503` with an error payload.

## Location behavior (important)

Priority:

1. Place name in the user message (e.g. Lucknow)
2. Else `location.lat` / `location.lon` from client
3. Else AI asks: which location to check?

## Example Node.js call

```js
const res = await fetch("http://127.0.0.1:8000/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "Will it rain tomorrow in Lucknow?",
    location: { lat: 26.8467, lon: 80.9462 },
  }),
});

const data = await res.json();
if (!res.ok) {
  // handle data.error / validation errors
} else {
  // show data.response in UI
  // optional: use data.language
}
```

## Ownership split

| MERN team | AI service (this repo) |
|-----------|-------------------------|
| UI / UX | `/chat`, `/health` |
| Auth / users | Gemini + tool calling |
| Chat history DB | Location + weather APIs |
| App routing | EN/HI response behavior |

## What the AI service currently supports

- Current weather
- Forecast
- Location search/geocoding
- Natural-language questions
- Tool calling
- English + Hindi
- Basic advisories

## Planned teammate extensions later

Can be added as new tools without changing the basic `/chat` request shape:

- IMD warnings
- Severe-weather risk
- Farmer advisory
- Voice input/output (client-side or extra service)

## Notes / limits

- Free-tier Gemini keys can hit rate limits (`429`/`503`)
- Weather facts come from APIs; the LLM should not invent weather
- Service is mostly stateless; store history in MERN if needed
