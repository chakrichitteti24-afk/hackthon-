import os

from dotenv import load_dotenv


load_dotenv()

# Chat endpoints need this, but health/session routes should still work locally
# when the key is absent.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
