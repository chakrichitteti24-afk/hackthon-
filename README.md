OmniFlow AI Backend
===================

This repository contains the FastAPI backend for OmniFlow AI — a multi-agent
customer intelligence platform with smart routing, web intelligence, and
dual-LLM orchestration.

Installation
------------

1. Create and activate a Python virtual environment (Windows example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and populate API keys.

Running (development)
---------------------

Start the FastAPI backend on port 8001 (frontend expects backend at :8001):

```bash
# from the omniflow-backend directory
uvicorn main:app --reload --port 8001 --host 0.0.0.0
```

The frontend runs separately (port 5174 by default). Ensure both are started
for end-to-end testing.

Notes
-----
- The backend uses Groq and optionally Cerebras for LLM calls. Provide API
  keys in the `.env` file. Web grounding now uses Wikipedia (stable,
  factual, low-latency) instead of an external news/search provider.
- For production deployment replace the in-memory session store with a
  persistent database.