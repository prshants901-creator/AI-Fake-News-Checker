import json
import os
import re
import time

from google import genai
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-flash-latest"]

PROMPT = """You are a professional fact-checker. Analyze the claim/news text below.
Use Google Search to verify it against reliable, recent sources when available.

Return ONLY a JSON object (no markdown, no extra text) with exactly these keys:
{{
  "verdict": "REAL" | "FAKE" | "UNVERIFIED",
  "fake_probability": integer 0-100 (chance that the text is fake/misleading),
  "confidence": "low" | "medium" | "high",
  "summary": "2-3 sentence explanation in {lang}",
  "red_flags": ["short bullet", ...],
  "supporting_points": ["short bullet", ...]
}}

Rules:
- If you cannot find reliable evidence either way, use "UNVERIFIED" and a probability near 50.
- Opinions, satire, or partly-true claims should be judged as misleading (higher fake_probability).

TEXT TO CHECK:
\"\"\"{text}\"\"\"
"""


def parse_json(raw: str) -> dict:
    raw = (raw or "").strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        raise ValueError("Valid JSON nahi mila. Model ka jawab tha: " + repr(raw[:150]))
    data = json.loads(match.group(0))
    prob = max(0, min(100, int(float(data.get("fake_probability", 50)))))
    data["fake_probability"] = prob
    data["verdict"] = str(data.get("verdict", "UNVERIFIED")).upper()
    data.setdefault("confidence", "low")
    data.setdefault("summary", "")
    data["red_flags"] = data.get("red_flags") or []
    data["supporting_points"] = data.get("supporting_points") or []
    return data


def _get_sources(resp):
    sources = []
    try:
        chunks = resp.candidates[0].grounding_metadata.grounding_chunks or []
        for c in chunks:
            if c.web and c.web.uri:
                sources.append({"title": c.web.title or c.web.uri, "url": c.web.uri})
    except (AttributeError, IndexError, TypeError):
        pass
    return sources


def _is_retryable(msg: str) -> bool:
    return any(k in msg for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "500", "INTERNAL"))


def check_news(text: str, api_key: str, lang: str = "Hinglish", use_search: bool = True):
    client = genai.Client(api_key=api_key)
    prompt = PROMPT.format(text=text[:6000], lang=lang)

    search_modes = [True, False] if use_search else [False]
    models = list(dict.fromkeys([MODEL] + FALLBACK_MODELS))
    errors = []

    for search in search_modes:
        if search:
            config = types.GenerateContentConfig(
                temperature=0.1,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
        else:
            # Bina search ke JSON format pakka karwa sakte hain
            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            )

        for model in models:
            for attempt in range(2):
                try:
                    resp = client.models.generate_content(
                        model=model, contents=prompt, config=config
                    )
                    result = parse_json(resp.text)
                    result["sources"] = _get_sources(resp)
                    result["model_used"] = model
                    result["search_used"] = search
                    return result
                except Exception as e:
                    msg = str(e)
                    if attempt == 1 or not _is_retryable(msg):
                        errors.append(f"{model} (search={'on' if search else 'off'}): {msg[:250]}")
                    if _is_retryable(msg):
                        time.sleep(2 * (attempt + 1))
                        continue
                    break  # 404, JSON error wagairah: seedha agla model

    raise RuntimeError("Saare models fail hue:\n\n" + "\n\n".join(errors))