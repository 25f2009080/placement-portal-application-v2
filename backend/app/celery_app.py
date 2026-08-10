from celery import Celery, Task


celery = Celery(
    "placement_portal",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
        "app.tasks.test_task",
        "app.tasks.interview_reminders",
        "app.tasks.reports",
        "app.tasks.exports"
    ],
)


celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
)


celery.conf.beat_schedule = {
    "check-interview-reminders": {
        "task": "app.tasks.interview_reminders.send_interview_reminders",
        "schedule": 3600.0,
    },
}