from datetime import date, datetime, timedelta, timezone

from .schemas import Facts


def _esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def facts_to_ics(facts: Facts) -> str:
    """All-day calendar events for every key date, with a reminder 3 days before deadlines."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//apertus-letter-helper//EN", "CALSCALE:GREGORIAN"]
    for i, kd in enumerate(facts.key_dates):
        d = date.fromisoformat(kd.date)
        sender = f" - {facts.sender}" if facts.sender else ""
        lines += [
            "BEGIN:VEVENT",
            f"UID:{kd.date}-{i}@apertus-letter-helper",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{d:%Y%m%d}",
            f"DTEND;VALUE=DATE:{d + timedelta(days=1):%Y%m%d}",
            f"SUMMARY:{_esc(f'[{kd.kind}] {kd.what}{sender}')}",
            f"DESCRIPTION:{_esc(facts.summary_en)}",
        ]
        if kd.kind == "deadline":
            lines += ["BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:Deadline in 3 days", "TRIGGER:-P3D", "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
