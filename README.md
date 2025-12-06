🔊 AUDIO-TO-AUDIO CHATBOT
An intelligent voice-interactive AI assistant built using Streamlit, Google Gemini API, Speech Recognition, and pyttsx3.
This chatbot allows users to speak to the AI, it listens, processes the query through Gemini, and responds back using audio — making it a complete audio-to-audio communication system.

🚀 Features

🎤 Voice Input using your microphone

🤖 AI-powered responses using Gemini Flash model

🔊 Audio Output (AI speaks back) using pyttsx3

💬 Chat Memory that remembers the conversation context

🎨 Attractive chat UI with user & assistant message bubbles

🧹 Clear Chat button to reset conversation

🛑 Stop Speaking button to interrupt TTS

🔐 Secure API Key handling using .env

📁 Project Structure
AUDIO-TO-AUDIO CHATBOT/
│── app.py
│── requirements.txt
│── .env
│── README.md

🔧 Installation
1️⃣ Clone the Project
git clone https://github.com/your-username/AUDIO-TO-AUDIO-CHATBOT.git
cd AUDIO-TO-AUDIO-CHATBOT

2️⃣ Install Dependencies
pip install -r requirements.txt


If PyAudio fails on Windows, download the wheel from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Then install manually:

pip install PyAudio-0.2.11-cp310-cp310-win_amd64.whl


(Choose the wheel matching your Python version.)

3️⃣ Configure Your API Key

Create a .env file:

GOOGLE_API_KEY=YOUR_GEMINI_API_KEY


Get Gemini API Key:
👉 https://aistudio.google.com/app/apikey

▶️ Running the Application

Run Streamlit:

streamlit run app.py


The chatbot will open automatically at:

http://localhost:8501

🎯 How the AUDIO-TO-AUDIO Chatbot Works
🔹 Step 1 — Speech to Text

Using SpeechRecognition, the app listens to your voice and converts it to text.

🔹 Step 2 — AI Processing

The recognized text + conversation history are sent to the Gemini Flash model for generating a response.

🔹 Step 3 — Text-to-Speech

The Gemini response is spoken out loud using pyttsx3, completing the audio-to-audio loop.

🔹 Step 4 — Chat Memory

Your conversation is stored and used for context-aware replies.

🛠️ Technologies Used

Python

Streamlit (Web UI)

Google Gemini API

SpeechRecognition

pyttsx3 (Text-to-Speech)

dotenv (Environment variables)

📦 Requirements (requirements.txt)
streamlit
speechrecognition
pyttsx3
python-dotenv
google-generativeai
pyaudio

🖼️ Screenshots

(Add your app screenshots here)

🌟 Future Improvements

🎧 Real-time streaming transcription

🗣️ Wake word activation ("Hey Gemini")

🎵 Change AI voice (male/female)

📱 Convert to EXE desktop app

📡 Add tool integrations (weather, news, calculator)

👨‍💻 Developer

Abdul Karim
Python Developer | AI Enthusiast
AUDIO-TO-AUDIO CHATBOT Project Creator

If you want, I can also generate:

✅ A project report PDF
✅ A PowerPoint presentation
✅ A GitHub profile-worthy README banner
✅ A project logo

Would you like any of these?
