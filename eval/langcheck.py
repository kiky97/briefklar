"""Cheap, deterministic check that an explanation is written in the requested language.

Two levels:
1. Script: the share of letters belonging to the expected writing system.
2. For Ge'ez (Ethiopic) script, telling Tigrinya from Amharic using high-frequency
   function words and orthography. The two languages share a script, and in our runs
   Apertus drifted from Tigrinya into Amharic. This is a heuristic, not a full language
   identifier: it reports evidence counts so the result can be audited.
"""

import re
import unicodedata

SCRIPT_OF = {
    "ukrainian": "CYRILLIC", "russian": "CYRILLIC", "bulgarian": "CYRILLIC",
    "arabic": "ARABIC", "farsi": "ARABIC", "persian": "ARABIC", "dari": "ARABIC", "pashto": "ARABIC", "urdu": "ARABIC",
    "tigrinya": "ETHIOPIC", "amharic": "ETHIOPIC",
    "tamil": "TAMIL", "chinese": "CJK", "greek": "GREEK", "hindi": "DEVANAGARI",
}

# Function words / spellings that are characteristic of one language and rare in the other.
TIGRINYA_MARKERS = ["እዩ", "እዚ", "እንታይ", "ኣለካ", "ኣለኩም", "ኣለዎ", "ናይ", "ክሳብ", "ብዛዕባ", "ኣብ", "ምስ", "ኢዩ", "ከምኡ", "እንተ", "ኣይ"]
AMHARIC_MARKERS = ["ነው", "ይህ", "ምን", "አለብኝ", "አለብዎት", "እስከ", "ያድርጉ", "የሚ", "እባክዎ", "ከሆነ", "ይችላል", "እርስዎ"]
# Orthography: Tigrinya writes the glottal "a" as ኣ (U+12A3), Amharic as አ (U+12A0).
TIGRINYA_LETTER, AMHARIC_LETTER = "ኣ", "አ"


def _script(ch: str) -> str | None:
    if not ch.isalpha():
        return None
    name = unicodedata.name(ch, "")
    if name.startswith("CJK"):
        return "CJK"
    for script in ("CYRILLIC", "ARABIC", "ETHIOPIC", "TAMIL", "GREEK", "DEVANAGARI"):
        if name.startswith(script):
            return script
    return "LATIN" if "LATIN" in name else "OTHER"


def _count(text: str, words: list[str]) -> int:
    return sum(len(re.findall(re.escape(w), text)) for w in words)


def check_language(text: str, language: str) -> dict:
    lang = language.split("(")[0].strip().lower()
    expected = SCRIPT_OF.get(lang, "LATIN")
    # Ignore quoted original terms like (Einsprache) and amounts/dates.
    body = re.sub(r"\([^)]*\)", " ", text)
    scripts = [s for s in map(_script, body) if s]
    share = sum(s == expected for s in scripts) / len(scripts) if scripts else 0.0
    result = {"expected_script": expected, "script_share": round(share, 3), "language_ok": share >= 0.6}
    if expected == "ETHIOPIC":
        ti = _count(body, TIGRINYA_MARKERS) + body.count(TIGRINYA_LETTER)
        am = _count(body, AMHARIC_MARKERS) + body.count(AMHARIC_LETTER)
        guess = "tigrinya" if ti > am else "amharic" if am > ti else "unclear"
        result.update({"tigrinya_markers": ti, "amharic_markers": am, "detected": guess})
        result["language_ok"] = result["language_ok"] and guess == lang
    return result
