from flask import Flask, render_template, request, jsonify, session, redirect
import os, json, base64, hashlib

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.secret_key = "final_voice_gmail_project"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

USERS_FILE = "users.json"
DATASET = "dataset"
CLIENT_SECRET = "client_secret.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

os.makedirs(DATASET, exist_ok=True)
if not os.path.exists(USERS_FILE):
    json.dump({}, open(USERS_FILE, "w"))

# ---------------- HELPERS ----------------
def hash_pwd(p):
    return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    return json.load(open(USERS_FILE))

def save_users(u):
    json.dump(u, open(USERS_FILE, "w"), indent=2)

def creds_to_dict(c):
    return {
        "token": c.token,
        "refresh_token": c.refresh_token,
        "token_uri": c.token_uri,
        "client_id": c.client_id,
        "client_secret": c.client_secret,
        "scopes": c.scopes
    }

def gmail_service():
    return build("gmail", "v1", credentials=Credentials(**session["credentials"]))

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session and "credentials" not in session:
        return redirect("/login")
    return render_template("dashboard.html", email=session.get("user", "Google User"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- MANUAL LOGIN ----------------
@app.route("/api/login", methods=["POST"])
def api_login():
    d = request.json
    users = load_users()

    if users.get(d["email"]) != hash_pwd(d["password"]):
        return jsonify(success=False, message="Invalid credentials")

    session["user"] = d["email"]
    session["mode"] = "local"
    return jsonify(success=True)

# ---------------- GOOGLE LOGIN ----------------
@app.route("/login/google")
def google_login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET,
        scopes=SCOPES,
        redirect_uri="http://127.0.0.1:5000/auth/google/callback"
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    session["state"] = state
    return redirect(auth_url)

@app.route("/auth/google/callback")
def google_callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET,
        scopes=SCOPES,
        state=session["state"],
        redirect_uri="http://127.0.0.1:5000/auth/google/callback"
    )

    flow.fetch_token(authorization_response=request.url)
    session["credentials"] = creds_to_dict(flow.credentials)
    session["user"] = "Logged in with Google"
    session["mode"] = "gmail"

    return redirect("/dashboard")

# ---------------- FACE LOGIN ----------------
@app.route("/api/face-login", methods=["POST"])
def api_face_login():
    import cv2

    data = request.json.get("image")
    if not data:
        return jsonify(success=False, message="No image received")

    img_bytes = base64.b64decode(data.split(",")[1])
    open("temp.jpg", "wb").write(img_bytes)

    if not os.path.exists("trainer.yml") or not os.path.exists("labels.json"):
        return jsonify(success=False, message="Face model not trained")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")
    labels = json.load(open("labels.json"))

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    img = cv2.imread("temp.jpg", cv2.IMREAD_GRAYSCALE)
    faces = face_cascade.detectMultiScale(img, 1.3, 5)

    if len(faces) == 0:
        return jsonify(success=False, message="No face detected")

    for (x, y, w, h) in faces:
        face = cv2.resize(img[y:y+h, x:x+w], (200, 200))
        label, confidence = recognizer.predict(face)

        if confidence < 140:
            session["user"] = labels[str(label)]
            session["mode"] = "face"
            return jsonify(success=True, message="Face verified")

    return jsonify(success=False, message="Face not recognized")

# ---------------- VOICE LOGIN ROUTER ----------------
@app.route("/api/voice-login", methods=["POST"])
def voice_login():
    command = request.json.get("command", "").lower().strip()
    command = command.replace(".", "").replace(",", "")

    if "login with google" in command:
        return jsonify(action="google")

    if "login" in command:
        return jsonify(action="face")

    return jsonify(action="none")

# ==================================================
# ✅ ONLY ADDED PART (DO NOT REMOVE)
# ---------------- VOICE COMMAND API ----------------
@app.route("/api/voice-command", methods=["POST"])
def voice_command():
    cmd = request.json.get("command", "").lower().strip()
    cmd = cmd.replace(".", "").replace(",", "")

    actions = {
        "inbox": ("Opening inbox", "inbox"),
        "sent": ("Opening sent mails", "sent"),
        "trash": ("Opening trash", "trash"),
        "compose": ("Opening compose", "compose"),
        "logout": ("Logging out", "logout"),
        "read": ("Reading latest email", "read"),
        "help": ("Say inbox, sent, trash, compose or logout", "help")
    }

    for key in actions:
        if key in cmd:
            return jsonify(response=actions[key][0], action=actions[key][1])

    return jsonify(response="Command not understood. Say help.", action="none")
# ==================================================

# ---------------- START ----------------
if __name__ == "__main__":
    app.run(debug=True)
