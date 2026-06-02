import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Testing gemini-3.5-flash:")
try:
    model = genai.GenerativeModel("gemini-3.5-flash")
    res = model.generate_content("Hello, respond in one word.")
    print(f"Result: {res.text}")
except Exception as e:
    print(f"Error: {e}")
