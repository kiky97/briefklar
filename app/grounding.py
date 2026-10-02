"""Deterministic helpers that check LLM output against the letter text.

The LLM is never trusted on its own for dates and amounts: every extracted value is
re-checked against what is literally written in the letter, and unverified values are
flagged to the user.
"""

import re
import unicodedata
from datetime import date

MONTHS = {
    # German
    "januar": 1, "jänner": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4, "mai": 5,
    "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11,
    "dezember": 12,
    # French
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "juin": 6,
    "juillet": 7, "août": 8, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
    "décembre": 12, "decembre": 12,
    # Italian
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
    "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "dicembre": 12,
    # English
    "january": 1, "february": 2, "march": 3, "may": 5, "june": 6, "july": 7,
    "october": 10, "december": 12,
}

_MONTH_ALT = "|".join(sorted(MONTHS, key=len, reverse=True))
_NUMERIC_DATE = re.compile(r"(?<!\d)(\d{1,2})\s?[./]\s?(\d{1,2})\s?[./]\s?(\d{4})(?!\d)")
_ISO_DATE = re.compile(r"(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)")
_NAMED_DATE = re.compile(
    rf"(?<!\d)(\d{{1,2}})(?:er|\.|º|°)?\s+({_MONTH_ALT})\s+(\d{{4}})(?!\d)", re.IGNORECASE
)
_NUMBER = re.compile(r"(?<![\d])(\d{1,3}(?:['’ ]\d{3})+|\d+)(?:[.,](\d{1,2}))?(?!\d)")


def normalize_digits(text: str) -> str:
    """Map non-ASCII decimal digits (Arabic-Indic, Persian, Devanagari, ...) to 0-9."""
    out = []
    for ch in text:
        if not ch.isascii() and ch.isdigit():
            try:
                out.append(str(unicodedata.decimal(ch)))
                continue
            except ValueError:
                pass
        out.append(ch)
    return "".join(out)


def _safe_date(y: int, m: int, d: int) -> date | None:
    try:
        return date(y, m, d)
    except ValueError:
        return None


def parse_date(value: str) -> date | None:
    """Parse one date string in ISO, DD.MM.YYYY, DD/MM/YYYY or 'D. Monat YYYY' form."""
    value = normalize_digits(value.strip())
    if m := _ISO_DATE.fullmatch(value):
        return _safe_date(int(m[1]), int(m[2]), int(m[3]))
    if m := _NUMERIC_DATE.fullmatch(value):
        return _safe_date(int(m[3]), int(m[2]), int(m[1]))
    if m := _NAMED_DATE.fullmatch(value):
        return _safe_date(int(m[3]), MONTHS[m[2].lower()], int(m[1]))
    return None


def find_dates(text: str) -> set[date]:
    text = normalize_digits(text)
    found: set[date] = set()
    for m in _NUMERIC_DATE.finditer(text):
        if d := _safe_date(int(m[3]), int(m[2]), int(m[1])):
            found.add(d)
    for m in _ISO_DATE.finditer(text):
        if d := _safe_date(int(m[1]), int(m[2]), int(m[3])):
            found.add(d)
    for m in _NAMED_DATE.finditer(text):
        if d := _safe_date(int(m[3]), MONTHS[m[2].lower()], int(m[1])):
            found.add(d)
    return found


def parse_amount(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    m = _NUMBER.search(normalize_digits(str(value)))
    if not m:
        return None
    whole = re.sub(r"['’ ]", "", m[1])
    cents = m[2] or "0"
    return float(f"{whole}.{cents}")


def find_amounts(text: str) -> set[float]:
    text = normalize_digits(text)
    amounts = set()
    for m in _NUMBER.finditer(text):
        whole = re.sub(r"['’ ]", "", m[1])
        amounts.add(round(float(f"{whole}.{m[2] or '0'}"), 2))
    return amounts


def amount_in(value: float, amounts: set[float]) -> bool:
    return any(abs(value - a) < 0.005 for a in amounts)
