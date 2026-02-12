def summarize_text(text):
    if not text or len(text.split()) < 50:
        return text

    sentences = text.split(".")
    summary = ". ".join(sentences[:3])
    return summary.strip()
