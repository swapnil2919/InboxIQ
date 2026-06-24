from twilio.rest import Client


class WhatsAppService:

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        twilio_number: str
    ):

        self.account_sid = account_sid
        self.auth_token = auth_token
        self.twilio_number = twilio_number

        self.client = Client(
            self.account_sid,
            self.auth_token
        )

    # =====================================
    # Validate Configuration
    # =====================================

    def validate(self):

        if not self.account_sid:
            raise Exception(
                "Account SID missing."
            )

        if not self.auth_token:
            raise Exception(
                "Auth Token missing."
            )

        if not self.twilio_number:
            raise Exception(
                "Twilio Number missing."
            )

        return True

    # =====================================
    # Send WhatsApp Message
    # =====================================

    def send_message(
        self,
        to_number: str,
        message: str
    ):

        self.validate()

        try:

            response = (
                self.client.messages.create(
                    body=message,
                    from_=self.twilio_number,
                    to=to_number
                )
            )

            return {
                "success": True,
                "sid": response.sid,
                "status": response.status
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    # =====================================
    # Send Email Summary
    # =====================================

    def send_email_summary(
        self,
        to_number: str,
        subject: str,
        summary: str
    ):

        message = f"""
📧 EMAIL SUMMARY

Subject:
{subject}

Summary:
{summary}
"""

        return self.send_message(
            to_number,
            message
        )

    # =====================================
    # Send Full Email
    # =====================================

    def send_email_content(
        self,
        to_number: str,
        subject: str,
        body: str
    ):

        max_length = 1400

        body = body[:max_length]

        message = f"""
📧 EMAIL

Subject:
{subject}

Body:
{body}
"""

        return self.send_message(
            to_number,
            message
        )

    # =====================================
    # Send AI Analysis
    # =====================================

    def send_ai_analysis(
        self,
        to_number: str,
        analysis: str
    ):

        message = f"""
🤖 AI EMAIL ANALYSIS

{analysis}
"""

        return self.send_message(
            to_number,
            message
        )

    # =====================================
    # Send Alert
    # =====================================

    def send_alert(
        self,
        to_number: str,
        title: str,
        message_body: str
    ):

        message = f"""
🚨 ALERT

{title}

{message_body}
"""

        return self.send_message(
            to_number,
            message
        )

    # =====================================
    # Send Inbox Statistics
    # =====================================

    def send_stats(
        self,
        to_number: str,
        total_emails: int,
        unread_emails: int
    ):

        message = f"""
📊 INBOX STATS

Total Emails:
{total_emails}

Unread Emails:
{unread_emails}
"""

        return self.send_message(
            to_number,
            message
        )

    # =====================================
    # Test Connection
    # =====================================

    def test_connection(
        self,
        to_number: str
    ):

        return self.send_message(
            to_number,
            "✅ WhatsApp connection successful."
        )