import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup


class EmailService:

    def __init__(
        self,
        email_id: str,
        password: str,
        imap_server: str
    ):
        self.email_id = email_id
        self.password = password
        self.imap_server = imap_server
        self.mail = None

    # =====================================
    # Connection
    # =====================================

    def connect(self):

        try:

            self.mail = imaplib.IMAP4_SSL(
                self.imap_server
            )

            self.mail.login(
                self.email_id,
                self.password
            )

            self.mail.select(
                "INBOX"
            )

            return True

        except Exception as e:

            raise Exception(
                f"Failed to connect: {str(e)}"
            )

    def disconnect(self):

        try:

            if self.mail:
                self.mail.logout()

        except Exception:
            pass

    # =====================================
    # Decoder
    # =====================================

    @staticmethod
    def decode_text(value):

        if not value:
            return ""

        decoded_parts = decode_header(
            value
        )

        result = ""

        for text, encoding in decoded_parts:

            try:

                if isinstance(
                    text,
                    bytes
                ):

                    result += text.decode(
                        encoding
                        if encoding
                        else "utf-8",
                        errors="ignore"
                    )

                else:

                    result += str(text)

            except Exception:

                result += str(text)

        return result

    # =====================================
    # Body Parser
    # =====================================

    @staticmethod
    def extract_body(msg):

        body = ""

        try:

            if msg.is_multipart():

                html_body = ""

                for part in msg.walk():

                    content_type = (
                        part.get_content_type()
                    )

                    disposition = str(
                        part.get(
                            "Content-Disposition"
                        )
                    )

                    if (
                        "attachment"
                        in disposition.lower()
                    ):
                        continue

                    if (
                        content_type
                        == "text/plain"
                    ):

                        body = (
                            part.get_payload(
                                decode=True
                            )
                            .decode(
                                errors="ignore"
                            )
                        )

                    elif (
                        content_type
                        == "text/html"
                    ):

                        html_body = (
                            part.get_payload(
                                decode=True
                            )
                            .decode(
                                errors="ignore"
                            )
                        )

                if (
                    not body
                    and html_body
                ):

                    soup = BeautifulSoup(
                        html_body,
                        "html.parser"
                    )

                    body = soup.get_text(
                        separator="\n"
                    )

            else:

                payload = (
                    msg.get_payload(
                        decode=True
                    )
                )

                if payload:

                    body = payload.decode(
                        errors="ignore"
                    )

        except Exception:

            pass

        return body

    # =====================================
    # Attachment Detection
    # =====================================

    @staticmethod
    def get_attachments(msg):

        attachments = []

        try:

            for part in msg.walk():

                filename = (
                    part.get_filename()
                )

                if filename:

                    attachments.append(
                        filename
                    )

        except Exception:
            pass

        return attachments

    # =====================================
    # Single Email Parser
    # =====================================

    def parse_email(
        self,
        msg
    ):

        try:

            subject = (
                self.decode_text(
                    msg.get(
                        "Subject",
                        ""
                    )
                )
            )

            sender = (
                self.decode_text(
                    msg.get(
                        "From",
                        ""
                    )
                )
            )

            receiver = (
                self.decode_text(
                    msg.get(
                        "To",
                        ""
                    )
                )
            )

            date = msg.get(
                "Date",
                ""
            )

            try:

                parsed_date = (
                    parsedate_to_datetime(
                        date
                    )
                )

                date = str(
                    parsed_date
                )

            except Exception:
                pass

            body = (
                self.extract_body(
                    msg
                )
            )

            attachments = (
                self.get_attachments(
                    msg
                )
            )

            return {
                "subject": subject,
                "from": sender,
                "to": receiver,
                "date": date,
                "body": body,
                "attachments": attachments,
                "has_attachment": len(
                    attachments
                )
                > 0,
            }

        except Exception as e:

            return {
                "subject": "",
                "from": "",
                "to": "",
                "date": "",
                "body": "",
                "attachments": [],
                "has_attachment": False,
                "error": str(e),
            }

    # =====================================
    # Fetch Emails
    # =====================================

    def fetch_emails(
        self,
        limit=100
    ):

        if not self.mail:

            raise Exception(
                "Not connected."
            )

        emails = []

        status, messages = (
            self.mail.search(
                None,
                "ALL"
            )
        )

        if status != "OK":

            raise Exception(
                "Unable to fetch emails."
            )

        email_ids = (
            messages[0]
            .split()
        )

        email_ids = (
            email_ids[-limit:]
        )

        for email_id in reversed(
            email_ids
        ):

            try:

                status, data = (
                    self.mail.fetch(
                        email_id,
                        "(RFC822)"
                    )
                )

                if (
                    status
                    != "OK"
                ):
                    continue

                for response in data:

                    if isinstance(
                        response,
                        tuple
                    ):

                        msg = (
                            email.message_from_bytes(
                                response[1]
                            )
                        )

                        parsed_email = (
                            self.parse_email(
                                msg
                            )
                        )

                        emails.append(
                            parsed_email
                        )

            except Exception:
                continue

        return emails

    # =====================================
    # Fetch Unread
    # =====================================

    def fetch_unread(
        self,
        limit=50
    ):

        emails = []

        status, messages = (
            self.mail.search(
                None,
                "UNSEEN"
            )
        )

        if status != "OK":

            return []

        email_ids = (
            messages[0]
            .split()
        )

        email_ids = (
            email_ids[-limit:]
        )

        for email_id in reversed(
            email_ids
        ):

            status, data = (
                self.mail.fetch(
                    email_id,
                    "(RFC822)"
                )
            )

            for response in data:

                if isinstance(
                    response,
                    tuple
                ):

                    msg = (
                        email.message_from_bytes(
                            response[1]
                        )
                    )

                    emails.append(
                        self.parse_email(
                            msg
                        )
                    )

        return emails