from sqlalchemy import text

from app import db
from app.celery_app import celery


@celery.task
def test_task():
    result = db.session.execute(text("SELECT 1")).scalar()

    print("Database test result:", result)

    return f"Flask + Celery + Database working: {result}"