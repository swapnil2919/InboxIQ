"""
High level mailbox helpers.

This module is the single place that knows how to (re)connect to the
mailbox using the credentials already stored in the Streamlit session.
Both the manual "Refresh" buttons and the live auto-refresh poll call
into here, so the user never has to re-enter their email / app password.
"""

from datetime import datetime

import streamlit as st

from services.email_service import EmailService


def has_credentials() -> bool:
    """True when we have enough to connect without asking the user again."""
    return bool(
        st.session_state.get("email_id")
        and st.session_state.get("password")
        and st.session_state.get("imap_server")
    )


def fetch_emails():
    """Connect with the session credentials, fetch, and disconnect."""
    service = EmailService(
        email_id=st.session_state.get("email_id", ""),
        password=st.session_state.get("password", ""),
        imap_server=st.session_state.get("imap_server", "imap.gmail.com"),
    )

    service.connect()

    try:
        emails = service.fetch_emails(
            limit=int(st.session_state.get("email_limit", 100))
        )
    finally:
        service.disconnect()

    return emails


def refresh_inbox():
    """
    Re-fetch the inbox using stored credentials.

    Returns a dict:
        {
            "ok": bool,
            "new": <count of newly arrived emails>,
            "total": <count after refresh>,
            "error": <message when ok is False>,
        }
    """
    if not has_credentials():
        return {
            "ok": False,
            "new": 0,
            "total": len(st.session_state.get("emails", [])),
            "error": "No saved mailbox credentials.",
        }

    previous_ids = {
        email.get("id")
        for email in st.session_state.get("emails", [])
    }

    try:
        emails = fetch_emails()
    except Exception as exc:
        st.session_state.connected = False
        return {
            "ok": False,
            "new": 0,
            "total": len(st.session_state.get("emails", [])),
            "error": str(exc),
        }

    new_count = len([
        email
        for email in emails
        if email.get("id") not in previous_ids
    ])

    st.session_state.emails = emails
    st.session_state.connected = True
    st.session_state.last_refresh = datetime.now().strftime("%b %d, %H:%M:%S")

    return {
        "ok": True,
        "new": new_count,
        "total": len(emails),
        "error": "",
    }
