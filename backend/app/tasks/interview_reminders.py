from datetime import datetime, timedelta, timezone

from app.celery_app import celery
from app.models import Application
from app.services.email_service import send_email


@celery.task
def send_interview_reminders():
    now = datetime.now(timezone.utc)

    reminder_window_start = now + timedelta(hours=23)
    reminder_window_end = now + timedelta(hours=25)

    applications = Application.query.filter(
        Application.interview_datetime.isnot(None),
        Application.interview_datetime >= reminder_window_start,
        Application.interview_datetime <= reminder_window_end,
        Application.status.in_([
            "Shortlisted",
            "Interview"
        ])
    ).all()

    sent_count = 0

    for application in applications:

        student = application.student
        job = application.job

        if not student or not student.user:
            continue

        if not job:
            continue

        email = student.user.email

        if not email:
            continue

        interview_time = application.interview_datetime

        subject = "Interview Reminder - Placement Portal"

        body = (
            f"Hello {student.name},\n\n"
            f"This is a reminder that you have an interview "
            f"scheduled for the following placement:\n\n"
            f"Company: {job.company.name}\n"
            f"Position: {job.title}\n"
            f"Interview Time: {interview_time}\n"
            f"Mode: {application.interview_mode or 'Not specified'}\n"
            f"Location: "
            f"{application.interview_location or 'Not specified'}\n\n"
            f"Interview Notes:\n"
            f"{application.interview_notes or 'None'}\n\n"
            f"Please make sure you are prepared and available "
            f"for the interview.\n\n"
            f"Regards,\n"
            f"Placement Portal"
        )

        send_email(
            email,
            subject,
            body
        )

        sent_count += 1

    return {
        "reminders_found": len(applications),
        "reminders_processed": sent_count
    }