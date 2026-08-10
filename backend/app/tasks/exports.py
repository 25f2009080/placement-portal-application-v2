import csv
import os
from datetime import datetime, timezone

from app.celery_app import celery
from app.models import Application, Placement


@celery.task
def export_application_history(user_type, user_id):
    """
    Generate an application/placement history CSV.

    user_type:
        "student" or "company"

    user_id:
        Student.id or Company.id
    """

    rows = []

    if user_type == "student":

        applications = Application.query.filter_by(
            student_id=user_id
        ).all()

        for application in applications:
            job = application.job
            company = job.company if job else None

            rows.append([
                "Application",
                company.name if company else "",
                job.title if job else "",
                getattr(application, "status", ""),
                getattr(application, "applied_at", ""),
                getattr(application, "updated_at", ""),
            ])

        placements = Placement.query.filter_by(
            student_id=user_id
        ).all()

        for placement in placements:
            rows.append([
                "Placement",
                placement.company.name
                if placement.company else "",
                placement.position or "",
                "Placed",
                placement.placed_at or "",
                placement.joining_date or "",
            ])

    elif user_type == "company":

        applications = (
            Application.query
            .join(Application.job)
            .filter_by(company_id=user_id)
            .all()
        )

        for application in applications:
            job = application.job
            student = application.student

            rows.append([
                "Application",
                student.name if student else "",
                job.title if job else "",
                getattr(application, "status", ""),
                getattr(application, "applied_at", ""),
                getattr(application, "updated_at", ""),
            ])

        placements = Placement.query.filter_by(
            company_id=user_id
        ).all()

        for placement in placements:
            rows.append([
                "Placement",
                placement.student.name
                if placement.student else "",
                placement.position or "",
                "Placed",
                placement.placed_at or "",
                placement.joining_date or "",
            ])

    else:
        return {
            "success": False,
            "message": "Invalid user type"
        }

    export_folder = os.path.join(
        "instance",
        "exports"
    )

    os.makedirs(export_folder, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{user_type}_history_{user_id}_{timestamp}.csv"
    )

    filepath = os.path.join(
        export_folder,
        filename
    )

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if user_type == "student":
            writer.writerow([
                "Record Type",
                "Company",
                "Position",
                "Status",
                "Applied/Placed At",
                "Updated/Joining Date"
            ])
        else:
            writer.writerow([
                "Record Type",
                "Student",
                "Position",
                "Status",
                "Applied/Placed At",
                "Updated/Joining Date"
            ])

        writer.writerows(rows)

    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "records": len(rows)
    }