import pandas as pd
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib.styles import (
    getSampleStyleSheet
)


# ==========================================
# Export Emails CSV
# ==========================================

def export_csv(
    emails,
    filename="emails.csv"
):

    df = pd.DataFrame(
        emails
    )

    df.to_csv(
        filename,
        index=False
    )

    return filename


# ==========================================
# Export Analytics CSV
# ==========================================

def export_analytics_csv(
    dataframe,
    filename="analytics.csv"
):

    dataframe.to_csv(
        filename,
        index=False
    )

    return filename


# ==========================================
# Export Single Email PDF
# ==========================================

def export_pdf(
    email_data,
    filename="email.pdf"
):

    doc = SimpleDocTemplate(
        filename
    )

    styles = (
        getSampleStyleSheet()
    )

    content = []

    content.append(
        Paragraph(
            email_data.get(
                "subject",
                "No Subject"
            ),
            styles["Title"]
        )
    )

    content.append(
        Spacer(
            1,
            12
        )
    )

    content.append(
        Paragraph(
            f"<b>From:</b> {email_data.get('from', '')}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"<b>To:</b> {email_data.get('to', '')}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Date:</b> {email_data.get('date', '')}",
            styles["BodyText"]
        )
    )

    content.append(
        Spacer(
            1,
            12
        )
    )

    body = email_data.get(
        "body",
        ""
    )

    body = body.replace(
        "\n",
        "<br/>"
    )

    content.append(
        Paragraph(
            body,
            styles["BodyText"]
        )
    )

    attachments = (
        email_data.get(
            "attachments",
            []
        )
    )

    if attachments:

        content.append(
            Spacer(
                1,
                12
            )
        )

        content.append(
            Paragraph(
                "<b>Attachments</b>",
                styles["Heading2"]
            )
        )

        for attachment in attachments:

            content.append(
                Paragraph(
                    attachment,
                    styles["BodyText"]
                )
            )

    doc.build(content)

    return filename


# ==========================================
# Export Multiple Emails PDF
# ==========================================

def export_all_emails_pdf(
    emails,
    filename="all_emails.pdf"
):

    doc = SimpleDocTemplate(
        filename
    )

    styles = (
        getSampleStyleSheet()
    )

    content = []

    for email in emails:

        content.append(
            Paragraph(
                email.get(
                    "subject",
                    "No Subject"
                ),
                styles["Heading1"]
            )
        )

        content.append(
            Paragraph(
                f"<b>From:</b> {email.get('from', '')}",
                styles["BodyText"]
            )
        )

        content.append(
            Paragraph(
                f"<b>Date:</b> {email.get('date', '')}",
                styles["BodyText"]
            )
        )

        content.append(
            Spacer(
                1,
                8
            )
        )

        body = email.get(
            "body",
            ""
        )

        body = body.replace(
            "\n",
            "<br/>"
        )

        content.append(
            Paragraph(
                body,
                styles["BodyText"]
            )
        )

        content.append(
            PageBreak()
        )

    doc.build(content)

    return filename


# ==========================================
# Export Summary PDF
# ==========================================

def export_summary_pdf(
    title,
    summary,
    filename="summary.pdf"
):

    doc = SimpleDocTemplate(
        filename
    )

    styles = (
        getSampleStyleSheet()
    )

    content = []

    content.append(
        Paragraph(
            title,
            styles["Title"]
        )
    )

    content.append(
        Spacer(
            1,
            12
        )
    )

    summary = summary.replace(
        "\n",
        "<br/>"
    )

    content.append(
        Paragraph(
            summary,
            styles["BodyText"]
        )
    )

    doc.build(content)

    return filename