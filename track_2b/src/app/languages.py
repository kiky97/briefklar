"""Language labels for prompts.

Naming the target language in its own script as well as in English (e.g. "Tigrinya (ትግርኛ)")
keeps Apertus on target. With the English name alone, our evaluation showed Tigrinya
output drifting into Amharic (direct generation) or Oromo (translation).
"""

NATIVE_NAMES = {
    "english": "English",
    "ukrainian": "українська",
    "tigrinya": "ትግርኛ",
    "amharic": "አማርኛ",
    "arabic": "العربية",
    "farsi": "فارسی",
    "persian": "فارسی",
    "dari": "دری",
    "pashto": "پښتو",
    "albanian": "shqip",
    "turkish": "Türkçe",
    "portuguese": "português",
    "spanish": "español",
    "tamil": "தமிழ்",
    "somali": "Soomaali",
    "chinese": "中文",
    "kurdish (kurmanji)": "Kurmancî",
    "serbian": "српски",
    "russian": "русский",
    "romansh": "rumantsch",
    "german": "Deutsch",
    "french": "français",
    "italian": "italiano",
}


def label(language: str) -> str:
    """'Tigrinya' -> 'Tigrinya (ትግርኛ)'; unknown or already-annotated names pass through."""
    name = language.strip()
    native = NATIVE_NAMES.get(name.lower())
    if not native or native == name or "(" in name:
        return name
    return f"{name} ({native})"
