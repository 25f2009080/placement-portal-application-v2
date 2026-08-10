import os
import smtplib
from email.message import EmailMessage


def send_email(to_email, subject, body):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([
        smtp_host,
        smtp_username,
        smtp_password
    ]):
        print("SMTP is not configured.")
        print(f"Email that would be sent to: {to_email}")
        print(f"Subject: {subject}")
        print(body)
        return False

    message = EmailMessage()

    message["From"] = smtp_username
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    return True