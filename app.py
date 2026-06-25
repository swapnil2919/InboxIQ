import streamlit as st
import pandas as pd

from utils.storage import load_credentials
from services.mailbox import refresh_inbox, has_credentials

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="InboxIQ",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded",
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
    "email_limit": 100,
    "gemini_key": "",
    "account_sid": "",
    "auth_token": "",
    "twilio_number": "",
    "auto_refresh": True,
    "refresh_interval": 60,
    "last_refresh": "—",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# BOOTSTRAP: load saved credentials + auto-connect once
# =========================================================

if not st.session_state.get("_bootstrapped"):
    st.session_state._bootstrapped = True

    saved = load_credentials()
    for key, value in saved.items():
        if value:
            st.session_state[key] = value

    # Auto-connect silently so the user does NOT re-enter the app password.
    if has_credentials() and not st.session_state.connected:
        try:
            refresh_inbox()
        except Exception:
            pass

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>
.block-container{ padding-top:1rem; padding-bottom:1rem; }

.mm-hero{
    padding:24px 28px; border-radius:18px; margin-bottom:8px;
    background:linear-gradient(120deg,#1e1b4b 0%,#0f172a 55%,#111827 100%);
    border:1px solid #1f2937;
}
.mm-hero .title{ font-size:34px; font-weight:800; color:#f8fafc;
    display:flex; align-items:center; gap:12px; letter-spacing:.3px; }
.mm-hero .subtitle{ color:#94a3b8; font-size:14px; margin-top:4px; }
.mm-hero .pill{
    display:inline-flex; align-items:center; gap:6px; margin-top:12px;
    padding:5px 14px; border-radius:999px; font-size:12px; font-weight:600;
}
.pill.on{ background:rgba(34,197,94,.15); color:#22c55e; border:1px solid rgba(34,197,94,.4); }
.pill.off{ background:rgba(248,113,113,.15); color:#f87171; border:1px solid rgba(248,113,113,.4); }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.title("📧 InboxIQ")
    st.caption("AI Powered Email Intelligence")
    st.divider()

    if st.session_state.connected:
        st.success("🟢 Connected")
    else:
        st.warning("🔴 Not Connected")

    st.toggle("🔄 Live auto-refresh", key="auto_refresh")

    st.divider()
    st.markdown("### Navigation")
    st.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.page_link("pages/inbox.py", label="Inbox", icon="📥")
    st.page_link("pages/analytics.py", label="Analytics", icon="📊")

# =========================================================
# LIVE AUTO-REFRESH POLL
# =========================================================


@st.fragment(
    run_every=(
        st.session_state.refresh_interval
        if st.session_state.auto_refresh and has_credentials()
        else None
    )
)
def _live_poll():
    if not (st.session_state.auto_refresh and has_credentials()):
        return
    result = refresh_inbox()
    if result["ok"] and result["new"] > 0:
        st.toast(f"📬 {result['new']} new email(s) arrived", icon="📬")
        st.rerun()


_live_poll()

# =========================================================
# HERO HEADER
# =========================================================

pill_cls = "on" if st.session_state.connected else "off"
pill_txt = "Connected" if st.session_state.connected else "Not connected"

head_left, head_right = st.columns([4, 1])

with head_left:
    st.markdown(
        f"""
        <div class="mm-hero">
          <div class="title">📧 InboxIQ</div>
          <div class="subtitle">AI Powered Email Dashboard · stays in sync automatically</div>
          <span class="pill {pill_cls}">● {pill_txt}  ·  last sync {st.session_state.last_refresh}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with head_right:
    st.write("")
    st.write("")
    if st.button("🔄 Refresh", use_container_width=True, type="primary"):
        if not has_credentials():
            st.warning("Connect your mailbox in Settings first.")
        else:
            with st.spinner("Syncing..."):
                result = refresh_inbox()
            if result["ok"]:
                if result["new"] > 0:
                    st.toast(f"📬 {result['new']} new email(s)", icon="📬")
                st.rerun()
            else:
                st.error(result["error"])

st.divider()

# =========================================================
# KPIs
# =========================================================

emails = st.session_state.get("emails", [])
total_emails = len(emails)

unique_senders = len(
    {email.get("sender_name", email.get("from", "")) for email in emails}
)

attachments = len([e for e in emails if e.get("has_attachment", False)])

col1, col2, col3, col4 = st.columns(4)
col1.metric("📧 Emails", total_emails)
col2.metric("👤 Senders", unique_senders)
col3.metric("📎 Attachments", attachments)
col4.metric(
    "🤖 AI", "Enabled" if st.session_state.gemini_key else "Disabled"
)

st.divider()

# =========================================================
# DASHBOARD
# =========================================================

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📨 Recent Emails")

    if total_emails == 0:
        st.info("No emails loaded yet. Connect your mailbox in Settings.")
    else:
        recent_emails = [
            {
                "Sender": email.get("sender_name", ""),
                "Subject": email.get("subject", ""),
                "Date": email.get("date", ""),
            }
            for email in emails[:10]
        ]
        st.dataframe(
            pd.DataFrame(recent_emails),
            use_container_width=True,
            hide_index=True,
        )

with right_col:
    st.subheader("⚡ Quick Actions")
    st.page_link("pages/inbox.py", label="Open Inbox", icon="📥")
    st.page_link("pages/analytics.py", label="View Analytics", icon="📊")
    st.page_link("pages/settings.py", label="Configure Mailbox", icon="⚙️")

    st.subheader("📈 System Status")
    st.metric(
        "Connection",
        "Connected" if st.session_state.connected else "Disconnected",
    )
    st.metric("Loaded Emails", total_emails)

# =========================================================
# EMAIL DOMAIN ANALYSIS
# =========================================================

if total_emails > 0:
    st.divider()
    st.subheader("🌐 Top Domains")

    domains = []
    for email in emails:
        sender_email = email.get("sender_email", "")
        if "@" in sender_email:
            domains.append(
                sender_email.split("@")[-1].replace(">", "").strip()
            )

    if domains:
        domain_df = (
            pd.Series(domains).value_counts().head(10).reset_index()
        )
        domain_df.columns = ["Domain", "Emails"]
        st.dataframe(
            domain_df, use_container_width=True, hide_index=True
        )

# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption("InboxIQ v1.1 • AI Email Dashboard")
