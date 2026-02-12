from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText

def get_service(creds):
    credentials = Credentials(
        token=creds["token"],
        refresh_token=creds.get("refresh_token"),
        token_uri=creds["token_uri"],
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        scopes=creds["scopes"]
    )
    return build("gmail", "v1", credentials=credentials)

# -------- FETCH EMAILS ----------
def get_emails_by_label(creds, label):
    service = get_service(creds)

    if label == "SENT":
        results = service.users().messages().list(
            userId="me",
            q="in:sent",
            maxResults=5
        ).execute()
    else:
        results = service.users().messages().list(
            userId="me",
            labelIds=[label],
            maxResults=5
        ).execute()

    emails = []

    for msg in results.get("messages", []):
        data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = data["payload"]["headers"]
        subject = sender = ""

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"]
            if h["name"] == "From":
                sender = h["value"]

        body = ""
        parts = data["payload"].get("parts", [])
        for p in parts:
            if p["mimeType"] == "text/plain" and "data" in p["body"]:
                body = base64.urlsafe_b64decode(
                    p["body"]["data"]
                ).decode(errors="ignore")

        emails.append({
            "id": msg["id"],
            "from": sender,
            "subject": subject,
            "body": body[:500]
        })

    return emails


# -------- SEND EMAIL (M3) ----------
def send_email(creds, to, subject, body):
    service = get_service(creds)

    # 🔥 FIX: CLEAN EMAIL
    to = to.strip().lower()
    to = to.replace(" ", "")
    to = to.rstrip(".,")   # <-- removes trailing . or ,

    message = MIMEText(body)
    message["to"] = to
    message["from"] = "me"
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    sent = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    print("✅ SENT MESSAGE ID:", sent["id"])


# -------- DELETE EMAIL (M3) ----------
def delete_email(creds, msg_id):
    service = get_service(creds)
    service.users().messages().trash(userId="me", id=msg_id).execute()
