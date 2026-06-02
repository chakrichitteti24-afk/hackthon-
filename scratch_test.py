import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import config
config.GEMINI_API_KEY = "mock_gemini_key"
config.GROQ_API_KEY = "mock_groq_key"

from agents import sales_agent
print("Direct import:", sales_agent.GEMINI_API_KEY)

# Let's inspect if sales_agent.GEMINI_API_KEY can be mutated
sales_agent.GEMINI_API_KEY = "changed_key"
print("Mutated:", sales_agent.GEMINI_API_KEY)
