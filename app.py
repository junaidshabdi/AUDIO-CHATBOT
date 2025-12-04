import streamlit as st
import requests
import os
import time
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv

if "stop" not in st.session_state:
    st.session_state.stop = False


# ----------------- CONFIG & SETUP -----------------

# Load environment variables (.env)
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
print("DEBUG API KEY:", API_KEY)

API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"
LLM_MODEL = "gemini-2.0-flash"


MAX_RETRIES = 3

SYSTEM_INSTRUCTION = (
    "You are a friendly, conversational AI Voice Assistant. "
    "Keep answers concise and clear."
)

# ---------- SAFE TEXT-TO-SPEECH (pyttsx3) ----------

def speak_text(text: str):
    """
    Safe TTS for Streamlit: create a fresh engine per call to avoid
    'run loop already started' errors.
    """
    if not text:
        return

    # If STOP was pressed, stay silent
    if st.session_state.get("stop", False):
        return

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("TTS error:", e)




def fetch_with_retry(api_url, payload, retries=MAX_RETRIES):
    """Call Gemini API with simple retry logic."""
    if not API_KEY:
        raise Exception("API key missing. Please set GOOGLE_API_KEY in .env")

    headers = {"Content-Type": "application/json"}

    for attempt in range(retries):
        try:
            full_url = f"{api_url}?key={API_KEY}"
            response = requests.post(full_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception:
            time.sleep(2 ** attempt)

    return {"error": "API request failed after retries"}


def get_gemini_response(user_text: str):
    """Send full chat history + new user message to Gemini and return reply."""
    # Build contents from chat history + new message
    contents = []

    # Add previous history
    for item in st.session_state.chat_history:
        contents.append(
            {
                "role": item["role"],  # "user" or "model"
                "parts": [{"text": item["text"]}],
            }
        )

    # Add current user message
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    api_url = API_BASE_URL + LLM_MODEL + ":generateContent"

    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
    }

    result = fetch_with_retry(api_url, payload)

    try:
        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        ai_text = "Sorry, I couldn't understand the API response."

    # Update session history
    st.session_state.chat_history.append({"role": "user", "text": user_text})
    st.session_state.chat_history.append({"role": "model", "text": ai_text})

    return ai_text


def speech_to_text():
    """Capture audio from mic and convert to text using Google Speech API."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        st.info("🎤 Listening... Speak now.")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except Exception:
        return "Sorry, I could not hear you clearly."


# ----------------- STREAMLIT UI -----------------

st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚙️ Settings & Info")
    st.write("This is a **Gemini-powered Voice Assistant** built with Streamlit.")
    st.write("- Text + Voice input\n- Text-to-Speech output\n- Chat memory")

    if API_KEY:
        st.success("✅ API key loaded from .env")
    else:
        st.error("❌ No API key found. Set GOOGLE_API_KEY in .env")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")

    # 🔴 STOP BUTTON (paste here)
    if st.button("🛑 Stop Speaking"):
        st.session_state.stop = True

    st.markdown("---")
    st.caption("Developed by ABDUL KARIM – Python, Streamlit, Gemini API")


# ---------- Main Layout ----------
st.title("🎙️ AI Voice Assistant")
st.write("Talk to your assistant using **text** or **voice**.")

st.markdown("---")

# Custom chat styling
st.markdown(
    """
    <style>

    /* 🌟 CLEAN LIGHT BACKGROUND (NOT TOO BRIGHT) */
    .stApp {
        background-color: #F2F3F5;  /* soft light gray */
        color: #222222 !important; /* dark text for readability */
    }

    /* 🌟 SIDEBAR FIX (so text looks clear) */
    section[data-testid="stSidebar"] {
        background-color: #E6E8EB !important;
        color: #222222 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #222222 !important;
    }

    /* 💬 USER bubble */
    .user-bubble {
        background-color: #D6F5D6; /* light green */
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 8px;
        max-width: 80%;
        margin-left: auto;
        color: #000000 !important;
    }

    /* 🤖 AI bubble */
    .ai-bubble {
        background-color: #FFFFFF; /* clean white bubble */
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 8px;
        max-width: 80%;
        margin-right: auto;
        color: #000000 !important;
    }

    /* Role labels */
    .role-label {
        font-size: 12px;
        color: #444444 !important;
        margin-bottom: 2px;
    }

    /* Improve input box visibility */
    input[type="text"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 8px !important;
    }

    /* Fix button visibility */
    .stButton>button {
        background-color: #4A90E2;
        color: white !important;
        padding: 8px 18px;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3C78C6;
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)




st.subheader("💬 Conversation")


# Show chat history
# Show chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="role-label" style="text-align:right;">You</div>
            <div class="user-bubble">{msg['text']}</div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="role-label">Assistant</div>
            <div class="ai-bubble">{msg['text']}</div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")   # Divider after chat history

# ---------- Text Input ----------
st.subheader("⌨️ Type your message")

col1, col2 = st.columns([3, 1])

with col1:
    user_input = st.text_input("Message", placeholder="Ask me anything...")

with col2:
    send_clicked = st.button("Send")

if send_clicked and user_input.strip() != "":
    st.session_state.stop = False   # allow new speaking
    ai_reply = get_gemini_response(user_input)
    st.success(f"Assistant: {ai_reply}")
    speak_text(ai_reply)


# ---------- Voice Input ----------
st.subheader("🎤 Or use your voice")

if st.button("🎙️ Speak"):
    st.session_state.stop = False   # allow new speaking
    spoken_text = speech_to_text()
    st.info(f"🧑 You said: **{spoken_text}**")
    ai_reply = get_gemini_response(spoken_text)
    st.success(f"Assistant: {ai_reply}")
    speak_text(ai_reply)


