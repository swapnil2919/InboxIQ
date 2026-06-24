# 📧 Email Dashboard

A modern Streamlit-based Email Dashboard that allows users to connect Gmail, Outlook, or any IMAP-compatible mailbox and manage emails with AI-powered summaries, analytics, WhatsApp integration, and export capabilities.

---

# 🚀 Features

## 📥 Email Management

* Connect Gmail using App Password
* Connect Outlook using IMAP
* Connect Custom IMAP Servers
* Read Inbox Emails
* Search Emails
* Filter Emails
* View Email Content
* Detect Attachments

---

## 🤖 AI Features

Powered by Google Gemini.

### Available Features

* Email Summary
* Priority Detection
* Email Categorization
* Action Item Extraction
* Suggested Email Replies
* Complete Email Analysis

---

## 📊 Analytics

* Total Emails
* Unique Senders
* Top Senders
* Domain Analysis
* Subject Length Analysis
* Email Statistics Dashboard
* CSV Export

---

## 📱 WhatsApp Integration

Powered by Twilio.

### Available Features

* Send Email Content
* Send Email Summary
* Send AI Analysis
* Send Alerts
* Test WhatsApp Connection

---

## 📄 Export Features

* Export Single Email PDF
* Export Multiple Emails PDF
* Export Inbox CSV
* Export Analytics CSV
* Export AI Summary PDF

---

# 📂 Project Structure

```text
email_dashboard/
│
├── app.py
│
├── pages/
│   ├── inbox.py
│   ├── analytics.py
│   └── settings.py
│
├── services/
│   ├── email_service.py
│   ├── ai_service.py
│   └── whatsapp_service.py
│
├── utils/
│   ├── parser.py
│   └── export.py
│
├── requirements.txt
│
└── README.md
```

---

# 🛠 Installation

Clone repository:

```bash
git clone https://github.com/your-username/email-dashboard.git

cd email-dashboard
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

Application will start on:

```text
http://localhost:8501
```

---

# 📧 Gmail Configuration

Enable:

1. Google Account
2. Security
3. 2-Step Verification
4. App Password

Use:

```text
Email:
your_email@gmail.com

Password:
Google App Password

IMAP:
imap.gmail.com
```

---

# 📧 Outlook Configuration

Use:

```text
Email:
your_email@outlook.com

Password:
Your Password

IMAP:
outlook.office365.com
```

---

# 🤖 Gemini Setup

Generate Gemini API Key:

https://aistudio.google.com/app/apikey

Add API Key in:

Settings → Gemini Configuration

---

# 📱 Twilio Setup

Create account:

https://www.twilio.com

Collect:

```text
ACCOUNT SID
AUTH TOKEN
WHATSAPP NUMBER
```

Add them in:

Settings → WhatsApp Configuration

Example:

```text
whatsapp:+14155238886
```

---

# 📊 Email Object Structure

Each email is returned as:

```python
{
    "subject": "Meeting Tomorrow",
    "from": "john@gmail.com",
    "to": "swapnil@gmail.com",
    "date": "2025-06-22",
    "body": "Please join the meeting...",
    "attachments": [
        "file.pdf"
    ],
    "has_attachment": True
}
```

---

# 🔐 Security Notes

Never share:

* Gmail App Password
* Gemini API Key
* Twilio Auth Token

This application stores credentials only in Streamlit Session State.

No credentials are stored in a database.

---

# 📦 Dependencies

```text
streamlit
pandas
plotly
beautifulsoup4
google-generativeai
twilio
reportlab
python-dateutil
```

---

# 🧪 Future Enhancements

* Email Threading
* Attachment Downloads
* Dark Mode
* PostgreSQL Integration
* FastAPI Backend
* User Authentication
* Email Scheduling
* AI Spam Detection
* AI Priority Inbox
* Docker Deployment
* Render Deployment
* Cloudflare R2 Storage

---

# 👨‍💻 Author

Swapnil Kansara

Software Developer | Photographer

---

# 📄 License

MIT License

Feel free to use, modify, and distribute this project.
