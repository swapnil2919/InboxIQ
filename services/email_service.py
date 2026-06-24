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
    # CONNECT
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
                f"Connection Failed: {str(e)}"
            )

    # =====================================
    # DISCONNECT
    # =====================================

    def disconnect(self):

        try:

            if self.mail:
                self.mail.logout()

        except:
            pass

    # =====================================
    # DECODE EMAIL TEXT
    # =====================================

    @staticmethod
    def decode_text(text):

        if not text:
            return ""

        decoded = decode_header(text)

        result = ""

        for value, encoding in decoded:

            try:

                if isinstance(
                    value,
                    bytes
                ):

                    result += value.decode(
                        encoding
                        if encoding
                        else "utf-8",
                        errors="ignore"
                    )

                else:

                    result += value

            except:

                result += str(value)

        return result

    # =====================================
    # EXTRACT BODY
    # =====================================

    @staticmethod
    def extract_body(msg):

        plain_text = ""
        html_body = ""

        try:

            if msg.is_multipart():

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

                    # ------------------
                    # TEXT
                    # ------------------

                    if (
                        content_type
                        == "text/plain"
                    ):

                        try:

                            plain_text = (
                                part.get_payload(
                                    decode=True
                                )
                                .decode(
                                    errors="ignore"
                                )
                            )

                        except:
                            pass

                    # ------------------
                    # HTML
                    # ------------------

                    elif (
                        content_type
                        == "text/html"
                    ):

                        try:

                            html_body = (
                                part.get_payload(
                                    decode=True
                                )
                                .decode(
                                    errors="ignore"
                                )
                            )

                        except:
                            pass

            else:

                payload = (
                    msg.get_payload(
                        decode=True
                    )
                )

                if payload:

                    plain_text = (
                        payload.decode(
                            errors="ignore"
                        )
                    )

        except:
            pass

        # Fallback:
        # create text from html

        if (
            not plain_text
            and html_body
        ):

            soup = BeautifulSoup(
                html_body,
                "html.parser"
            )

            plain_text = (
                soup.get_text(
                    separator="\n"
                )
            )

        return {
            "plain_text":
            plain_text,

            "html_body":
            html_body
        }

    # =====================================
    # ATTACHMENTS
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

        except:
            pass

        return attachments

    # =====================================
    # PARSE EMAIL
    # =====================================

    def parse_email(
        self,
        msg
    ):

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

            date = str(
                parsedate_to_datetime(
                    date
                )
            )

        except:
            pass

        body_data = (
            self.extract_body(
                msg
            )
        )

        plain_text = (
            body_data[
                "plain_text"
            ]
        )

        html_body = (
            body_data[
                "html_body"
            ]
        )

        attachments = (
            self.get_attachments(
                msg
            )
        )

        sender_name = sender

        try:

            if "<" in sender:

                sender_name = (
                    sender.split(
                        "<"
                    )[0]
                    .strip()
                )

        except:
            pass

        preview = (
            plain_text[:150]
            + "..."
            if len(
                plain_text
            ) > 150
            else plain_text
        )

        return {

            "id":
            str(
                hash(
                    subject
                    + sender
                    + date
                )
            ),

            "subject":
            subject,

            "sender_name":
            sender_name,

            "sender_email":
            sender,

            "to":
            receiver,

            "date":
            date,

            # Plain text version
            "body":
            plain_text,

            # Original html version
            "body_html":
            html_body,

            "preview":
            preview,

            "attachments":
            attachments,

            "has_attachment":
            len(
                attachments
            ) > 0,

            "category":
            "Inbox",

            "is_read":
            False
        }

    # =====================================
    # FETCH EMAILS
    # =====================================

    def fetch_emails(
        self,
        limit=100
    ):

        emails = []

        status, messages = (
            self.mail.search(
                None,
                "ALL"
            )
        )

        if (
            status
            != "OK"
        ):

            return emails

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

                status, msg_data = (
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

                for response in msg_data:

                    if isinstance(
                        response,
                        tuple
                    ):

                        msg = (
                            email.message_from_bytes(
                                response[1]
                            )
                        )

                        parsed = (
                            self.parse_email(
                                msg
                            )
                        )

                        emails.append(
                            parsed
                        )

            except:
                continue

        return emails

    # =====================================
    # FETCH UNREAD
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

        if (
            status
            != "OK"
        ):

            return emails

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

                status, msg_data = (
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

                for response in msg_data:

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

            except:
                continue

        return emails
