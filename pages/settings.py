import streamlit as st
from services.email_service import EmailService

st.title("⚙️ Settings")

st.markdown(
    """
    Configure your Email, AI and WhatsApp settings.

    All settings are stored only in the current session.
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
    "connected": False
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
    placeholder="example@gmail.com"
)

password = st.text_input(
    "App Password",
    value=st.session_state.password,
    type="password"
)

imap_server = st.selectbox(
    "IMAP Server",
    options=[
        "imap.gmail.com",
        "outlook.office365.com",
        "custom"
    ]
)

if imap_server == "custom":

    custom_imap = st.text_input(
        "Custom IMAP Server",
        value=st.session_state.imap_server
    )

    imap_server = custom_imap

email_limit = st.slider(
    "Emails To Load",
    min_value=10,
    max_value=1000,
    value=st.session_state.email_limit,
    step=10
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
    help="Used for AI Email Summaries"
)

st.divider()

# ==========================================
# Twilio Configuration
# ==========================================

st.subheader("📱 WhatsApp Notifications")

account_sid = st.text_input(
    "Twilio Account SID",
    value=st.session_state.account_sid
)

auth_token = st.text_input(
    "Twilio Auth Token",
    value=st.session_state.auth_token,
    type="password"
)

twilio_number = st.text_input(
    "Twilio WhatsApp Number",
    value=st.session_state.twilio_number,
    placeholder="whatsapp:+14155238886"
)

st.divider()

# ==========================================
# Save Settings
# ==========================================

if st.button(
    "💾 Save Settings",
    use_container_width=True
):

    st.session_state.email_id = email_id
    st.session_state.password = password
    st.session_state.imap_server = imap_server
    st.session_state.email_limit = email_limit

    st.session_state.gemini_key = gemini_key

    st.session_state.account_sid = account_sid
    st.session_state.auth_token = auth_token
    st.session_state.twilio_number = twilio_number

    st.success(
        "Settings saved successfully."
    )

# ==========================================
# Connect Mailbox
# ==========================================

st.subheader("🔗 Mailbox Connection")

if st.button(
    "Connect Mailbox",
    use_container_width=True
):

    try:

        with st.spinner(
            "Connecting..."
        ):

            service = EmailService(
                email_id=email_id,
                password=password,
                imap_server=imap_server
            )

            service.connect()

            emails = service.fetch_emails(
                limit=email_limit
            )

            service.disconnect()

        st.session_state.emails = emails
        st.session_state.connected = True

        st.success(
            f"Successfully loaded {len(emails)} emails."
        )

    except Exception as e:

        st.session_state.connected = False

        st.error(
            f"Connection Failed: {str(e)}"
        )

# ==========================================
# Status
# ==========================================

st.divider()

st.subheader("📊 Current Status")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Connection",
        "Connected"
        if st.session_state.connected
        else "Disconnected"
    )

with col2:

    st.metric(
        "Emails Loaded",
        len(
            st.session_state.get(
                "emails",
                []
            )
        )
    )

with col3:

    st.metric(
        "Gemini",
        "Configured"
        if st.session_state.gemini_key
        else "Not Configured"
    )

# ==========================================
# Quick Help
# ==========================================

with st.expander(
    "ℹ️ Setup Help"
):

    st.markdown(
        """
        ### Gmail

        1. Enable 2-Step Verification
        2. Create App Password
        3. Use:
           - IMAP Server: `imap.gmail.com`

        ### Outlook

        Use:
        - IMAP Server:
          `outlook.office365.com`

        ### Gemini

        Generate API key from:
        https://aistudio.google.com

        ### Twilio WhatsApp

        Use:
        - Account SID
        - Auth Token
        - Sandbox WhatsApp Number
        """
    )