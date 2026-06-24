import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MailMind",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE DEFAULTS
# =========================================================

defaults = {
    "connected": False,
    "emails": [],
    "email_id": "",
    "password": "",
    "imap_server": "imap.gmail.com",
    "gemini_key": "",
    "account_sid": "",
    "auth_token": "",
    "twilio_number": ""
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

.metric-card{
    padding:20px;
    border-radius:12px;
    border:1px solid #2d2d2d;
    background:#111827;
}

.dashboard-card{
    padding:20px;
    border-radius:12px;
    border:1px solid #2d2d2d;
    background:#111827;
    margin-bottom:15px;
}

.big-title{
    font-size:42px;
    font-weight:700;
}

.small-text{
    color:#9ca3af;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📧 MailMind")

    st.caption(
        "AI Powered Email Intelligence"
    )

    st.divider()

    if st.session_state.connected:

        st.success(
            "🟢 Connected"
        )

    else:

        st.warning(
            "🔴 Not Connected"
        )

    st.divider()

    st.markdown(
        """
### Navigation

⚙️ Settings

📥 Inbox

📊 Analytics
"""
    )

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
<div class="big-title">
📧 MailMind
</div>
""",
    unsafe_allow_html=True
)

st.caption(
    "AI Powered Email Dashboard"
)

st.divider()

# =========================================================
# KPIs
# =========================================================

emails = st.session_state.get(
    "emails",
    []
)

total_emails = len(
    emails
)

unique_senders = len(
    set(
        [
            email.get(
                "sender_name",
                email.get(
                    "from",
                    ""
                )
            )
            for email in emails
        ]
    )
)

attachments = len(
    [
        email
        for email in emails
        if email.get(
            "has_attachment",
            False
        )
    ]
)

col1, col2, col3, col4 = st.columns(
    4
)

with col1:

    st.metric(
        "📧 Emails",
        total_emails
    )

with col2:

    st.metric(
        "👤 Senders",
        unique_senders
    )

with col3:

    st.metric(
        "📎 Attachments",
        attachments
    )

with col4:

    st.metric(
        "🤖 AI",
        "Enabled"
        if st.session_state.gemini_key
        else "Disabled"
    )

st.divider()

# =========================================================
# DASHBOARD
# =========================================================

left_col, right_col = st.columns(
    [2, 1]
)

# =========================================================
# LEFT SIDE
# =========================================================

with left_col:

    st.subheader(
        "📨 Recent Emails"
    )

    if len(emails) == 0:

        st.info(
            "No emails loaded yet."
        )

    else:

        recent_emails = []

        for email in emails[:10]:

            recent_emails.append(
                {
                    "Sender":
                    email.get(
                        "sender_name",
                        ""
                    ),

                    "Subject":
                    email.get(
                        "subject",
                        ""
                    ),

                    "Date":
                    email.get(
                        "date",
                        ""
                    )
                }
            )

        st.dataframe(
            pd.DataFrame(
                recent_emails
            ),
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# RIGHT SIDE
# =========================================================

with right_col:

    st.subheader(
        "⚡ Quick Actions"
    )

    st.info(
        """
📥 Open Inbox

📊 View Analytics

⚙️ Configure Mailbox

🤖 Generate AI Summary

📱 Send WhatsApp Alerts
"""
    )

    st.subheader(
        "📈 System Status"
    )

    st.metric(
        "Connection",
        "Connected"
        if st.session_state.connected
        else "Disconnected"
    )

    st.metric(
        "Loaded Emails",
        len(emails)
    )

# =========================================================
# EMAIL DOMAIN ANALYSIS
# =========================================================

if len(emails) > 0:

    st.divider()

    st.subheader(
        "🌐 Top Domains"
    )

    domains = []

    for email in emails:

        sender_email = email.get(
            "sender_email",
            ""
        )

        if "@" in sender_email:

            domain = (
                sender_email
                .split("@")[-1]
                .replace(">", "")
                .strip()
            )

            domains.append(
                domain
            )

    if len(domains) > 0:

        domain_df = (
            pd.Series(domains)
            .value_counts()
            .head(10)
            .reset_index()
        )

        domain_df.columns = [
            "Domain",
            "Emails"
        ]

        st.dataframe(
            domain_df,
            use_container_width=True,
            hide_index=True
        )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "MailMind v1.0 • AI Email Dashboard"
)