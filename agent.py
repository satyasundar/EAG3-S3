"""
Smart shopping assistant. Python prototype.
Run: uv run agent.py
"""

import os
import json
import requests
from google import genai
from dotenv import load_dotenv


# ================================================
# CONFIG
# ================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

MAX_ITERATIONS = 5

print("\n LLM Used: ", GEMINI_MODEL)
client = genai.Client(api_key=GEMINI_API_KEY)

# ================================================
# SIMPLE LLM RUN
# ================================================

# response = client.models.generate_content(model=GEMINI_MODEL, contents="Tell me a joke")
# print(response.text)

# ================================================
# THINKING LLM RUN
# ================================================
# from google.genai import types

# response = client.models.generate_content(
#     model=GEMINI_MODEL,
#     contents="What is 2 raised to the pwoer of 5?",
#     config=types.GenerateContentConfig(
#         thinking_config=types.ThinkingConfig(include_thoughts=True)
#     ),
# )

# print("\n === FINAL ANSWER ====")
# print(response.text)

# ================================================
# TOOLS - these are what agent can call
# ================================================
