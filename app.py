import streamlit as st

st.set_page_config(
    page_title="Email Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Session State Initialization
# ==========================================

defaults = {
    "connected": False,
    "emails": [],
    "email_id": "",
    "password": "",
    "imap_server": "imap.gmail.com",
    "gemini_key": "",
    "account_sid": "",
    "auth_token": "",
    "twilio_number": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.title("📧 Email Dashboard")

    if st.session_state.connected:
        st.success("Connected")
    else:
        st.warning("Not Connected")

    st.divider()

    st.markdown("""
    ### Navigation

    Use Streamlit Pages:

    ⚙️ Settings

    📥 Inbox

    📊 Analytics
    """)

    st.divider()

    st.markdown("### Current Status")

    st.metric(
        "Emails Loaded",
        len(st.session_state.emails)
    )

# ==========================================
# Header
# ==========================================

st.title("📧 Email Dashboard")

st.caption(
    "Gmail • Outlook • AI Summary • WhatsApp Notifications"
)

# ==========================================
# Dashboard Cards
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Connection",
        "Active" if st.session_state.connected else "Offline"
    )

with col2:
    st.metric(
        "Inbox Emails",
        len(st.session_state.emails)
    )

with col3:
    st.metric(
        "AI Summary",
        "Enabled"
        if st.session_state.gemini_key
        else "Disabled"
    )

with col4:
    st.metric(
        "WhatsApp",
        "Enabled"
        if st.session_state.account_sid
        else "Disabled"
    )

st.divider()

# ==========================================
# Main Content
# ==========================================

if not st.session_state.connected:

    st.info(
        """
        Welcome to Email Dashboard.

        To get started:

        1. Open **Settings**
        2. Enter your Email
        3. Enter App Password
        4. Enter IMAP Server
        5. Click Connect
        """
    )

    st.code("""
Gmail IMAP:
imap.gmail.com

Outlook IMAP:
outlook.office365.com
""")

else:

    st.success(
        f"Connected as {st.session_state.email_id}"
    )

    st.subheader("Quick Overview")

    total_emails = len(
        st.session_state.emails
    )

    senders = set()

    for email in st.session_state.emails:
        senders.add(
            email.get("from", "")
        )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total Emails",
            total_emails
        )

    with col2:

        st.metric(
            "Unique Senders",
            len(senders)
        )

    st.divider()

    st.subheader("Recent Emails")

    preview_data = []

    for item in st.session_state.emails[:10]:

        preview_data.append(
            {
                "From": item.get(
                    "from",
                    ""
                ),
                "Subject": item.get(
                    "subject",
                    ""
                ),
                "Date": item.get(
                    "date",
                    ""
                )
            }
        )

    if preview_data:
        st.dataframe(
            preview_data,
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "Email Dashboard v1.0 | Streamlit + IMAP + Gemini + Twilio"
)