import html
import os

import streamlit as st
from dotenv import load_dotenv

from checker import check_news

load_dotenv()
st.set_page_config(page_title="AI Fake News Checker", page_icon="🕵️", layout="centered")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
html, body, [class*="css"], .stMarkdown, p, label { font-family: 'Poppins', sans-serif; }
.stApp { background: radial-gradient(circle at 15% 10%, #1e1b4b 0%, #0b1020 45%, #050814 100%); }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.92); border-right: 1px solid rgba(255,255,255,0.08); }

.hero { text-align: center; padding: 1.2rem 0 0.4rem; animation: rise .8s ease both; }
.hero .icon { font-size: 3.2rem; display: inline-block; animation: float 3s ease-in-out infinite; }
.hero h1 {
  font-size: 2.5rem; font-weight: 800; margin: 0.2rem 0; padding: 0;
  background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #60a5fa);
  background-size: 300% auto; -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent; animation: shine 6s linear infinite;
}
.hero p { color: #94a3b8; font-size: 1rem; margin-top: 0.2rem; }
@keyframes shine { to { background-position: 300% center; } }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
@keyframes rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fill { from { stroke-dashoffset: 339.3; } }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 var(--glow); } 50% { box-shadow: 0 0 22px 4px var(--glow); } }

.section-label { color: #cbd5e1; font-weight: 600; margin: 1.1rem 0 0.3rem; }

.stTextArea textarea {
  background: rgba(255,255,255,0.05) !important; color: #e2e8f0 !important;
  border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 16px !important;
  transition: all .25s ease;
}
.stTextArea textarea:focus {
  border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129,140,248,0.25) !important;
}

.stButton > button {
  border-radius: 14px; font-weight: 600; border: 1px solid rgba(255,255,255,0.12);
  transition: all .25s ease; width: 100%;
}
.stButton > button:hover { transform: translateY(-3px) scale(1.02); }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
  background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); border: none; color: white;
  padding: 0.65rem 1rem; font-size: 1.05rem; box-shadow: 0 8px 24px rgba(139,92,246,0.35);
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
  box-shadow: 0 12px 32px rgba(236,72,153,0.5);
}
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"] {
  background: rgba(255,255,255,0.06); color: #cbd5e1; font-size: 0.85rem;
}
.stButton > button[kind="secondary"]:hover, .stButton > button[data-testid="stBaseButton-secondary"]:hover {
  background: rgba(129,140,248,0.2); border-color: #818cf8; color: white;
}

.result-card {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 22px; padding: 1.5rem; margin-top: 1.2rem;
  backdrop-filter: blur(12px); animation: rise .6s ease both;
}
.top-row { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }
.gauge { position: relative; width: 150px; height: 150px; flex-shrink: 0; }
.gauge svg { transform: rotate(-90deg); }
.gauge .track { stroke: rgba(255,255,255,0.1); }
.gauge .bar { stroke-dasharray: 339.3; animation: fill 1.4s cubic-bezier(.2,.8,.2,1) both; stroke-linecap: round; }
.gauge .num {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; color: white;
}
.gauge .num b { font-size: 2rem; line-height: 1; }
.gauge .num span { font-size: 0.7rem; color: #94a3b8; margin-top: 4px; }
.verdict-box { flex: 1; min-width: 200px; }
.badge {
  display: inline-block; padding: 0.35rem 1rem; border-radius: 999px; font-weight: 800;
  letter-spacing: 1px; color: white; animation: pulse 2.2s infinite;
}
.meta { color: #94a3b8; font-size: 0.8rem; margin-top: 0.6rem; }
.summary { color: #e2e8f0; margin-top: 0.8rem; line-height: 1.6; }

.stats { display: flex; gap: 0.8rem; margin-top: 1.2rem; }
.stat { flex: 1; border-radius: 16px; padding: 0.8rem; text-align: center; transition: transform .25s ease; }
.stat:hover { transform: translateY(-4px); }
.stat b { font-size: 1.6rem; display: block; }
.stat span { font-size: 0.8rem; opacity: 0.85; }
.stat.real { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.stat.fake { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }

.chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.4rem; }
.chip { padding: 0.4rem 0.8rem; border-radius: 12px; font-size: 0.85rem; transition: transform .2s ease; }
.chip:hover { transform: scale(1.05); }
.chip.red { background: rgba(239,68,68,0.14); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }
.chip.green { background: rgba(34,197,94,0.14); color: #86efac; border: 1px solid rgba(34,197,94,0.3); }
.src a { color: #93c5fd; text-decoration: none; }
.src a:hover { text-decoration: underline; }
.src div { margin-top: 0.3rem; font-size: 0.9rem; }
.disclaimer { text-align: center; color: #64748b; font-size: 0.75rem; margin-top: 2rem; }
</style>
"""

EXAMPLES = {
    "🚀 ISRO": "ISRO successfully landed Chandrayaan-3 near the Moon's south pole in August 2023.",
    "🏧 ATM ban": "The government has announced that all ATMs will be shut down permanently from tonight.",
    "💸 WhatsApp offer": "Forward this message to 10 people on WhatsApp and get 500 rupees in your account.",
}


def set_example(t: str):
    st.session_state.claim = t


def esc(x) -> str:
    return html.escape(str(x))


def render_result(r: dict):
    fake = r["fake_probability"]
    real = 100 - fake
    if fake >= 65:
        color = "#ef4444"
    elif fake <= 35:
        color = "#22c55e"
    else:
        color = "#f59e0b"
    offset = 339.3 * (1 - fake / 100)

    parts = [
        '<div class="result-card">',
        '<div class="top-row">',
        '<div class="gauge">',
        '<svg width="150" height="150" viewBox="0 0 120 120">',
        '<circle class="track" cx="60" cy="60" r="54" fill="none" stroke-width="10"/>',
        f'<circle class="bar" cx="60" cy="60" r="54" fill="none" stroke-width="10" '
        f'stroke="{color}" style="stroke-dashoffset:{offset:.1f}"/>',
        '</svg>',
        f'<div class="num"><b>{fake}%</b><span>FAKE</span></div>',
        '</div>',
        '<div class="verdict-box">',
        f'<span class="badge" style="background:{color};--glow:{color}88">{esc(r["verdict"])}</span>',
        f'<div class="meta">Confidence: {esc(r["confidence"])} &nbsp;|&nbsp; '
        f'Model: {esc(r.get("model_used", "-"))} &nbsp;|&nbsp; '
        f'Search: {"on" if r.get("search_used") else "off"}</div>',
        f'<div class="summary">{esc(r["summary"])}</div>',
        '</div>',
        '</div>',
        '<div class="stats">',
        f'<div class="stat real"><b>{real}%</b><span>🟢 Real</span></div>',
        f'<div class="stat fake"><b>{fake}%</b><span>🔴 Fake</span></div>',
        '</div>',
    ]
    if r["red_flags"]:
        parts.append('<div class="section-label">🚩 Red flags</div><div class="chips">')
        parts += [f'<span class="chip red">{esc(x)}</span>' for x in r["red_flags"]]
        parts.append('</div>')
    if r["supporting_points"]:
        parts.append('<div class="section-label">✅ Supporting points</div><div class="chips">')
        parts += [f'<span class="chip green">{esc(x)}</span>' for x in r["supporting_points"]]
        parts.append('</div>')
    if r["sources"]:
        parts.append('<div class="section-label">🔗 Sources</div><div class="src">')
        parts += [f'<div><a href="{esc(s["url"])}" target="_blank">{esc(s["title"])}</a></div>'
                  for s in r["sources"]]
        parts.append('</div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


st.markdown(CSS, unsafe_allow_html=True)
st.markdown(
    '<div class="hero"><div class="icon">🕵️</div><h1>AI Fake News Checker</h1>'
    '<p>Paste any news or claim and AI will tell you instantly if it is real or fake</p></div>',
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

api_key = os.getenv("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API key", type="password")
lang = st.sidebar.selectbox("Explanation language", ["English", "Hindi", "Hinglish"])
use_search = st.sidebar.toggle("Verify with Google Search", value=False)
st.sidebar.caption("Turning search on gives better results, but uses up the free quota faster.")

st.markdown('<div class="section-label">⚡ Try an example</div>', unsafe_allow_html=True)
cols = st.columns(len(EXAMPLES))
for col, (label, t) in zip(cols, EXAMPLES.items()):
    col.button(label, key=f"ex_{label}", on_click=set_example, args=(t,))

st.markdown('<div class="section-label">📝 News / claim</div>', unsafe_allow_html=True)
text = st.text_area("claim", key="claim", height=160, label_visibility="collapsed",
                    placeholder="e.g. The government announced that all ATMs will shut down from tomorrow...")

if st.button("🔍 Check", type="primary"):
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar first.")
    elif len(text.strip()) < 15:
        st.warning("Please enter a longer text (at least one full sentence).")
    else:
        r = None
        with st.spinner("AI is verifying..."):
            try:
                r = check_news(text, api_key, lang, use_search)
            except Exception as e:
                st.error("Gemini did not respond. See the reason below:")
                st.code(str(e))
        if r:
            render_result(r)
            st.session_state.history.insert(0, {
                "text": text.strip()[:70], "fake": r["fake_probability"], "verdict": r["verdict"]})

if st.session_state.history:
    with st.expander(f"🕘 Previous checks ({len(st.session_state.history)})"):
        for h in st.session_state.history[:8]:
            icon = "🔴" if h["fake"] >= 65 else ("🟢" if h["fake"] <= 35 else "🟠")
            st.markdown(f"{icon} **{h['verdict']}** ({h['fake']}% fake) - {h['text']}...")

st.markdown('<div class="disclaimer">⚠️ This is an AI estimate, not a calibrated probability. '
            'Always confirm important information from official sources.</div>',
            unsafe_allow_html=True)