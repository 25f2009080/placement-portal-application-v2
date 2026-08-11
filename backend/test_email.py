from app import create_app
from app.tasks.interview_reminders import send_interview_reminders

app = create_app()

with app.app_context():
    result = send_interview_reminders.delay()
    print("Task submitted successfully.")
    print("Task ID:", result.id)
