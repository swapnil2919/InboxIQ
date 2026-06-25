import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

from utils.parser import search_emails
from utils.ui import avatar_color, initials, format_date
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from services.mailbox import refresh_inbox, has_credentials
from utils.export import export_pdf


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="InboxIQ Inbox",
    page_icon="📧",
    layout="wide",
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>
.block-container{ padding-top:1.2rem; padding-bottom:1rem; }

/* Top toolbar */
.mm-toolbar{
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 18px; border-radius:14px; margin-bottom:14px;
    background:linear-gradient(90deg,#0f172a 0%,#111827 100%);
    border:1px solid #1f2937;
}
.mm-toolbar h2{ margin:0; font-size:20px; font-weight:700; color:#f1f5f9; }
.mm-badge{
    display:inline-flex; align-items:center; gap:6px;
    padding:4px 12px; border-radius:999px; font-size:12px; font-weight:600;
}
.mm-badge.on{ background:rgba(22,163,74,.15); color:#22c55e; border:1px solid rgba(34,197,94,.4); }
.mm-badge.off{ background:rgba(220,38,38,.15); color:#f87171; border:1px solid rgba(248,113,113,.4); }
.mm-sub{ color:#94a3b8; font-size:12px; }

/* Email list card */
.mm-card{
    display:flex; gap:12px; padding:10px 12px; border-radius:12px;
    border:1px solid #1f2937; background:#0f172a; margin-bottom:2px;
}
.mm-avatar{
    flex:0 0 auto; width:42px; height:42px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    color:#fff; font-weight:700; font-size:16px;
}
.mm-meta{ overflow:hidden; }
.mm-sender{ font-size:14px; font-weight:600; color:#e2e8f0;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mm-subject{ font-size:13px; color:#cbd5e1;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mm-preview{ font-size:12px; color:#64748b;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mm-row{ display:flex; align-items:center; gap:8px; }
.mm-date{ font-size:11px; color:#64748b; }
.mm-dot{ width:8px; height:8px; border-radius:50%; background:#3b82f6;
    display:inline-block; flex:0 0 auto; }
.mm-chip{ font-size:11px; color:#93c5fd; }

/* Reader header */
.mm-reader-head{ display:flex; gap:14px; align-items:center; margin-bottom:6px; }
.mm-reader-sub{ color:#94a3b8; font-size:13px; }

/* tighten the inline select buttons */
div[data-testid="stVerticalBlock"] button[kind="secondary"]{
    background:transparent; border:none; color:#3b82f6; padding:2px 0;
    text-align:left; font-size:12px;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SESSION DEFAULTS
# =========================================================

st.session_state.setdefault("auto_refresh", True)
st.session_state.setdefault("refresh_interval", 60)
st.session_state.setdefault("last_refresh", "—")
st.session_state.setdefault("selected_email_index", 0)

# =========================================================
# SIDEBAR (folders)
# =========================================================

with st.sidebar:
    st.title("📧 InboxIQ")

    selected_menu = option_menu(
        menu_title=None,
        options=["Inbox", "Important", "Work", "Finance", "Social"],
        icons=["inbox", "star", "briefcase", "cash-stack", "people"],
        default_index=0,
    )

    st.divider()
    st.toggle("🔄 Live auto-refresh", key="auto_refresh")
    st.select_slider(
        "Check every",
        options=[15, 30, 60, 120, 300],
        format_func=lambda s: f"{s}s" if s < 60 else f"{s // 60}m",
        key="refresh_interval",
    )

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
# TOOLBAR
# =========================================================

emails = st.session_state.get("emails", [])
connected = st.session_state.get("connected", False)

status_cls = "on" if connected else "off"
status_txt = "Connected" if connected else "Disconnected"

bar_left, bar_right = st.columns([4, 1])

with bar_left:
    st.markdown(
        f"""
        <div class="mm-toolbar">
          <div>
            <h2>📥 {selected_menu}</h2>
            <span class="mm-sub">Last sync: {st.session_state.last_refresh}</span>
          </div>
          <span class="mm-badge {status_cls}">● {status_txt}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with bar_right:
    st.write("")
    if st.button("🔄 Refresh now", use_container_width=True, type="primary"):
        if not has_credentials():
            st.warning("Connect your mailbox in Settings first.")
        else:
            with st.spinner("Syncing mailbox..."):
                result = refresh_inbox()
            if result["ok"]:
                if result["new"] > 0:
                    st.toast(f"📬 {result['new']} new email(s)", icon="📬")
                st.rerun()
            else:
                st.error(result["error"])

# =========================================================
# EMPTY STATE
# =========================================================

if not emails:
    st.info(
        "📭 No emails loaded yet. Open **Settings**, connect your mailbox, "
        "then return here — it will keep itself up to date automatically."
    )
    st.stop()


# =========================================================
# FOLDER CATEGORISATION (lightweight heuristic)
# =========================================================

def in_folder(email, folder):
    if folder == "Inbox":
        return True

    text = (
        email.get("subject", "") + " " + email.get("sender_email", "")
    ).lower()

    if folder == "Important":
        return email.get("has_attachment") or not email.get("is_read", False)
    if folder == "Work":
        return any(k in text for k in
                   ["meeting", "project", "task", "report", "deadline", "team"])
    if folder == "Finance":
        return any(k in text for k in
                   ["invoice", "payment", "bank", "receipt", "order", "salary", "transaction"])
    if folder == "Social":
        return any(k in text for k in
                   ["facebook", "instagram", "twitter", "linkedin", "youtube", "x.com"])
    return True


folder_emails = [e for e in emails if in_folder(e, selected_menu)]

# =========================================================
# SEARCH
# =========================================================

search_text = st.text_input(
    "Search", placeholder="🔍 Search sender, subject or content...",
    label_visibility="collapsed",
)

filtered_emails = search_emails(folder_emails, search_text)

if not filtered_emails:
    st.info("No emails match this view.")
    st.stop()

if st.session_state.selected_email_index >= len(filtered_emails):
    st.session_state.selected_email_index = 0

# =========================================================
# MAIN LAYOUT
# =========================================================

left_col, right_col = st.columns([1, 2.4], gap="medium")

# ----------------- EMAIL LIST -----------------

with left_col:
    st.caption(f"{len(filtered_emails)} conversation(s)")

    for idx, email in enumerate(filtered_emails):
        sender = email.get("sender_name", "Unknown") or "Unknown"
        subject = email.get("subject", "No Subject") or "No Subject"
        preview = email.get("preview", "") or ""
        unread = not email.get("is_read", False)
        has_attach = email.get("has_attachment", False)
        date = format_date(email.get("date", ""))

        dot = '<span class="mm-dot"></span>' if unread else ""
        chip = '<span class="mm-chip">📎</span>' if has_attach else ""

        with st.container(border=True):
            st.markdown(
                f"""
                <div class="mm-card" style="border:none;background:transparent;padding:0;margin:0;">
                  <div class="mm-avatar" style="background:{avatar_color(sender)};">
                    {initials(sender)}
                  </div>
                  <div class="mm-meta">
                    <div class="mm-row">{dot}
                      <span class="mm-sender">{sender[:28]}</span>
                    </div>
                    <div class="mm-subject">{subject[:46]}</div>
                    <div class="mm-preview">{preview[:60]}</div>
                    <div class="mm-row">
                      <span class="mm-date">{date}</span> {chip}
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            is_selected = idx == st.session_state.selected_email_index
            if st.button(
                "✓ Open" if is_selected else "Open",
                key=f"open_{idx}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state.selected_email_index = idx
                filtered_emails[idx]["is_read"] = True
                st.rerun()

# ----------------- READER -----------------

selected_email = filtered_emails[st.session_state.selected_email_index]
selected_email["is_read"] = True

with right_col:
    sender_name = selected_email.get("sender_name", "")
    sender_email = selected_email.get("sender_email", "")
    subject = selected_email.get("subject", "")
    date = selected_email.get("date", "")
    body = selected_email.get("body", "")
    html_body = selected_email.get("body_html", "")

    head1, head2 = st.columns([1, 10])

    with head1:
        st.markdown(
            f"""
            <div class="mm-avatar" style="width:52px;height:52px;font-size:20px;
                 background:{avatar_color(sender_name)};">
              {initials(sender_name)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with head2:
        st.markdown(f"### {subject or '(No subject)'}")
        line = f"**{sender_name or 'Unknown sender'}**"
        if sender_email and sender_email != sender_name:
            line += f"  ·  {sender_email}"
        st.markdown(
            f"<div class='mm-reader-sub'>{line}  ·  {format_date(date)}</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    if html_body:
        components.html(
            f"""
            <html><head><style>
                body {{ font-family:Arial, sans-serif; padding:15px;
                        background:#ffffff; color:#111; }}
                img {{ max-width:100%; height:auto; }}
                table {{ max-width:100%; }}
                a {{ color:#2563eb; text-decoration:none; }}
            </style></head>
            <body>{html_body}</body></html>
            """,
            height=720,
            scrolling=True,
        )
    else:
        st.markdown(
            f"""
            <div style="border:1px solid #1f2937;border-radius:12px;padding:16px;
                 background:#0f172a;color:#e2e8f0;">
            {body.replace(chr(10), '<br>') if body else '<em>No content.</em>'}
            </div>
            """,
            unsafe_allow_html=True,
        )

# =========================================================
# ACTION BAR
# =========================================================

st.divider()
action1, action2, action3 = st.columns(3)

with action1:
    if st.button("🤖 AI Summary", use_container_width=True):
        try:
            api_key = st.session_state.get("gemini_key", "")
            if not api_key:
                st.error("Gemini key not configured.")
            else:
                ai = AIService(api_key)
                st.session_state["ai_result"] = ai.full_analysis(
                    selected_email.get("subject", ""),
                    selected_email.get("body", ""),
                )
        except Exception as e:
            st.error(str(e))

with action2:
    if st.button("📱 WhatsApp", use_container_width=True):
        st.session_state["show_whatsapp"] = True

with action3:
    if st.button("📄 Export PDF", use_container_width=True):
        try:
            file_path = export_pdf(selected_email, "email.pdf")
            with open(file_path, "rb") as f:
                st.download_button(
                    "Download PDF",
                    data=f,
                    file_name="email.pdf",
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(str(e))

# =========================================================
# AI RESULT
# =========================================================

if "ai_result" in st.session_state:
    st.divider()
    st.subheader("🤖 AI Analysis")
    st.markdown(st.session_state["ai_result"])

# =========================================================
# WHATSAPP FORM
# =========================================================

if st.session_state.get("show_whatsapp", False):
    st.divider()
    st.subheader("📱 Send To WhatsApp")

    phone = st.text_input(
        "Recipient Number", placeholder="whatsapp:+91XXXXXXXXXX"
    )

    if st.button("Send WhatsApp Message"):
        try:
            wa = WhatsAppService(
                st.session_state.get("account_sid", ""),
                st.session_state.get("auth_token", ""),
                st.session_state.get("twilio_number", ""),
            )
            result = wa.send_email_content(
                phone,
                selected_email.get("subject", ""),
                selected_email.get("body", ""),
            )
            if result.get("success"):
                st.success("Message Sent")
            else:
                st.error(result.get("error", "Failed"))
        except Exception as e:
            st.error(str(e))
