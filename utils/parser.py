from collections import Counter
from email.utils import parsedate_to_datetime


# ==========================================
# Search Emails
# ==========================================

def search_emails(
    emails,
    keyword=""
):

    if not keyword:
        return emails

    keyword = keyword.lower()

    results = []

    for email in emails:

        subject = email.get(
            "subject",
            ""
        ).lower()

        # Emails expose sender via sender_name / sender_email
        # (older records may still use "from").
        sender = (
            email.get("sender_name", "")
            + " "
            + email.get("sender_email", "")
            + " "
            + email.get("from", "")
        ).lower()

        body = email.get(
            "body",
            ""
        ).lower()

        if (
            keyword in subject
            or keyword in sender
            or keyword in body
        ):
            results.append(email)

    return results


# ==========================================
# Filter By Sender
# ==========================================

def filter_by_sender(
    emails,
    sender_name
):

    if not sender_name:
        return emails

    sender_name = (
        sender_name.lower()
    )

    return [
        email
        for email in emails
        if sender_name
        in email.get(
            "from",
            ""
        ).lower()
    ]


# ==========================================
# Filter By Subject
# ==========================================

def filter_by_subject(
    emails,
    subject_text
):

    if not subject_text:
        return emails

    subject_text = (
        subject_text.lower()
    )

    return [
        email
        for email in emails
        if subject_text
        in email.get(
            "subject",
            ""
        ).lower()
    ]


# ==========================================
# Filter Attachments
# ==========================================

def filter_attachments(
    emails
):

    return [
        email
        for email in emails
        if email.get(
            "has_attachment",
            False
        )
    ]


# ==========================================
# Sort By Date
# ==========================================

def sort_by_date(
    emails,
    descending=True
):

    def parse_date(email):

        try:

            return (
                parsedate_to_datetime(
                    email.get(
                        "date",
                        ""
                    )
                )
            )

        except Exception:

            return None

    return sorted(
        emails,
        key=parse_date,
        reverse=descending
    )


# ==========================================
# Get Unique Senders
# ==========================================

def get_unique_senders(
    emails
):

    senders = set()

    for email in emails:

        senders.add(
            email.get(
                "from",
                ""
            )
        )

    return sorted(
        list(senders)
    )


# ==========================================
# Extract Domain
# ==========================================

def extract_domain(
    sender
):

    try:

        if "@" in sender:

            return (
                sender.split(
                    "@"
                )[-1]
                .replace(">", "")
                .strip()
            )

    except Exception:
        pass

    return "Unknown"


# ==========================================
# Top Domains
# ==========================================

def get_top_domains(
    emails,
    top_n=10
):

    domains = []

    for email in emails:

        sender = email.get(
            "from",
            ""
        )

        domains.append(
            extract_domain(
                sender
            )
        )

    return Counter(
        domains
    ).most_common(
        top_n
    )


# ==========================================
# Top Senders
# ==========================================

def get_top_senders(
    emails,
    top_n=10
):

    senders = []

    for email in emails:

        senders.append(
            email.get(
                "from",
                "Unknown"
            )
        )

    return Counter(
        senders
    ).most_common(
        top_n
    )


# ==========================================
# Email Statistics
# ==========================================

def generate_stats(
    emails
):

    total_emails = len(
        emails
    )

    unique_senders = len(
        get_unique_senders(
            emails
        )
    )

    attachment_count = len(
        filter_attachments(
            emails
        )
    )

    return {
        "total_emails":
        total_emails,

        "unique_senders":
        unique_senders,

        "emails_with_attachments":
        attachment_count,
    }


# ==========================================
# Email Preview
# ==========================================

def get_preview(
    body,
    max_length=150
):

    if not body:
        return ""

    body = body.replace(
        "\n",
        " "
    )

    if len(body) <= max_length:

        return body

    return (
        body[:max_length]
        + "..."
    )


# ==========================================
# Safe Email Record
# ==========================================

def normalize_email(
    email
):

    return {
        "subject":
        email.get(
            "subject",
            ""
        ),

        "from":
        email.get(
            "from",
            ""
        ),

        "to":
        email.get(
            "to",
            ""
        ),

        "date":
        email.get(
            "date",
            ""
        ),

        "body":
        email.get(
            "body",
            ""
        ),

        "attachments":
        email.get(
            "attachments",
            []
        ),

        "has_attachment":
        email.get(
            "has_attachment",
            False
        )
    }