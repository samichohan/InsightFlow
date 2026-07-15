import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


async def send_verification_email(email: str, token: str):
    verify_link = f"{settings.FRONTEND_URL}/verify/{token}"

    subject = "Verify your InsightFlow account"

    body = f"""
    <h2>Welcome to InsightFlow</h2>

    <p>Click the button below to verify your email.</p>

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

    msg = MIMEMultipart()
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        print("Connecting SMTP...")
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        print("Starting TLS...")
        server.starttls()

        print("Logging in...")
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        print("Sending email...")
        server.sendmail(settings.FROM_EMAIL, email, msg.as_string())

        print("✅ Email sent successfully!")

        server.quit()

    except Exception as e:
        print("SMTP ERROR:", e)
        raise