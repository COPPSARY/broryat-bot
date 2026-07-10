from typing import Literal

_KHMER_RANGE = (0x1780, 0x17FF)


def detect_language(text: str) -> Literal["km", "en"]:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return "en"

    khmer_count = sum(1 for ch in letters if _KHMER_RANGE[0] <= ord(ch) <= _KHMER_RANGE[1])
    return "km" if khmer_count / len(letters) > 0.5 else "en"
