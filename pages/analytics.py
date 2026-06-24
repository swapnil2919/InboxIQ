import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Email Analytics")

# ==========================================
# Validation
# ==========================================

if (
    "emails" not in st.session_state
    or len(st.session_state.emails) == 0
):

    st.warning(
        "No emails loaded. Please connect your mailbox first."
    )

    st.stop()

emails = st.session_state.emails

# ==========================================
# Create DataFrame
# ==========================================

records = []

for email in emails:

    sender = email.get(
        "from",
        "Unknown"
    )

    subject = email.get(
        "subject",
        ""
    )

    date = email.get(
        "date",
        ""
    )

    domain = "Unknown"

    try:

        if "@" in sender:

            domain = (
                sender.split("@")[-1]
                .replace(">", "")
                .strip()
            )

    except Exception:
        pass

    records.append(
        {
            "sender": sender,
            "subject": subject,
            "date": date,
            "domain": domain,
            "subject_length": len(
                subject
            ),
        }
    )

df = pd.DataFrame(records)

# ==========================================
# KPIs
# ==========================================

total_emails = len(df)

unique_senders = (
    df["sender"]
    .nunique()
)

unique_domains = (
    df["domain"]
    .nunique()
)

avg_subject_length = round(
    df["subject_length"].mean(),
    2
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Emails",
        total_emails
    )

with col2:

    st.metric(
        "Unique Senders",
        unique_senders
    )

with col3:

    st.metric(
        "Domains",
        unique_domains
    )

with col4:

    st.metric(
        "Avg Subject Length",
        avg_subject_length
    )

st.divider()

# ==========================================
# Top Senders
# ==========================================

st.subheader(
    "📨 Top Senders"
)

sender_counts = (
    df["sender"]
    .value_counts()
    .reset_index()
)

sender_counts.columns = [
    "Sender",
    "Count"
]

fig = px.bar(
    sender_counts.head(10),
    x="Sender",
    y="Count",
    title="Top 10 Senders"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================
# Domain Analysis
# ==========================================

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
    "Count"
]

fig_domain = px.pie(
    domain_counts.head(10),
    values="Count",
    names="Domain",
    title="Top Domains"
)

st.plotly_chart(
    fig_domain,
    use_container_width=True
)

# ==========================================
# Subject Length Distribution
# ==========================================

st.subheader(
    "📝 Subject Length Distribution"
)

fig_subject = px.histogram(
    df,
    x="subject_length",
    nbins=20,
    title="Subject Length"
)

st.plotly_chart(
    fig_subject,
    use_container_width=True
)

# ==========================================
# Sender Statistics Table
# ==========================================

st.subheader(
    "📋 Sender Statistics"
)

st.dataframe(
    sender_counts,
    use_container_width=True
)

# ==========================================
# Domain Statistics Table
# ==========================================

st.subheader(
    "📋 Domain Statistics"
)

st.dataframe(
    domain_counts,
    use_container_width=True
)

# ==========================================
# Export Analytics
# ==========================================

st.divider()

st.subheader(
    "⬇ Export Analytics"
)

csv_data = sender_counts.to_csv(
    index=False
)

st.download_button(
    label="Download Sender Analytics CSV",
    data=csv_data,
    file_name="sender_analytics.csv",
    mime="text/csv"
)

# ==========================================
# Recent Emails Preview
# ==========================================

st.divider()

st.subheader(
    "📧 Recent Emails"
)

preview_df = df[
    [
        "sender",
        "subject",
        "domain"
    ]
].head(20)

st.dataframe(
    preview_df,
    use_container_width=True
)