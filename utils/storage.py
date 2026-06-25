"""
Local credential persistence for InboxIQ.

Stores connection settings in a gitignored JSON file so the user does
NOT have to re-enter their email + app password every time the app is
restarted or a new email arrives.

Note: values are base64 obfuscated, not encrypted. This is a personal,
local-only convenience store. The file is added to .gitignore.
"""

import os
import json
import base64


STORE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    ".InboxIQ_credentials.json"
)

# Fields that we persist between sessions.
FIELDS = [
    "email_id",
    "password",
    "imap_server",
    "email_limit",
    "gemini_key",
    "account_sid",
    "auth_token",
    "twilio_number",
]


def _encode(value):
    try:
        return base64.b64encode(str(value).encode()).decode()
    except Exception:
        return ""


def _decode(value):
    try:
        return base64.b64decode(str(value).encode()).decode()
    except Exception:
        return ""


def save_credentials(data: dict):
    """Persist selected fields to the local store."""
    payload = {key: _encode(data.get(key, "")) for key in FIELDS}

    try:
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        return True
    except Exception:
        return False


def load_credentials() -> dict:
    """Load persisted fields. Returns {} when nothing is stored."""
    if not os.path.exists(STORE_FILE):
        return {}

    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {}

    result = {}

    for key in FIELDS:
        value = _decode(raw.get(key, ""))

        if key == "email_limit":
            try:
                value = int(value) if value else 100
            except Exception:
                value = 100

        result[key] = value

    return result


def clear_credentials():
    """Delete the local credential store ('forget me')."""
    try:
        if os.path.exists(STORE_FILE):
            os.remove(STORE_FILE)
        return True
    except Exception:
        return False


def has_saved_credentials() -> bool:
    return os.path.exists(STORE_FILE)
