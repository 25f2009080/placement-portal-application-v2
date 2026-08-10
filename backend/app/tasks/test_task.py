from app.celery_app import celery


@celery.task
def test_task():
    print("Celery test task executed!")

    return "Celery is working!"