import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("FAILED: GEMINI_API_KEY not found.")
    exit(1)

print(f"Key loaded (first 6 chars): {api_key[:6]}...")

from google import genai

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Reply with exactly one word: OK",
)

print("Gemini responded:", response.text.strip())
print("SUCCESS: key is valid and authentication works.")
