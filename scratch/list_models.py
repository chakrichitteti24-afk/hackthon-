import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:6]}...{api_key[-6:] if len(api_key) > 12 else ''}")

genai.configure(api_key=api_key)

try:
    print("Listing models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name} ({m.display_name})")
except Exception as e:
    print(f"Error listing models: {e}")

# Test generating content with gemini-1.5-flash
print("\nTesting gemini-1.5-flash:")
try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    res = model.generate_content("Hello, respond in one word.")
    print(f"Result: {res.text}")
except Exception as e:
    print(f"Error with gemini-1.5-flash: {e}")

# Test generating content with gemini-2.5-flash
print("\nTesting gemini-2.5-flash:")
try:
    model = genai.GenerativeModel("gemini-2.5-flash")
    res = model.generate_content("Hello, respond in one word.")
    print(f"Result: {res.text}")
except Exception as e:
    print(f"Error with gemini-2.5-flash: {e}")
