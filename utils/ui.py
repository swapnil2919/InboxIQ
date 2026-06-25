"""
Small presentation helpers shared across pages.
"""

from datetime import datetime
from email.utils import parsedate_to_datetime


# Palette used to colour sender avatars deterministically.
_AVATAR_COLORS = [
    "#2563eb", "#7c3aed", "#db2777", "#dc2626",
    "#ea580c", "#d97706", "#16a34a", "#0891b2",
    "#4f46e5", "#0d9488",
]


def avatar_color(name: str) -> str:
    if not name:
        return _AVATAR_COLORS[0]
    return _AVATAR_COLORS[sum(ord(c) for c in name) % len(_AVATAR_COLORS)]


def initials(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "?"
    parts = [p for p in name.replace('"', "").split() if p]
    if not parts:
        return name[0].upper()
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[1][0]).upper()


def format_date(raw) -> str:
    """Return a clean 'Jun 24, 14:30' style date from many input formats."""
    if not raw:
        return ""

    raw = str(raw)

    # Try RFC 2822 email header first.
    try:
        return parsedate_to_datetime(raw).strftime("%b %d, %H:%M")
    except Exception:
        pass

    # Try ISO / str(datetime) form, e.g. '2025-06-24 14:30:00+00:00'.
    try:
        return datetime.fromisoformat(raw).strftime("%b %d, %H:%M")
    except Exception:
        pass

    return raw[:16]
