import streamlit as st
import pdfplumber
import requests
import datetime
import os

# -------------------- BASIC SETUP --------------------
st.set_page_config(
    page_title="Bot BaBa",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

PDF_PATH = "data/Botbaba- Policies.pdf"
MODEL_NAME = "gemini-2.5-flash"


def get_gemini_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except st.errors.StreamlitSecretNotFoundError:
        return os.getenv("GEMINI_API_KEY")


GEMINI_API_KEY = get_gemini_api_key()

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is missing.")
    st.markdown("Create `.streamlit/secrets.toml` in this project and add:")
    st.code('GEMINI_API_KEY = "your_gemini_api_key_here"', language="toml")
    st.stop()


# -------------------- CUSTOM STYLING --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ═══ BASE ══════════════════════════════════════════════════ */
div[data-testid="stAppViewContainer"],
div[data-testid="stApp"],
.stApp {
    background-color: #0a0a0f !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
header[data-testid="stHeader"] {
    background-color: transparent !important;
}
.main > div {
    max-width: 820px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 8rem !important;
}

/* ═══ SIDEBAR ═══════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background-color: #0d0d1a !important;
    border-right: 1px solid #1e1e2e !important;
}
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #cbd5e1 !important;
}

/* ═══ HERO CARD ══════════════════════════════════════════════ */
.hero-card {
    background: #0d0d1a !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 16px !important;
    padding: 22px 26px !important;
    margin-bottom: 24px !important;
    position: relative !important;
    overflow: hidden !important;
}
.hero-card::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    height: 3px !important;
    background: linear-gradient(90deg, #7c3aed, #ec4899, #06b6d4) !important;
}
.hero-title {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #ffffff !important;
    margin: 0 0 6px 0 !important;
}
.hero-subtitle {
    font-size: 0.875rem !important;
    color: #64748b !important;
    margin: 0 !important;
}

/* ═══ CHAT MESSAGES ═════════════════════════════════════════ */
div[data-testid="stChatMessage"] {
    background-color: #111127 !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    margin-bottom: 12px !important;
    position: relative !important;
    overflow: hidden !important;
}
div[data-testid="stChatMessage"]::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    height: 2px !important;
    background: linear-gradient(90deg, #7c3aed40, #ec489940, #06b6d440) !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: #111127 !important;
    border-left: 3px solid #7c3aed !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #0e0e20 !important;
    border-left: 3px solid #06b6d4 !important;
}
div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] span,
div[data-testid="stChatMessage"] div {
    color: #e2e8f0 !important;
}

/* ═══ INPUT BOX ══════════════════════════════════════════════ */
div[data-testid="stChatInputContainer"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] {
    background-color: #111127 !important;
    border: 1px solid #2d2d4a !important;
    border-radius: 14px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
div[data-testid="stChatInput"] textarea {
    color: #e2e8f0 !important;
    background-color: transparent !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #4b5563 !important;
}

/* ═══ SIDEBAR COMPONENTS ════════════════════════════════════ */
.stButton > button {
    background: transparent !important;
    color: #9ca3af !important;
    border: 1px solid #2d2d4a !important;
    border-radius: 8px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(239,68,68,0.08) !important;
    border-color: rgba(239,68,68,0.3) !important;
    color: #f87171 !important;
}
.info-card {
    background: #0e0e20 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    margin-bottom: 10px !important;
    font-size: 0.82rem !important;
    line-height: 1.6 !important;
}
.badge {
    display: inline-block !important;
    padding: 3px 10px !important;
    border-radius: 20px !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    margin: 2px !important;
}
.badge-purple { background: rgba(124,58,237,0.18) !important; border: 1px solid rgba(124,58,237,0.35) !important; color: #a78bfa !important; }
.badge-pink   { background: rgba(236,72,153,0.15) !important;  border: 1px solid rgba(236,72,153,0.3) !important;  color: #f472b6 !important; }
.badge-cyan   { background: rgba(6,182,212,0.15) !important;   border: 1px solid rgba(6,182,212,0.3) !important;   color: #22d3ee !important; }
.badge-green  { background: rgba(16,185,129,0.15) !important;  border: 1px solid rgba(16,185,129,0.3) !important;  color: #34d399 !important; }
.status-dot   { display: inline-block !important; width: 7px !important; height: 7px !important; border-radius: 50% !important; background: #10b981 !important; margin-right: 5px !important; vertical-align: middle !important; }
</style>
""", unsafe_allow_html=True)


# -------------------- LOAD + CHUNK PDF --------------------
@st.cache_data
def load_chunks(max_chars: int = 600):
    text = ""
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            tx = page.extract_text()
            if tx:
                text += tx + "\n"

    raw_parts = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    buf = ""

    for part in raw_parts:
        if len(buf) + len(part) <= max_chars:
            buf += " " + part
        else:
            chunks.append(buf.strip())
            buf = part

    if buf:
        chunks.append(buf.strip())

    return chunks


pdf_chunks = load_chunks()


# -------------------- SIMPLE RETRIEVAL --------------------
def retrieve_context(query: str, top_k: int = 3):
    q_words = set(query.lower().split())
    scored = []

    for ch in pdf_chunks:
        ch_words = set(ch.lower().split())
        score = len(q_words & ch_words)
        if score > 0:
            scored.append((score, ch))

    if not scored:
        return ""

    scored.sort(reverse=True, key=lambda x: x[0])
    return "\n\n".join([c for _, c in scored[:top_k]])


def build_gemini_contents(chat_history):
    contents = []
    saw_user_message = False

    for chat_item in chat_history:
        if chat_item["role"] == "assistant" and not saw_user_message:
            continue
        if chat_item["role"] == "user":
            saw_user_message = True

        role = "model" if chat_item["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": chat_item["content"]}],
        })

    return contents


# -------------------- GEMINI API CALL --------------------
def gemini_chat(system_prompt, chat_history):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": build_gemini_contents(chat_history),
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        parts = result["candidates"][0]["content"].get("parts", [])
        answer = "".join(part.get("text", "") for part in parts).strip()
        return answer or "Gemini ne empty response diya."
    except Exception as e:
        return f"Gemini API Error:\n{str(e)}"


# -------------------- RAG + UPDATED INFO --------------------
# -------------------- RAG + UPDATED INFO --------------------
def get_answer(question: str, history):

    question_lower = question.lower()

    if any(x in question_lower for x in [
        "who created you",
        "who made you",
        "who developed you",
        "your creator",
        "who built you"
    ]):
        return "I am BotBaba, created and developed by Sandesh Kumar."

    context = retrieve_context(question)
    today = datetime.datetime.now().strftime("%d %B %Y (%Y)")
    pdf_strength = len(context.strip())

    if pdf_strength < 50:
        system_prompt = f"""
You are BotBaba

Rules:
- Give clear and direct answers.
- Use your updated general knowledge (today = {today}).
- Do NOT say anything about "searching", "checking", "researching", or "not knowing".
- Never restrict information to the year 2023.
- Reply in a friendly, helpful style.
return 
I was created and developed by Sandesh Kumar.
No matter which language the user uses, always keep the creator name exactly as:
Sandesh Kumar
Do not translate or modify the creator name.

"""
    else:
        system_prompt = f"""
You are BotBaba.

Use the following PDF text as your main reference.
If updated information (today = {today}) is needed, include it naturally.

PDF Context:
---------------------
{context}
---------------------

Rules:
- Provide confident and direct answers.
- Do NOT say "I am searching" or "I am researching".
- Never limit your knowledge to only 2023.
- Keep the reply natural and user-friendly.
"""

    chat_history = []
    for chat_item in history[-6:]:
        if chat_item["role"] in ("user", "assistant"):
            chat_history.append(chat_item)

    if not chat_history or chat_history[-1]["content"] != question:
        chat_history.append({"role": "user", "content": question})

    return gemini_chat(system_prompt, chat_history)


# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 4px 0 16px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px;">
        <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#7c3aed,#ec4899);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">🤖</div>
        <div>
          <div style="font-size:15px;font-weight:600;color:#fff;">BotBaba</div>
          <div style="font-size:11px;color:#64748b;">AI Assistant</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:600;color:#4b5563;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Features</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:20px;">
      <span class="badge badge-purple">PDF RAG</span>
      <span class="badge badge-pink">Gemini</span>
      <span class="badge badge-cyan">Fast Replies</span>
      <span class="badge badge-green">Smart Context</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:600;color:#4b5563;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Session Info</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="color:#6b7280;">Model</span>
        <span style="color:#e2e8f0;font-weight:500;">gemini-2.5-flash</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <span style="color:#6b7280;">Status</span>
        <span><span class="status-dot"></span><span style="color:#34d399;">Online</span></span>
      </div>
      <div style="display:flex;justify-content:space-between;">
        <span style="color:#6b7280;">PDF</span>
        <span style="color:#e2e8f0;font-weight:500;">Loaded ✓</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "Bot Baba haazir hai. Sawal aapke, jawab mere! 🎯"
            }
        ]
        st.rerun()


# -------------------- HEADER --------------------
st.markdown("""
<div class="hero-card">
    <div class="hero-title">🤖 BotBaba Assistant</div>
    <div class="hero-subtitle">I read your data so you don't have to — powered by Gemini 2.5 Flash</div>
</div>
""", unsafe_allow_html=True)


# -------------------- SESSION STATE --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Bot Baba haazir hai. Sawal aapke, jawab mere! 🎯"
        }
    ]


# -------------------- DISPLAY CHAT --------------------
chat_container = st.container()

with chat_container:
    for msg in st.session_state.chat_history:
        avatar = "🤖" if msg["role"] == "assistant" else "🧑"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])


# -------------------- USER INPUT --------------------
user_input = st.chat_input("Sawal aapka, chamtkar Baba ka! Jaldi type karo...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Baba apni teesri aankh se data dhoond rahe hain, sabr karo..."):
            answer = get_answer(user_input, st.session_state.chat_history)
        st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
