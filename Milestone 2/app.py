import webbrowser
import subprocess
import platform
import re
import os, json, base64, cv2

from flask import Flask, render_template, request, jsonify, session, redirect
from google_auth_oauthlib.flow import Flow

from ai.summarizer import summarize_text
from ai.reply_generator import generate_reply

from gmail_service import (
    get_emails_by_label,
    send_email,
    delete_email
)

from voice_asr import transcribe_audio


# ================== APP CONFIG ==================
app = Flask(__name__)
app.secret_key = "final_voice_gmail_project"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_SECRET = "client_secret.json"
USERS_FILE = "users.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

if not os.path.exists(USERS_FILE):
    json.dump({}, open(USERS_FILE, "w"))


# ================== BASIC ROUTES ==================
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "credentials" not in session and "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ✅ RESTORED VOICE COMPOSE PAGE ROUTE
@app.route("/voice-mail")
def voice_mail():
    if "credentials" not in session and "user" not in session:
        return redirect("/login")
    return render_template("voice_compose.html")


# ================== GOOGLE LOGIN ==================
@app.route("/login/google")
def google_login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET,
        scopes=SCOPES,
        redirect_uri="http://127.0.0.1:5000/auth/google/callback"
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )
    return redirect(auth_url)

@app.route("/auth/google/callback")
def google_callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET,
        scopes=SCOPES,
        redirect_uri="http://127.0.0.1:5000/auth/google/callback"
    )
    flow.fetch_token(authorization_response=request.url)

    session["credentials"] = {
        "token": flow.credentials.token,
        "refresh_token": flow.credentials.refresh_token,
        "token_uri": flow.credentials.token_uri,
        "client_id": flow.credentials.client_id,
        "client_secret": flow.credentials.client_secret,
        "scopes": flow.credentials.scopes
    }
    session["user"] = "Google User"
    return redirect("/dashboard")


# ================== FACE + PIN LOGIN ==================
@app.route("/api/face-pin-login", methods=["POST"])
def face_pin_login():
    data = request.json or {}
    pin = data.get("pin")
    image = data.get("image")

    if not pin or not image:
        return jsonify(success=False, message="PIN or face image missing")

    try:
        img_bytes = base64.b64decode(image.split(",")[1])
        with open("temp.jpg", "wb") as f:
            f.write(img_bytes)
    except:
        return jsonify(success=False, message="Invalid image data")

    users = json.load(open(USERS_FILE))

    if not hasattr(cv2, "face"):
        return jsonify(success=False, message="Install opencv-contrib-python")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")
    labels = json.load(open("labels.json"))

    gray = cv2.imread("temp.jpg", cv2.IMREAD_GRAYSCALE)
    faces = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    ).detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        label, confidence = recognizer.predict(face)
        email = labels.get(str(label))

        if (
            email in users
            and confidence < 200
            and str(users[email]["pin"]) == str(pin)
        ):
            session["user"] = email
            return jsonify(success=True, redirect="/dashboard")

    return jsonify(success=False, message="Face or PIN incorrect")


# ================== FETCH GMAIL ==================
@app.route("/api/gmail/<folder>")
def gmail_folder(folder):
    if "credentials" not in session:
        return jsonify(success=False)

    label_map = {
        "inbox": "INBOX",
        "sent": "SENT",
        "trash": "TRASH"
    }

    emails = get_emails_by_label(
        session["credentials"],
        label_map[folder]
    )

    session["emails"] = emails
    return jsonify(success=True, emails=emails)


# ================== SEND EMAIL ==================
@app.route("/api/compose", methods=["POST"])
def compose_mail():
    if "credentials" not in session:
        return jsonify(success=False), 401

    data = request.json
    send_email(
        session["credentials"],
        data["to"],
        data["subject"],
        data["body"]
    )
    return jsonify(success=True)


# ================== AI SUMMARY / REPLY ==================
@app.route("/api/email/ai/<int:index>")
def ai_email(index):
    emails = session.get("emails", [])

    if index < 0 or index >= len(emails):
        return jsonify(success=False)

    email = emails[index]
    summary = summarize_text(email["body"])
    reply = generate_reply(email["body"])

    return jsonify(success=True, summary=summary, reply=reply)


# ================== TELEGRAM ==================
def open_telegram(chat_name=None):
    try:
        if chat_name is None:
            webbrowser.open("https://web.telegram.org/")
            return "Opening Telegram"

        username = chat_name.lower().replace(" ", "")
        webbrowser.open(f"https://t.me/{username}")
        return f"Opening {chat_name} chat on Telegram"

    except:
        return "Unable to open Telegram"


@app.route("/api/telegram/voice", methods=["POST"])
def telegram_voice():
    text = request.json.get("text", "").lower().strip()

    if text == "telegram" or text == "open telegram":
        return jsonify(reply=open_telegram())

    if "open" in text and "chat" in text and "telegram" in text:
        try:
            name = text.split("open")[1].split("chat")[0].strip()
            return jsonify(reply=open_telegram(name))
        except:
            return jsonify(reply="Chat name not detected")

    return jsonify(reply="Command not recognized")


# ================== RUN ==================
if __name__ == "__main__":
    app.run(debug=True)
