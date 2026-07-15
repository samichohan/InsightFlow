import resend

from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


async def send_verification_email(email: str, token: str):
    verify_link = f"{settings.FRONTEND_URL}/verify/{token}"

    resend.Emails.send({
        "from": f"InsightFlow <{settings.FROM_EMAIL}>",
        "to": email,
        "subject": "Verify your InsightFlow account",
        "html": f"""
        <h2>Welcome to InsightFlow</h2>

        <p>Click below to verify your email.</p>

        <a href="{verify_link}"
           style="padding:12px 20px;
                  background:#2563eb;
                  color:white;
                  text-decoration:none;
                  border-radius:6px;">
            Verify Email
        </a>

        <p>If you didn't create this account, ignore this email.</p>
        """
    })