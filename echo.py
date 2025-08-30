import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
import os
from dotenv import load_dotenv

# -------------------------------
# Load API Key from .env
# -------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API key not found. Please set GEMINI_API_KEY in your .env file.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="EchoVerse 🎧", layout="wide")
st.title("🎙️ EchoVerse - AI Audiobook Generator")
st.write("Transform your text or uploaded file into expressive, natural-sounding audio.")

# -------------------------------
# Input Options
# -------------------------------
st.header("Provide Text or Upload File")

tab1, tab2 = st.tabs(["✍️ Paste Text", "📂 Upload File"])
input_text = ""

with tab1:
    input_text = st.text_area("Paste your text here", height=200)

with tab2:
    uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded_file is not None:
        input_text = uploaded_file.read().decode("utf-8")
        st.success("File uploaded successfully!")
        st.text_area("File Content", input_text, height=200)

# -------------------------------
# Tone
# -------------------------------
st.header("Choose Tone")
tone = st.radio("Select a tone for rewriting:", ["Neutral", "Suspenseful", "Inspiring"])

# -------------------------------
# Voice Selection (edge-tts)
# -------------------------------
st.header("Choose Voice")
voice_map = {
    "Lisa": "en-US-AriaNeural",
    "Michael": "en-US-GuyNeural",
    "Allison": "en-US-JennyNeural"
}
voice_choice = st.radio("Select a voice:", list(voice_map.keys()))

# -------------------------------
# Session State for rewritten text
# -------------------------------
if "rewritten_text" not in st.session_state:
    st.session_state["rewritten_text"] = ""

# -------------------------------
# Rewriting with Gemini
# -------------------------------
if st.button("Rewrite Text"):
    if input_text.strip() == "":
        st.error("Please provide text or upload a file.")
    else:
        prompt = f"Rewrite the following text in a {tone.lower()} tone. Only one version:\n\n{input_text}"
        response = model.generate_content(prompt)
        st.session_state["rewritten_text"] = response.text
        st.success("Text rewritten successfully!")

# -------------------------------
# Show Rewritten Text (always visible if available)
# -------------------------------
if st.session_state["rewritten_text"]:
    st.subheader("📖 Text Comparison")
    st.write("**Original Text**")
    st.write(input_text if input_text.strip() else "(From last upload/input)")
    st.write(f"**{tone} Rewritten Text**")
    st.write(st.session_state["rewritten_text"])

# -------------------------------
# Generate Audio with edge-tts
# -------------------------------
async def generate_audio(text, voice):
    tts = edge_tts.Communicate(text, voice)
    output_file = "output.mp3"
    await tts.save(output_file)
    return output_file

if st.session_state["rewritten_text"]:
    if st.button("🔊 Listen to Audio"):
        output_file = asyncio.run(generate_audio(st.session_state["rewritten_text"], voice_map[voice_choice]))
        audio_bytes = open(output_file, "rb").read()
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            label="⬇️ Download Narration (.mp3)",
            data=audio_bytes,
            file_name="audiobook.mp3",
            mime="audio/mp3"
        )
