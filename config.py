import os
from typing import Optional

from dotenv import load_dotenv


load_dotenv()

# API keys (may be None in local dev)
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
WIKI_LANGUAGE = os.getenv("WIKI_LANGUAGE", "en")
WIKI_USER_AGENT = os.getenv("WIKI_USER_AGENT", "OmniFlowAI/1.0")

# Optional settings
DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-3.5-flash")
DEFAULT_GROQ_MODEL = os.getenv("DEFAULT_GROQ_MODEL", "llama-3.1-8b-instant")

