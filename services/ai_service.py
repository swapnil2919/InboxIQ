import google.generativeai as genai


class AIService:

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-flash"
    ):

        self.api_key = api_key
        self.model_name = model_name

        genai.configure(
            api_key=self.api_key
        )

        self.model = genai.GenerativeModel(
            self.model_name
        )

    # =====================================
    # Generic Prompt
    # =====================================

    def generate(
        self,
        prompt: str
    ):

        try:

            response = (
                self.model.generate_content(
                    prompt
                )
            )

            return response.text

        except Exception as e:

            raise Exception(
                f"Gemini Error: {str(e)}"
            )

    # =====================================
    # Email Summary
    # =====================================

    def summarize_email(
        self,
        subject: str,
        body: str
    ):

        prompt = f"""
You are an expert email assistant.

Analyze the email below.

SUBJECT:
{subject}

BODY:
{body}

Provide:

1. Short Summary
2. Priority (Low/Medium/High)
3. Action Items
4. Suggested Response
"""

        return self.generate(
            prompt
        )

    # =====================================
    # Email Categorization
    # =====================================

    def categorize_email(
        self,
        subject: str,
        body: str
    ):

        prompt = f"""
Categorize this email.

Possible categories:

- Work
- Finance
- Personal
- Marketing
- Social
- Notification
- Travel
- Spam

Subject:
{subject}

Body:
{body}

Return ONLY category name.
"""

        return self.generate(
            prompt
        )

    # =====================================
    # Priority Detection
    # =====================================

    def detect_priority(
        self,
        subject: str,
        body: str
    ):

        prompt = f"""
Determine priority.

Options:

- Low
- Medium
- High

Subject:
{subject}

Body:
{body}

Return only priority.
"""

        return self.generate(
            prompt
        )

    # =====================================
    # Action Items
    # =====================================

    def extract_action_items(
        self,
        subject: str,
        body: str
    ):

        prompt = f"""
Extract all action items.

Subject:
{subject}

Body:
{body}

Return bullet points.
"""

        return self.generate(
            prompt
        )

    # =====================================
    # Suggested Reply
    # =====================================

    def generate_reply(
        self,
        subject: str,
        body: str,
        tone="Professional"
    ):

        prompt = f"""
Create a reply.

Tone:
{tone}

Original Subject:
{subject}

Original Email:
{body}

Generate a complete email response.
"""

        return self.generate(
            prompt
        )

    # =====================================
    # Smart Analysis
    # =====================================

    def full_analysis(
        self,
        subject: str,
        body: str
    ):

        prompt = f"""
Perform a complete email analysis.

Subject:
{subject}

Body:
{body}

Return:

# Summary

# Priority

# Category

# Action Items

# Suggested Reply
"""

        return self.generate(
            prompt
        )