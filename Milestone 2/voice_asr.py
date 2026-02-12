import whisper
import tempfile
import os
import subprocess

# 🔴 FORCE ffmpeg path (Windows fix)
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg-8.0.1-essentials_build\bin"

model = whisper.load_model("base")

def transcribe_audio(audio_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        audio_file.save(tmp.name)
        temp_path = tmp.name

    result = model.transcribe(temp_path)

    os.remove(temp_path)
    return result["text"].strip().lower()
