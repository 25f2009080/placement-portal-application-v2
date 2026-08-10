from celery import Celery


celery = Celery(
    "placement_portal",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
        "app.tasks.test_task"
    ],
)


celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
)