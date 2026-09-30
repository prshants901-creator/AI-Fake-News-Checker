import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for m in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest"]:
    try:
        r = client.models.generate_content(model=m, contents="Say hi")
        print("OK  ", m, "->", r.text.strip()[:30])
    except Exception as e:
        print("FAIL", m, "->", str(e)[:150])