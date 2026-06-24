import streamlit as st

from utils.parser import search_emails
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from utils.export import export_pdf, export_csv

# ==========================================
# Validation
# ==========================================

st.title("📥 Inbox")

if (
    "emails" not in st.session_state
    or len(st.session_state.emails) == 0
):

    st.warning(
        "No emails found. Connect your mailbox from Settings."
    )

    st.stop()

emails = st.session_state.emails

# ==========================================
# Search Bar
# ==========================================

search_text = st.text_input(
    "🔍 Search Email",
    placeholder="Search by sender, subject or content..."
)

filtered_emails = search_emails(
    emails,
    search_text
)

# ==========================================
# Layout
# ==========================================

left_col, right_col = st.columns(
    [1, 2]
)

# ==========================================
# Left Panel - Email List
# ==========================================

with left_col:

    st.subheader(
        f"Emails ({len(filtered_emails)})"
    )

    if len(filtered_emails) == 0:

        st.info(
            "No matching emails found."
        )

        st.stop()

    email_titles = []

    for email_item in filtered_emails:

        sender = email_item.get(
            "from",
            "Unknown"
        )

        subject = email_item.get(
            "subject",
            "No Subject"
        )

        email_titles.append(
            f"{sender[:25]} | {subject[:50]}"
        )

    selected_index = st.selectbox(
        "Select Email",
        options=range(
            len(email_titles)
        ),
        format_func=lambda x:
        email_titles[x]
    )

# ==========================================
# Right Panel - Email Viewer
# ==========================================

with right_col:

    selected_email = (
        filtered_emails[
            selected_index
        ]
    )

    st.subheader(
        selected_email.get(
            "subject",
            "No Subject"
        )
    )

    st.write(
        "**From:**",
        selected_email.get(
            "from",
            ""
        )
    )

    st.write(
        "**Date:**",
        selected_email.get(
            "date",
            ""
        )
    )

    st.divider()

    st.text_area(
        "Email Content",
        selected_email.get(
            "body",
            ""
        ),
        height=450
    )

    st.divider()

# ==========================================
# Action Buttons
# ==========================================

col1, col2, col3 = st.columns(
    3
)

# ==========================================
# AI Summary
# ==========================================

with col1:

    if st.button(
        "🤖 Generate Summary"
    ):

        gemini_key = (
            st.session_state.get(
                "gemini_key",
                ""
            )
        )

        if not gemini_key:

            st.error(
                "Gemini API key not configured."
            )

        else:

            try:

                with st.spinner(
                    "Generating summary..."
                ):

                    ai = AIService(
                        gemini_key
                    )

                    summary = (
                        ai.summarize_email(
                            selected_email[
                                "subject"
                            ],
                            selected_email[
                                "body"
                            ]
                        )
                    )

                    st.session_state[
                        "email_summary"
                    ] = summary

            except Exception as e:

                st.error(
                    str(e)
                )

# Show Summary

if (
    "email_summary"
    in st.session_state
):

    st.subheader(
        "🤖 AI Summary"
    )

    st.markdown(
        st.session_state[
            "email_summary"
        ]
    )

# ==========================================
# WhatsApp Send
# ==========================================

with col2:

    if st.button(
        "📱 Send WhatsApp"
    ):

        st.session_state[
            "show_whatsapp"
        ] = True

if st.session_state.get(
    "show_whatsapp",
    False
):

    phone_number = st.text_input(
        "Recipient WhatsApp Number",
        placeholder="whatsapp:+919999999999"
    )

    if st.button(
        "Send Message"
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

            message = (
                selected_email[
                    "subject"
                ]
                + "\n\n"
                + selected_email[
                    "body"
                ][:1000]
            )

            wa.send_message(
                phone_number,
                message
            )

            st.success(
                "WhatsApp message sent."
            )

        except Exception as e:

            st.error(
                str(e)
            )

# ==========================================
# Export PDF
# ==========================================

with col3:

    if st.button(
        "📄 Export PDF"
    ):

        try:

            pdf_file = export_pdf(
                selected_email,
                "email.pdf"
            )

            with open(
                pdf_file,
                "rb"
            ) as f:

                st.download_button(
                    label="⬇ Download PDF",
                    data=f,
                    file_name="email.pdf",
                    mime="application/pdf"
                )

        except Exception as e:

            st.error(
                str(e)
            )

# ==========================================
# Export Entire Inbox CSV
# ==========================================

st.divider()

st.subheader(
    "Export Inbox"
)

if st.button(
    "⬇ Export All Emails CSV"
):

    csv_file = export_csv(
        emails,
        "emails.csv"
    )

    with open(
        csv_file,
        "rb"
    ) as f:

        st.download_button(
            label="Download CSV",
            data=f,
            file_name="emails.csv",
            mime="text/csv"
        )

# ==========================================
# Inbox Statistics
# ==========================================

st.divider()

st.subheader(
    "Inbox Statistics"
)

col1, col2, col3 = st.columns(
    3
)

with col1:
    st.metric(
        "Total Emails",
        len(emails)
    )

with col2:
    st.metric(
        "Filtered Emails",
        len(filtered_emails)
    )

with col3:
    st.metric(
        "Unique Senders",
        len(
            set(
                [
                    x["from"]
                    for x in emails
                ]
            )
        )
    )