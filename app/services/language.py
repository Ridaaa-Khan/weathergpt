def detect_language(text: str) -> str:
    """
    Detect English vs Hindi from the user message.
    Returns: "hi" or "en"
    """
    if not text or not text.strip():
        return "en"

    devanagari_count = 0
    letter_count = 0

    for ch in text:
        code = ord(ch)
        # Devanagari block (used by Hindi)
        if 0x0900 <= code <= 0x097F:
            devanagari_count += 1
            letter_count += 1
        elif ch.isalpha():
            letter_count += 1

    if letter_count == 0:
        return "en"

    # If a clear share of letters are Devanagari, treat as Hindi.
    if devanagari_count / letter_count >= 0.3:
        return "hi"

    return "en"