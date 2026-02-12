def generate_reply(text):
    text = text.lower()

    if "deadline" in text or "submission" in text:
        return (
            "Thank you for the update. "
            "I will make sure all required documents are submitted before the deadline."
        )

    if "meeting" in text or "discussion" in text:
        return (
            "Thank you for the information. "
            "Please let me know the meeting time and I will be available."
        )

    if "approved" in text or "confirmation" in text:
        return (
            "Thank you for the confirmation. "
            "I acknowledge the update."
        )

    if "issue" in text or "problem" in text:
        return (
            "Thank you for informing me. "
            "I will look into the issue and update you shortly."
        )

    # default fallback
    return "Thank you for your message. I will get back to you soon."
