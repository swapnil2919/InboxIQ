import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

from utils.parser import search_emails
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from utils.export import export_pdf


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MailMind Inbox",
    page_icon="📧",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

.email-card{
    padding:12px;
    border-radius:12px;
    border:1px solid #2d2d2d;
    margin-bottom:8px;
    background-color:#111827;
}

.email-card:hover{
    border:1px solid #3b82f6;
}

.sender{
    font-size:14px;
    font-weight:600;
}

.subject{
    font-size:13px;
    font-weight:500;
}

.preview{
    font-size:12px;
    color:#9ca3af;
}

.viewer-box{
    border:1px solid #2d2d2d;
    border-radius:12px;
    padding:15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# VALIDATION
# =========================================================

if (
    "emails" not in st.session_state
    or len(st.session_state.emails) == 0
):
    st.warning(
        "No emails loaded. Please connect mailbox from Settings."
    )
    st.stop()

emails = st.session_state.emails

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📧 MailMind")

    selected_menu = option_menu(
        menu_title=None,
        options=[
            "Inbox",
            "Important",
            "Work",
            "Finance",
            "Social"
        ],
        icons=[
            "inbox",
            "star",
            "briefcase",
            "cash-stack",
            "people"
        ],
        default_index=0
    )

# =========================================================
# SEARCH
# =========================================================

search_text = st.text_input(
    "",
    placeholder="🔍 Search emails..."
)

filtered_emails = search_emails(
    emails,
    search_text
)

if len(filtered_emails) == 0:
    st.info("No emails found.")
    st.stop()

# =========================================================
# SESSION STATE
# =========================================================

if (
    "selected_email_index"
    not in st.session_state
):
    st.session_state.selected_email_index = 0

if (
    st.session_state.selected_email_index
    >= len(filtered_emails)
):
    st.session_state.selected_email_index = 0

# =========================================================
# MAIN LAYOUT
# =========================================================

left_col, right_col = st.columns(
    [1, 2.5]
)

# =========================================================
# EMAIL LIST
# =========================================================

with left_col:

    st.subheader(
        f"📥 Inbox ({len(filtered_emails)})"
    )

    for idx, email in enumerate(
        filtered_emails
    ):

        sender = email.get(
            "sender_name",
            "Unknown"
        )

        subject = email.get(
            "subject",
            "No Subject"
        )

        preview = email.get(
            "preview",
            ""
        )

        button_text = (
            f"📧 {sender[:30]}"
        )

        if st.button(
            button_text,
            key=f"mail_{idx}",
            use_container_width=True
        ):
            st.session_state.selected_email_index = idx

        st.caption(subject[:70])

        if preview:
            st.caption(preview[:90])

        st.divider()

# =========================================================
# SELECTED EMAIL
# =========================================================

selected_email = (
    filtered_emails[
        st.session_state.selected_email_index
    ]
)

# =========================================================
# EMAIL VIEWER
# =========================================================

with right_col:

    sender_name = selected_email.get(
        "sender_name",
        ""
    )

    sender_email = selected_email.get(
        "sender_email",
        ""
    )

    subject = selected_email.get(
        "subject",
        ""
    )

    date = selected_email.get(
        "date",
        ""
    )

    body = selected_email.get(
        "body",
        ""
    )

    html_body = selected_email.get(
        "body_html",
        ""
    )

    avatar = (
        sender_name[0].upper()
        if sender_name
        else "?"
    )

    head1, head2 = st.columns(
        [1, 10]
    )

    with head1:

        st.markdown(
            f"""
            <div style="
            width:50px;
            height:50px;
            border-radius:50%;
            background:#2563eb;
            color:white;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:24px;
            font-weight:bold;
            ">
            {avatar}
            </div>
            """,
            unsafe_allow_html=True
        )

    with head2:

        st.markdown(
            f"## {subject}"
        )

        st.write(
            f"**{sender_name}**"
        )

        if sender_email:
            st.caption(
                sender_email
            )

        st.caption(
            date
        )

    st.divider()

    # =====================================
    # HTML EMAIL RENDERING
    # =====================================

    if html_body:

        components.html(
            f"""
            <html>
            <head>
                <style>

                    body {{
                        font-family:Arial;
                        padding:15px;
                        background:white;
                        color:black;
                    }}

                    img {{
                        max-width:100%;
                        height:auto;
                    }}

                    table {{
                        max-width:100%;
                    }}

                    a {{
                        color:#2563eb;
                        text-decoration:none;
                    }}

                </style>
            </head>

            <body>
                {html_body}
            </body>

            </html>
            """,
            height=800,
            scrolling=True
        )

    else:

        st.markdown(
            f"""
            <div class="viewer-box">
            {body.replace(chr(10), '<br>')}
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# ACTION BAR
# =========================================================

st.divider()

action1, action2, action3 = st.columns(
    3
)

# =========================================================
# AI SUMMARY
# =========================================================

with action1:

    if st.button(
        "🤖 AI Summary",
        use_container_width=True
    ):

        try:

            api_key = (
                st.session_state.get(
                    "gemini_key",
                    ""
                )
            )

            if not api_key:

                st.error(
                    "Gemini key not configured."
                )

            else:

                ai = AIService(
                    api_key
                )

                result = (
                    ai.full_analysis(
                        subject,
                        body
                    )
                )

                st.session_state[
                    "ai_result"
                ] = result

        except Exception as e:

            st.error(
                str(e)
            )

# =========================================================
# WHATSAPP
# =========================================================

with action2:

    if st.button(
        "📱 WhatsApp",
        use_container_width=True
    ):

        st.session_state[
            "show_whatsapp"
        ] = True

# =========================================================
# PDF EXPORT
# =========================================================

with action3:

    if st.button(
        "📄 Export PDF",
        use_container_width=True
    ):

        try:

            file_path = export_pdf(
                selected_email,
                "email.pdf"
            )

            with open(
                file_path,
                "rb"
            ) as f:

                st.download_button(
                    "Download PDF",
                    data=f,
                    file_name="email.pdf",
                    mime="application/pdf"
                )

        except Exception as e:

            st.error(
                str(e)
            )

# =========================================================
# AI RESULT
# =========================================================

if (
    "ai_result"
    in st.session_state
):

    st.divider()

    st.subheader(
        "🤖 AI Analysis"
    )

    st.markdown(
        st.session_state[
            "ai_result"
        ]
    )

# =========================================================
# WHATSAPP FORM
# =========================================================

if st.session_state.get(
    "show_whatsapp",
    False
):

    st.divider()

    st.subheader(
        "📱 Send To WhatsApp"
    )

    phone = st.text_input(
        "Recipient Number",
        placeholder="whatsapp:+91XXXXXXXXXX"
    )

    if st.button(
        "Send WhatsApp Message"
    ):

        try:

            wa = WhatsAppService(
                st.session_state.get(
                    "account_sid",
                    ""
                ),
                st.session_state.get(
                    "auth_token",
                    ""
                ),
                st.session_state.get(
                    "twilio_number",
                    ""
                )
            )

            result = (
                wa.send_email_content(
                    phone,
                    subject,
                    body
                )
            )

            if result.get(
                "success"
            ):
                st.success(
                    "Message Sent"
                )
            else:
                st.error(
                    result.get(
                        "error",
                        "Failed"
                    )
                )

        except Exception as e:

            st.error(
                str(e)
            )