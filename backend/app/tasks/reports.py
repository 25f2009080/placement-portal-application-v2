import os
from datetime import datetime, timezone

from app.celery_app import celery


@celery.task
def generate_company_placement_report(company_id):

    from app import create_app

    flask_app = create_app()

    with flask_app.app_context():

        from app.models import Company, Application, Placement

        company = Company.query.get(company_id)

        if not company:
            return {
                "success": False,
                "message": "Company not found"
            }

        applications = (
            Application.query
            .join(Application.job)
            .filter_by(company_id=company.id)
            .all()
        )

        placements = Placement.query.filter_by(
            company_id=company.id
        ).all()

        total_applications = len(applications)

        applied = sum(
            1
            for a in applications
            if a.status == "Applied"
        )

        shortlisted = sum(
            1
            for a in applications
            if a.status == "Shortlisted"
        )

        selected = sum(
            1
            for a in applications
            if a.status in [
                "Selected",
                "Offer",
                "Placed"
            ]
        )

        rejected = sum(
            1
            for a in applications
            if a.status == "Rejected"
        )

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Placement Report - {company.name}</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}

        h1, h2 {{
            color: #222;
        }}

        .summary {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}

        .card {{
            border: 1px solid #ccc;
            padding: 15px;
            min-width: 130px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background: #f2f2f2;
        }}
    </style>
</head>

<body>

<h1>Placement Report</h1>

<p>
    <strong>Company:</strong> {company.name}
</p>

<p>
    <strong>Generated:</strong>
    {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
</p>

<h2>Application Statistics</h2>

<div class="summary">

    <div class="card">
        <strong>Total Applications</strong><br>
        {total_applications}
    </div>

    <div class="card">
        <strong>Applied</strong><br>
        {applied}
    </div>

    <div class="card">
        <strong>Shortlisted</strong><br>
        {shortlisted}
    </div>

    <div class="card">
        <strong>Selected / Placed</strong><br>
        {selected}
    </div>

    <div class="card">
        <strong>Rejected</strong><br>
        {rejected}
    </div>

</div>

<h2>Placement Details</h2>

<table>

    <tr>
        <th>Student</th>
        <th>Position</th>
        <th>Salary</th>
        <th>Joining Date</th>
        <th>Placed At</th>
    </tr>
"""

        for placement in placements:

            student_name = (
                placement.student.name
                if placement.student
                else "Unknown"
            )

            salary = (
                f"₹{placement.salary:,.2f}"
                if placement.salary is not None
                else "-"
            )

            joining_date = (
                placement.joining_date.isoformat()
                if placement.joining_date
                else "-"
            )

            placed_at = (
                placement.placed_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
                if placement.placed_at
                else "-"
            )

            html += f"""
    <tr>
        <td>{student_name}</td>
        <td>{placement.position}</td>
        <td>{salary}</td>
        <td>{joining_date}</td>
        <td>{placed_at}</td>
    </tr>
"""

        html += """
</table>

</body>
</html>
"""

        report_folder = os.path.join(
            flask_app.instance_path,
            "reports"
        )

        os.makedirs(
            report_folder,
            exist_ok=True
        )

        filename = (
            f"placement_report_company_{company.id}_"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.html"
        )

        filepath = os.path.join(
            report_folder,
            filename
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(html)

        return {
            "success": True,
            "filename": filename,
            "filepath": filepath,
            "total_applications": total_applications,
            "total_placements": len(placements)
        }