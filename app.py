import streamlit as st
import yt_dlp
import requests
from transcribe import transcribe  # Ensure this module is correctly implemented
from pydub import AudioSegment
import os
import tempfile
import google.generativeai as genai

# -------------------------
# Configuration and Setup
# -------------------------

# Load environment variables securely using Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)

# Optimized prompt for Gemini Flash
OPTIMIZED_PROMPT = """
Arabic (and non-English) words are italicized.  Exception: Non-English words that have entered the English vernacular (e.g., Allah, Imām, Quran) are not italicized.  People's names and place names are not italicized.  Book titles are italicized.  "al-" is lowercase unless it is the first word of a sentence or title.  Do not use hamzat al-waṣl for *sūrah* names or prayers (e.g., *Sūrat al-Fātiḥah*, *ṣalāt al-Fajr*).  Do not use apostrophes or single quotes for ع or ء; use their respective symbols (ʿ and ʾ).  Words ending in ة end with "h" (e.g., *sūrah*, *Abu Ḥanīfah*).  Do not transliterate hamzah unless the word is between two words.  Represent *shaddah* with a double letter (e.g., شدّة = *shaddah*). Do not use contractions.  Keep the original Arabic text as is.  Do not add any extra information or commentary.  Only edit the provided text.
"""

# Initialize session state variables
if 'original_transcript' not in st.session_state:
    st.session_state.original_transcript = ""
if 'improved_transcript' not in st.session_state:
    st.session_state.improved_transcript = ""
if 'final_transcript' not in st.session_state:
    st.session_state.final_transcript = ""

# -------------------------
# Helper Functions
# -------------------------

def improve_transcript(transcript):
    """
    Improves the transcript using Gemini Flash model.
    Splits the transcript into chunks to comply with API limits.
    """
    edited_transcript = ""
    chunks = [transcript[i:i+8000] for i in range(0, len(transcript), 8000)]  # 8000 character chunks
    model = genai.GenerativeModel("gemini-1.5-flash")

    for chunk in chunks:
        prompt_text = f"{OPTIMIZED_PROMPT}\n\n{chunk}"
        payload = {
            "prompt": {"text": prompt_text},
        }

        try:
            # response = model.generate_content(payload)
            response = model.generate_content(prompt_text);
            # Assuming the response contains 'candidates' with 'output'
            if response and 'candidates' in response and len(response['candidates']) > 0:
                edited_transcript += response.text
            else:
                st.error("No output received from Gemini Flash API.")
                return None
        except Exception as e:
            st.error(f"Gemini Flash API error: {e}")
            return None

    # Optionally, save the edited transcript to a file
    with open("edited_transcript.txt", "w", encoding='utf-8') as f:
        f.write(edited_transcript)

    return edited_transcript

def compare_and_correct(original, edited):
    """
    Compares the edited transcript with the original and corrects any discrepancies using Gemini Pro model.
    """
    corrected_transcript = ""
    chunks = [edited[i:i+8000] for i in range(0, len(edited), 8000)]  # 8000 character chunks
    original_chunks = [original[i:i+8000] for i in range(0, len(original), 8000)]
    model = genai.GenerativeModel("gemini-1.5-pro-002")

    for chunk_edited, chunk_original in zip(chunks, original_chunks):
        prompt = f"""Compare the edited transcript with the original transcript and correct any errors or unnecessary changes in the edited transcript.\
Make sure the edited transcript follows the prompt and the changes are accurate.

Original Transcript:
{chunk_original}

Edited Transcript:
{chunk_edited}
"""
        payload = {
            "prompt": {"text": prompt},
        }

        try:
            response = model.generate_content(payload)
            if response and 'candidates' in response and len(response['candidates']) > 0:
                corrected_transcript += response.text
            else:
                st.error("No output received from Gemini Pro API.")
                return None
        except Exception as e:
            st.error(f"Gemini Pro API error: {e}")
            return None

    # Optionally, save the corrected transcript to a file
    with open("corrected_transcript.txt", "w", encoding='utf-8') as f:
        f.write(corrected_transcript)

    return corrected_transcript

def download_audio(youtube_url):
    """
    Downloads audio from a YouTube URL using yt_dlp.
    Returns the path to the downloaded audio file.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        audio_file = f"{info['id']}.mp3"
    return audio_file

def upload_to_gemini(audio_file_path):
    """
    Uploads the audio file to Gemini API for transcription.
    Returns the path or identifier of the uploaded file.
    """
    # Placeholder function: Implement the actual upload logic based on Gemini API specifications
    # This might involve sending the file to a specific endpoint and receiving an upload ID
    # For demonstration, we'll assume the file is uploaded and return the same path
    return audio_file_path

def transcribe_audio(uploaded_file_path):
    """
    Transcribes the uploaded audio file using the transcribe function from transcribe module.
    """
    try:
        transcript = transcribe(uploaded_file_path)
        return transcript
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return None

# -------------------------
# Streamlit Application
# -------------------------

st.set_page_config(layout="wide")

# -------------------------
# Input Selection
# -------------------------
st.title("📄 YouTube Transcript Improver & 🎤 Audio Transcription")

input_method = st.radio(
    "Choose input method:",
    ["YouTube URL", "Audio File", "Direct Text Input"],
    horizontal=True
)

if input_method == "YouTube URL":
    youtube_url = st.text_input("Enter YouTube URL:")
    if youtube_url and st.button("Download and Process"):
        with st.spinner("Downloading audio from YouTube..."):
            audio_file = download_audio(youtube_url)
            if audio_file:
                st.success("Audio downloaded successfully!")
                st.session_state.uploaded_audio_path = audio_file
                st.audio(audio_file, format='audio/mp3')

elif input_method == "Audio File":
    uploaded_audio = st.file_uploader(
        "Upload an audio file for transcription (mp3, wav, m4a):",
        type=["mp3", "wav", "m4a"]
    )
    # ... rest of the audio upload logic ...

elif input_method == "Direct Text Input":
    st.session_state.original_transcript = st.text_area(
        "Enter or paste your text here:",
        value=st.session_state.original_transcript,
        height=200
    )

# -------------------------
# Text Editing Workflow
# -------------------------
st.header("📝 Text Editing Workflow")

# Original Editor
st.subheader("Original Transcript Editor")
original_editor = st.text_area(
    "Edit the original transcript here:",
    value=st.session_state.original_transcript,
    height=200,
    key="original_editor"
)
# -------------------------
# Audio Transcription Workflow
# -------------------------
st.header("🎧 Audio Transcription Workflow")

# Upload Audio File
uploaded_audio = st.file_uploader(
    "Upload an audio file for transcription (mp3, wav, m4a):",
    type=["mp3", "wav", "m4a"]
)

# Initialize session state for audio
if 'uploaded_audio_path' not in st.session_state:
    st.session_state.uploaded_audio_path = None
if 'transcribed_audio' not in st.session_state:
    st.session_state.transcribed_audio = ""

# Audio Workflow Buttons
if uploaded_audio is not None:
    # Save uploaded file to a temporary directory
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tmp_file.write(uploaded_audio.getbuffer())
        uploaded_file_path = tmp_file.name
    st.session_state.uploaded_audio_path = uploaded_file_path

    # Display audio player
    st.audio(uploaded_file_path, format='audio/mp3')

    # Upload to Gemini Button
    if st.button("Upload to Gemini"):
        with st.spinner("Uploading audio to Gemini..."):
            uploaded_to_gemini = upload_to_gemini(uploaded_file_path)
            if uploaded_to_gemini:
                st.success("Audio uploaded to Gemini successfully!")
            else:
                st.error("Failed to upload audio to Gemini.")

    # Transcribe Button
    if st.button("Transcribe"):
        if st.session_state.uploaded_audio_path is None:
            st.error("No audio file uploaded. Please upload an audio file first.")
        else:
            with st.spinner("Transcribing audio..."):
                transcript = transcribe_audio(st.session_state.uploaded_audio_path)
                if transcript:
                    st.session_state.transcribed_audio = transcript
                    st.success("Audio transcribed successfully!")
                else:
                    st.error("Failed to transcribe audio.")
    
    # # Display Transcribed Text
    # if st.session_state.transcribed_audio:
    #     st.subheader("Transcribed Text")
    #     st.text_area(
    #         "Transcribed text:",
    #         value=st.session_state.transcribed_audio,
    #         height=200,
    #         key="transcribed_audio"
        # )


# Update session state
st.session_state.original_transcript = original_editor

# Improve Transcript Button
if st.button("Improve Transcript"):
    if st.session_state.original_transcript.strip() == "":
        st.error("Original transcript is empty. Please enter text to improve.")
    else:
        with st.spinner("Improving transcript with Gemini Flash..."):
            improved = improve_transcript(st.session_state.original_transcript)
            if improved:
                st.session_state.improved_transcript = improved
                st.success("Transcript improved successfully!")
            else:
                st.error("Failed to improve the transcript.")

# Improved Editor
st.subheader("Improved Transcript Editor")
improved_editor = st.text_area(
    "Edit the improved transcript here:",
    value=st.session_state.improved_transcript,
    height=200,
    key="improved_editor"
)

# Update session state
st.session_state.improved_transcript = improved_editor

# Finalize Transcript Button
if st.button("Finalize Transcript"):
    if st.session_state.improved_transcript.strip() == "":
        st.error("Improved transcript is empty. Please improve the text first.")
    else:
        with st.spinner("Finalizing transcript with Gemini Pro..."):
            final = compare_and_correct(st.session_state.original_transcript, st.session_state.improved_transcript)
            if final:
                st.session_state.final_transcript = final
                st.success("Transcript finalized successfully!")
            else:
                st.error("Failed to finalize the transcript.")

# Final Editor
st.subheader("Final Transcript Editor")
final_editor = st.text_area(
    "Final transcript will appear here:",
    value=st.session_state.final_transcript,
    height=200,
    key="final_editor"
)

# Update session state
st.session_state.final_transcript = final_editor
