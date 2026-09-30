# 🕵️ AI Fake News Checker (Gemini API)

Koi bhi news/claim paste karo -> Gemini (Google Search grounding ke saath) verify karke Real/Fake percentage, red flags aur sources dikhata hai. Dataset ki zarurat nahi.

## Setup
pip install -r requirements.txt
GEMINI_API_KEY ko .env file me daalo (https://aistudio.google.com/apikey)
streamlit run app.py

## How it works
1. User text -> structured fact-check prompt
2. Gemini + Google Search grounding se live verification
3. JSON output parse (verdict, fake %, confidence, red flags)
4. Streamlit UI me percentage, explanation aur source links

## Limitations
- Percentage LLM ka estimate hai, statistically calibrated nahi
- Bahut nayi ya local khabron pe result UNVERIFIED aa sakta hai