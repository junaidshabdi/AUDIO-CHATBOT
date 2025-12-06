import os
import time

import streamlit as st
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import google.generativeai as genai

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# ----------------- SESSION STATE FLAGS -----------------

if "stop" not in st.session_state:
    st.session_state.stop = False

if "chat_history" not in st.session_state:
    # list of {"role": "user"/"assistant", "text": "..."}
    st.session_state.chat_history = []

if "input_key" not in st.session_state:
    st.session_state.input_key = 0  # Key to force text-input reset

# ----------------- CONFIG & SETUP -----------------

# Load environment variables (.env)
load_dotenv()

# Support both names, in case you used either
default_api_key = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or ""
)

SYSTEM_INSTRUCTION = (
    "You are a friendly, conversational AI voice assistant. "
    "Keep answers concise, clear, and easy to understand."
)

# ---------- SIDEBAR (API KEY, CONTROLS) ----------

with st.sidebar:
    st.title("⚙️ Settings & Info")
    st.write("This is a **Gemini-powered Voice Assistant** built with Streamlit.")
    st.write("- Text + Voice input\n- Text-to-Speech output\n- Chat memory")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=default_api_key,
        help="Loaded from GOOGLE_API_KEY or GEMINI_API_KEY in your .env (if present)."
    )

    if api_key:
        st.success("✅ API key ready")
    else:
        st.error("❌ Enter your Gemini API key above.")
    
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.input_key += 1
        st.rerun()

    if st.button("🛑 Stop Speaking"):
        st.session_state.stop = True

    st.markdown("---")
    st.caption("Developed by ABDUL KARIM – Python, Streamlit, Gemini API")

# If no API key → stop everything
if not api_key:
    st.stop()

# Configure Gemini client
genai.configure(api_key=api_key)
MODEL_NAME = "gemini-flash-latest"
model = genai.GenerativeModel(MODEL_NAME)

# ---------- SAFE TEXT-TO-SPEECH (pyttsx3) ----------

def speak_text(text: str):
    """
    Speak text safely in Streamlit.
    Fresh engine per call to avoid 'run loop already started' issues.
    """
    if not text:
        return

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


# ---------- GEMINI CALL (USING CLIENT LIBRARY) ----------

def get_gemini_response(user_text: str) -> str:
    """
    Build a single prompt including system instruction + conversation
    history, then call Gemini and return the reply text.
    """
    # Convert chat history to plain text conversation
    history_lines = []
    for msg in st.session_state.chat_history:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history_lines.append(f"{role_label}: {msg['text']}")

    history_text = "\n".join(history_lines)

    full_prompt = f"""
System: {SYSTEM_INSTRUCTION}

Conversation so far:
{history_text}

User: {user_text}
Assistant:
""".strip()

    try:
        response = model.generate_content(full_prompt)
        reply = (response.text or "").strip()
        if not reply:
            reply = "I'm sorry, I couldn't generate a response."
    except Exception as e:
        reply = f"Error calling Gemini API: {e}"

    # Update chat history
    st.session_state.chat_history.append({"role": "user", "text": user_text})
    st.session_state.chat_history.append({"role": "assistant", "text": reply})

    return reply


# ---------- SPEECH TO TEXT (LOCAL MIC) ----------

def speech_to_text() -> str:
    """Capture audio from mic and convert to text using Google Speech API."""
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            st.info("🎤 Listening... Speak now.")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        text = recognizer.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        return "I didn't hear anything. Please try again."
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Speech service unavailable. Check your internet connection."
    except Exception as e:
        return f"An unknown microphone error occurred: {e}"


# ----------------- MAIN UI -----------------

st.title("🎙️ AUDIO-TO-AUDIO CHATBOT")
st.write("Talk to your assistant using **text** or **voice**.")

st.markdown("---")

# ---------- Custom CSS ----------
st.markdown(
    """
    <style>

    .stApp {
        background-color: #F2F3F5;
        color: #222222 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #E6E8EB !important;
        color: #222222 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #222222 !important;
    }

    .user-bubble {
        background-color: #D6F5D6;
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 8px;
        max-width: 80%;
        margin-left: auto;
        color: #000000 !important;
    }

    .ai-bubble {
        background-color: #FFFFFF;
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 8px;
        max-width: 80%;
        margin-right: auto;
        color: #000000 !important;
    }

    .role-label {
        font-size: 12px;
        color: #444444 !important;
        margin-bottom: 2px;
    }

    input[type="text"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 8px !important;
    }

    .stButton>button {
        background-color: #4A90E2;
        color: white !important;
        padding: 8px 18px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #3C78C6;
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Conversation (Chat History) ----------

st.subheader("💬 Conversation")

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

if not st.session_state.chat_history:
    st.info("💡 Start a conversation by typing a message or using voice input!")

st.markdown("---")

# ---------- Text Input ----------
st.subheader("⌨️ Type your message")

with st.form(key="text_input_form"):
    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Ask me anything...",
            key=f"text_input_{st.session_state.input_key}",
        )

    with col2:
        submit_button = st.form_submit_button("Send", type="primary")

if submit_button and user_input.strip():
    st.session_state.stop = False
    user_text = user_input.strip()

    ai_reply = get_gemini_response(user_text)
    st.toast("Assistant replied!", icon="🤖")

    speak_text(ai_reply)

    st.session_state.input_key += 1
    st.rerun()

# ---------- Voice Input ----------
st.subheader("🎤 Or use your voice")

if st.button("🎙️ Speak", key="speak_button"):
    st.session_state.stop = False

    with st.spinner("Recording..."):
        spoken_text = speech_to_text()

    if spoken_text:
        st.info(f"🧑 You said: **{spoken_text}**")

        error_messages = [
            "I didn't hear anything. Please try again.",
            "Sorry, I could not understand the audio.",
            "Speech service unavailable. Check your internet connection.",
            "An unknown microphone error occurred:",
        ]

        if not any(error_msg in spoken_text for error_msg in error_messages):
            ai_reply = get_gemini_response(spoken_text)
            st.toast("Assistant replied!", icon="🤖")
            speak_text(ai_reply)
            st.rerun()
        else:
            st.warning(spoken_text)
    else:
        st.warning("No speech detected. Please try again.")




