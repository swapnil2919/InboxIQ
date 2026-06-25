import streamlit as st

from services.mailbox import refresh_inbox
from utils.storage import (
    save_credentials,
    clear_credentials,
    has_saved_credentials,
)

st.title("⚙️ Settings")

st.markdown(
    """
    Configure your Email, AI and WhatsApp settings.

    Enable **Remember on this device** so you never have to re-enter your
    app password again — the inbox then stays connected and refreshes by itself.
    """
)

# ==========================================
# Session Defaults
# ==========================================

defaults = {
    "email_id": "",
    "password": "",
    "imap_server": "imap.gmail.com",
    "email_limit": 100,
    "gemini_key": "",
    "account_sid": "",
    "auth_token": "",
    "twilio_number": "",
    "connected": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================
# Email Configuration
# ==========================================

st.subheader("📧 Email Configuration")

email_id = st.text_input(
    "Email Address",
    value=st.session_state.email_id,
    placeholder="example@gmail.com",
)

password = st.text_input(
    "App Password",
    value=st.session_state.password,
    type="password",
)

imap_options = ["imap.gmail.com", "outlook.office365.com", "custom"]
current_imap = st.session_state.imap_server
default_idx = (
    imap_options.index(current_imap)
    if current_imap in imap_options
    else 2
)

imap_server = st.selectbox(
    "IMAP Server", options=imap_options, index=default_idx
)

if imap_server == "custom":
    imap_server = st.text_input(
        "Custom IMAP Server", value=st.session_state.imap_server
    )

email_limit = st.slider(
    "Emails To Load",
    min_value=10,
    max_value=1000,
    value=int(st.session_state.email_limit),
    step=10,
)

remember = st.checkbox(
    "💾 Remember on this device (skip re-entering the app password)",
    value=has_saved_credentials(),
)

st.divider()

# ==========================================
# Gemini Configuration
# ==========================================

st.subheader("🤖 Gemini AI")

gemini_key = st.text_input(
    "Gemini API Key",
    value=st.session_state.gemini_key,
    type="password",
    help="Used for AI Email Summaries",
)

st.divider()

# ==========================================
# Twilio Configuration
# ==========================================

st.subheader("📱 WhatsApp Notifications")

account_sid = st.text_input(
    "Twilio Account SID", value=st.session_state.account_sid
)

auth_token = st.text_input(
    "Twilio Auth Token",
    value=st.session_state.auth_token,
    type="password",
)

twilio_number = st.text_input(
    "Twilio WhatsApp Number",
    value=st.session_state.twilio_number,
    placeholder="whatsapp:+14155238886",
)

st.divider()


# ==========================================
# Helper: push widget values into session
# ==========================================

def _commit_to_session():
    st.session_state.email_id = email_id
    st.session_state.password = password
    st.session_state.imap_server = imap_server
    st.session_state.email_limit = email_limit
    st.session_state.gemini_key = gemini_key
    st.session_state.account_sid = account_sid
    st.session_state.auth_token = auth_token
    st.session_state.twilio_number = twilio_number


def _persist_if_remembered():
    if remember:
        save_credentials(
            {
                "email_id": email_id,
                "password": password,
                "imap_server": imap_server,
                "email_limit": email_limit,
                "gemini_key": gemini_key,
                "account_sid": account_sid,
                "auth_token": auth_token,
                "twilio_number": twilio_number,
            }
        )
    else:
        clear_credentials()


# ==========================================
# Save / Connect / Forget
# ==========================================

btn1, btn2, btn3 = st.columns(3)

with btn1:
    if st.button("💾 Save Settings", use_container_width=True):
        _commit_to_session()
        _persist_if_remembered()
        st.success("Settings saved.")

with btn2:
    if st.button(
        "🔗 Connect Mailbox", use_container_width=True, type="primary"
    ):
        _commit_to_session()
        _persist_if_remembered()
        with st.spinner("Connecting..."):
            result = refresh_inbox()
        if result["ok"]:
            st.success(f"Connected — loaded {result['total']} emails.")
        else:
            st.error(f"Connection Failed: {result['error']}")

with btn3:
    if st.button("🗑️ Forget Saved", use_container_width=True):
        clear_credentials()
        st.info("Saved credentials removed from this device.")

# ==========================================
# Status
# ==========================================

st.divider()
st.subheader("📊 Current Status")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Connection",
    "Connected" if st.session_state.connected else "Disconnected",
)
col2.metric("Emails Loaded", len(st.session_state.get("emails", [])))
col3.metric(
    "Remembered", "Yes" if has_saved_credentials() else "No"
)

# ==========================================
# Quick Help
# ==========================================

with st.expander("ℹ️ Setup Help"):
    st.markdown(
        """
        ### Gmail
        1. Enable 2-Step Verification
        2. Create an App Password
        3. IMAP Server: `imap.gmail.com`

        ### Outlook
        IMAP Server: `outlook.office365.com`

        ### Gemini
        Generate an API key at https://aistudio.google.com

        ### Twilio WhatsApp
        Use Account SID, Auth Token and the Sandbox WhatsApp number.
        """
    )
