import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.parser import (
    get_top_domains,
    get_top_senders,
    generate_stats
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="InboxIQ Analytics",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.metric-card{
    padding:15px;
    border-radius:12px;
    border:1px solid #2d2d2d;
    background:#111827;
}

.analytics-title{
    font-size:18px;
    font-weight:600;
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
        "No emails loaded. Please connect mailbox first."
    )
    st.stop()

emails = st.session_state.emails

# =========================================================
# PAGE TITLE
# =========================================================

st.title("📊 InboxIQ Analytics")

st.caption(
    "Analyze inbox activity, senders, domains and engagement."
)

# =========================================================
# STATS
# =========================================================

stats = generate_stats(
    emails
)

total_emails = stats.get(
    "total_emails",
    0
)

unique_senders = stats.get(
    "unique_senders",
    0
)

attachments = stats.get(
    "emails_with_attachments",
    0
)

domains = len(
    set(
        [
            email.get(
                "sender_email",
                ""
            ).split("@")[-1]
            for email in emails
            if "@"
            in email.get(
                "sender_email",
                ""
            )
        ]
    )
)

# =========================================================
# KPI ROW
# =========================================================

col1, col2, col3, col4 = st.columns(
    4
)

with col1:

    st.metric(
        "📧 Total Emails",
        total_emails
    )

with col2:

    st.metric(
        "👤 Unique Senders",
        unique_senders
    )

with col3:

    st.metric(
        "📎 Attachments",
        attachments
    )

with col4:

    st.metric(
        "🌐 Domains",
        domains
    )

st.divider()

# =========================================================
# DATAFRAME
# =========================================================

records = []

for email in emails:

    sender = email.get(
        "sender_name",
        "Unknown"
    )

    sender_email = email.get(
        "sender_email",
        ""
    )

    subject = email.get(
        "subject",
        ""
    )

    domain = "Unknown"

    if "@" in sender_email:

        domain = (
            sender_email
            .split("@")[-1]
            .replace(">", "")
            .strip()
        )

    records.append(
        {
            "sender":
            sender,

            "sender_email":
            sender_email,

            "subject":
            subject,

            "domain":
            domain,

            "subject_length":
            len(subject),

            "has_attachment":
            email.get(
                "has_attachment",
                False
            )
        }
    )

df = pd.DataFrame(
    records
)

# =========================================================
# TOP SENDERS
# =========================================================

st.subheader(
    "👤 Top Senders"
)

sender_counts = (
    df["sender"]
    .value_counts()
    .reset_index()
)

sender_counts.columns = [
    "Sender",
    "Emails"
]

fig_sender = px.bar(
    sender_counts.head(10),
    x="Sender",
    y="Emails",
    text="Emails",
    title="Top 10 Senders"
)

fig_sender.update_layout(
    height=450
)

st.plotly_chart(
    fig_sender,
    use_container_width=True
)

# =========================================================
# DOMAIN ANALYSIS
# =========================================================

col1, col2 = st.columns(
    2
)

with col1:

    st.subheader(
        "🌐 Email Domains"
    )

    domain_counts = (
        df["domain"]
        .value_counts()
        .reset_index()
    )

    domain_counts.columns = [
        "Domain",
        "Emails"
    ]

    fig_domain = px.pie(
        domain_counts.head(10),
        names="Domain",
        values="Emails",
        hole=0.4
    )

    st.plotly_chart(
        fig_domain,
        use_container_width=True
    )

with col2:

    st.subheader(
        "📎 Attachments"
    )

    attach_df = pd.DataFrame(
        {
            "Type":
            [
                "With Attachment",
                "Without Attachment"
            ],

            "Count":
            [
                len(
                    df[
                        df[
                            "has_attachment"
                        ]
                        == True
                    ]
                ),
                len(
                    df[
                        df[
                            "has_attachment"
                        ]
                        == False
                    ]
                )
            ]
        }
    )

    fig_attach = px.pie(
        attach_df,
        names="Type",
        values="Count"
    )

    st.plotly_chart(
        fig_attach,
        use_container_width=True
    )

st.divider()

# =========================================================
# SUBJECT LENGTH
# =========================================================

st.subheader(
    "📝 Subject Length Analysis"
)

fig_subject = px.histogram(
    df,
    x="subject_length",
    nbins=20
)

fig_subject.update_layout(
    height=450
)

st.plotly_chart(
    fig_subject,
    use_container_width=True
)

st.divider()

# =========================================================
# TOP DOMAINS TABLE
# =========================================================

st.subheader(
    "🌐 Top Domains"
)

top_domains = get_top_domains(
    emails
)

domain_df = pd.DataFrame(
    top_domains,
    columns=[
        "Domain",
        "Count"
    ]
)

st.dataframe(
    domain_df,
    use_container_width=True
)

# =========================================================
# TOP SENDERS TABLE
# =========================================================

st.subheader(
    "👤 Top Senders"
)

top_senders = get_top_senders(
    emails
)

sender_df = pd.DataFrame(
    top_senders,
    columns=[
        "Sender",
        "Count"
    ]
)

st.dataframe(
    sender_df,
    use_container_width=True
)

st.divider()

# =========================================================
# RECENT EMAILS
# =========================================================

st.subheader(
    "📧 Recent Emails"
)

preview_df = pd.DataFrame(
    [
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

            "Attachment":
            "Yes"
            if email.get(
                "has_attachment",
                False
            )
            else "No"
        }

        for email in emails[:50]
    ]
)

st.dataframe(
    preview_df,
    use_container_width=True
)

# =========================================================
# EXPORT ANALYTICS
# =========================================================

st.divider()

csv_data = df.to_csv(
    index=False
)

st.download_button(
    label="⬇ Download Analytics CSV",
    data=csv_data,
    file_name="inboxiq_analytics.csv",
    mime="text/csv",
    use_container_width=True
)