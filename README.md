# WeatherGPT AI Service

Standalone FastAPI service for conversational weather intelligence (SIH 2026).

This service is called by the MERN application over HTTP.

## Features (MVP)

- Natural-language weather chat (`POST /chat`)
- Gemini tool calling (location, current weather, forecast)
- English + Hindi auto-detection
- Basic advisories from real weather data
- Health check endpoint

## Setup

1. Create and activate a virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

4. Run:

```bash
uvicorn app.main:app --reload
```

Service: `http://127.0.0.1:8000`

## Quick API

- `GET /health`
- `POST /chat`

## Docs for teammates

- [MERN Integration Guide](docs/MERN_INTEGRATION.md)
- [AI Service Overview](docs/AI_SERVICE_OVERVIEW.md)

## Docker

Build:

```bash
docker build -t weathergpt-ai .
```

Run (PowerShell):

```powershell
docker run --rm -p 8000:8000 `
  -e GEMINI_API_KEY=your_real_key_here `
  -e GEMINI_MODEL=gemini-3.5-flash-lite `
  weathergpt-ai
```

Then test:

- `http://127.0.0.1:8000/health`
- `POST http://127.0.0.1:8000/chat`
