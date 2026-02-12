from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests
import json, os

from ai.summarizer import summarize_text
from ai.reply_generator import generate_reply

# ================= CONFIG =================
BOT_TOKEN = "8386672558:AAEsV6lOrKhBt4J7CZnR2ca9p-0T0Sb4HNY"
STORE_FILE = "telegram_messages.json"

# Map names to chat_ids (DEMO PURPOSE)
USER_MAP = {
    "rahul": 123456789,
    "pooja": 987654321
}
# =========================================


# ---------- SAVE MESSAGES ----------
def save_message(data):
    if not os.path.exists(STORE_FILE):
        with open(STORE_FILE, "w") as f:
            json.dump([], f)

    with open(STORE_FILE, "r") as f:
        messages = json.load(f)

    messages.append(data)

    with open(STORE_FILE, "w") as f:
        json.dump(messages, f, indent=2)


# ---------- SEND TELEGRAM MESSAGE ----------
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, json=payload)


# ---------- COMMAND PARSER (VOICE SIMULATION) ----------
def parse_command(text):
    text = text.lower()

    if "send telegram message to" in text and "saying" in text:
        try:
            name = text.split("to")[1].split("saying")[0].strip()
            message = text.split("saying")[1].strip()
            return name, message
        except:
            return None, None

    return None, None


# ---------- MAIN HANDLER ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user.username or "unknown"

    # 1️⃣ CHECK FOR SEND COMMAND
    name, msg = parse_command(text)

    if name and msg:
        if name in USER_MAP:
            send_telegram_message(USER_MAP[name], msg)
            await update.message.reply_text(
                f"✅ Message sent to {name} on Telegram"
            )
        else:
            await update.message.reply_text(
                "❌ User not found in Telegram contacts"
            )
        return

    # 2️⃣ NORMAL MESSAGE → SUMMARY + AI REPLY
    summary = summarize_text(text)
    reply = generate_reply(text)

    save_message({
        "user": user,
        "message": text,
        "summary": summary,
        "reply": reply
    })

    await update.message.reply_text(
        f"📌 Summary:\n{summary}\n\n🤖 Suggested Reply:\n{reply}"
    )


# ---------- RUN BOT ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Telegram Bot Running (Milestone 3)")
    app.run_polling()


if __name__ == "__main__":
    main()
