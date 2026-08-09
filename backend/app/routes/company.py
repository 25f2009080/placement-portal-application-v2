from datetime import datetime

from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from app import db
from app.models import User, Company, JobPosition, Application


company_bp = Blueprint("company", __name__)


def get_current_company():
    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)

    if not user:
        return None, None, (
            jsonify({
                "success": False,
                "message": "User not found"
            }),
            404
        )

    if user.role != User.COMPANY:
        return None, None, (
            jsonify({
                "success": False,
                "message": "Company access required"
            }),
            403
        )

    company = user.company

    if not company:
        return None, None, (
            jsonify({
                "success": False,
                "message": "Company profile not found"
            }),
            404
        )

    if not company.approved:
        return None, None, (
            jsonify({
                "success": False,
                "message": "Company is not approved"
            }),
            403
        )

    if not company.is_active:
        return None, None, (
            jsonify({
                "success": False,
                "message": "Company account is inactive"
            }),
            403
        )

    return user, company, None


@company_bp.route("/api/company/profile", methods=["GET"])
@jwt_required()
def get_company_profile():

    user, company, error = get_current_company()

    if error:
        return error

    return jsonify({
        "success": True,
        "company": {
            "id": company.id,
            "company_id": company.company_id,
            "name": company.name,
            "industry": company.industry,
            "location": company.location,
            "website": company.website,
            "description": company.description,
            "hr_name": company.hr_name,
            "hr_email": company.hr_email,
            "approved": company.approved,
            "is_active": company.is_active
        }
    }), 200


@company_bp.route("/api/company/profile", methods=["PUT"])
@jwt_required()
def update_company_profile():

    user, company, error = get_current_company()

    if error:
        return error

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid or missing JSON data"
        }), 400

    required_fields = [
        "name",
        "industry",
        "location",
        "hr_name",
        "hr_email"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    company.name = data["name"]
    company.industry = data["industry"]
    company.location = data["location"]
    company.website = data.get("website")
    company.description = data.get("description")
    company.hr_name = data["hr_name"]
    company.hr_email = data["hr_email"]

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Company profile updated successfully"
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update company profile"
        }), 500


@company_bp.route("/api/company/jobs", methods=["POST"])
@jwt_required()
def create_job():

    user, company, error = get_current_company()

    if error:
        return error

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid or missing JSON data"
        }), 400

    required_fields = [
        "title",
        "description",
        "location",
        "experience",
        "skills_required",
        "deadline",
        "min_cgpa"
    ]

    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        deadline = datetime.strptime(
            data["deadline"],
            "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Deadline must be in YYYY-MM-DD format"
        }), 400

    salary = data.get("salary")

    if salary not in [None, ""]:
        try:
            salary = float(salary)

            if salary < 0:
                return jsonify({
                    "success": False,
                    "message": "Salary cannot be negative"
                }), 400

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Salary must be a valid number"
            }), 400
    else:
        salary = None

    try:
        min_cgpa = float(data["min_cgpa"])

        if min_cgpa < 0 or min_cgpa > 10:
            return jsonify({
                "success": False,
                "message": "Minimum CGPA must be between 0 and 10"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Minimum CGPA must be a valid number"
        }), 400

    application_limit = data.get("application_limit")

    if application_limit not in [None, ""]:
        try:
            application_limit = int(application_limit)

            if application_limit <= 0:
                return jsonify({
                    "success": False,
                    "message": "Application limit must be greater than 0"
                }), 400

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Application limit must be a valid integer"
            }), 400
    else:
        application_limit = None

    job = JobPosition(
        company_id=company.id,
        title=data["title"],
        description=data["description"],
        location=data["location"],
        salary=salary,
        experience=data["experience"],
        skills_required=data["skills_required"],
        benefits=data.get("benefits"),
        min_cgpa=min_cgpa,
        deadline=deadline,
        application_limit=application_limit,
        status="Pending",
        last_updated_by="company"
    )

    try:
        db.session.add(job)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Job created successfully. Waiting for admin approval.",
            "job": {
                "id": job.id,
                "title": job.title,
                "status": job.status
            }
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to create job"
        }), 500

@company_bp.route("/api/company/jobs", methods=["GET"])
@jwt_required()
def get_company_jobs():

    user, company, error = get_current_company()

    if error:
        return error

    jobs = JobPosition.query.filter_by(
        company_id=company.id
    ).order_by(
        JobPosition.created_at.desc()
    ).all()

    return jsonify({
        "success": True,
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "location": job.location,
                "salary": job.salary,
                "experience": job.experience,
                "skills_required": job.skills_required,
                "benefits": job.benefits,
                "min_cgpa": job.min_cgpa,
                "deadline": job.deadline.isoformat(),
                "application_limit": job.application_limit,
                "status": job.status,
                "created_at": job.created_at.isoformat()
                    if job.created_at else None,
                "updated_at": job.updated_at.isoformat()
                    if job.updated_at else None
            }
            for job in jobs
        ]
    }), 200

@company_bp.route("/api/company/jobs/<int:job_id>", methods=["PUT"])
@jwt_required()
def update_company_job(job_id):

    user, company, error = get_current_company()

    if error:
        return error

    job = JobPosition.query.filter_by(
        id=job_id,
        company_id=company.id
    ).first()

    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid or missing JSON data"
        }), 400

    required_fields = [
        "title",
        "description",
        "location",
        "experience",
        "skills_required",
        "deadline",
        "min_cgpa"
    ]

    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        deadline = datetime.strptime(
            data["deadline"],
            "%Y-%m-%d"
        ).date()
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Deadline must be in YYYY-MM-DD format"
        }), 400

    salary = data.get("salary")

    if salary not in [None, ""]:
        try:
            salary = float(salary)

            if salary < 0:
                return jsonify({
                    "success": False,
                    "message": "Salary cannot be negative"
                }), 400

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Salary must be a valid number"
            }), 400
    else:
        salary = None

    try:
        min_cgpa = float(data["min_cgpa"])

        if min_cgpa < 0 or min_cgpa > 10:
            return jsonify({
                "success": False,
                "message": "Minimum CGPA must be between 0 and 10"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Minimum CGPA must be a valid number"
        }), 400

    application_limit = data.get("application_limit")

    if application_limit not in [None, ""]:
        try:
            application_limit = int(application_limit)

            if application_limit <= 0:
                return jsonify({
                    "success": False,
                    "message": "Application limit must be greater than 0"
                }), 400

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Application limit must be a valid integer"
            }), 400
    else:
        application_limit = None

    job.title = data["title"]
    job.description = data["description"]
    job.location = data["location"]
    job.salary = salary
    job.experience = data["experience"]
    job.skills_required = data["skills_required"]
    job.benefits = data.get("benefits")
    job.min_cgpa = min_cgpa
    job.deadline = deadline
    job.application_limit = application_limit
    job.last_updated_by = "company"

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Job updated successfully"
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update job"
        }), 500

@company_bp.route(
    "/api/company/jobs/<int:job_id>/status",
    methods=["PUT"]
)
@jwt_required()
def update_job_status(job_id):

    user, company, error = get_current_company()

    if error:
        return error

    job = JobPosition.query.filter_by(
        id=job_id,
        company_id=company.id
    ).first()

    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    data = request.get_json()

    if not data or "status" not in data:
        return jsonify({
            "success": False,
            "message": "Status is required"
        }), 400

    new_status = data["status"]

    if new_status not in ["Active", "Closed"]:
        return jsonify({
            "success": False,
            "message": "Status must be Active or Closed"
        }), 400

    if job.status in ["Pending", "Rejected", "Inactive"]:
        return jsonify({
            "success": False,
            "message": "This job status cannot be changed by the company"
        }), 403

    job.status = new_status
    job.last_updated_by = "company"

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Job status changed to {new_status}",
            "status": job.status
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update job status"
        }), 500

@company_bp.route(
    "/api/company/jobs/<int:job_id>/applications",
    methods=["GET"]
)
@jwt_required()
def get_job_applications(job_id):

    user, company, error = get_current_company()

    if error:
        return error

    job = JobPosition.query.filter_by(
        id=job_id,
        company_id=company.id
    ).first()

    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    applications = Application.query.filter_by(
        job_id=job.id
    ).order_by(
        Application.applied_at.desc()
    ).all()

    result = []

    for application in applications:

        student = application.student

        result.append({
            "id": application.id,
            "status": application.status,
            "remarks": application.remarks,
            "applied_at": (
                application.applied_at.isoformat()
                if application.applied_at else None
            ),
            "updated_at": (
                application.updated_at.isoformat()
                if application.updated_at else None
            ),
            "interview_datetime": (
                application.interview_datetime.isoformat()
                if application.interview_datetime else None
            ),
            "interview_mode": application.interview_mode,
            "interview_location": application.interview_location,
            "interview_notes": application.interview_notes,
            "student": {
                "id": student.id,
                "student_id": student.student_id,
                "name": student.name,
                "department": student.department,
                "cgpa": student.cgpa,
                "phone": student.phone,
                "skills": student.skills,
                "education": student.education,
                "resume": student.resume
            } if student else None
        })

    return jsonify({
        "success": True,
        "job": {
            "id": job.id,
            "title": job.title,
            "status": job.status
        },
        "applications": result
    }), 200

@company_bp.route(
    "/api/company/applications/<int:application_id>/status",
    methods=["PUT"]
)
@jwt_required()
def update_application_status(application_id):

    user, company, error = get_current_company()

    if error:
        return error

    application = db.session.get(
        Application,
        application_id
    )

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    if (
        not application.job
        or application.job.company_id != company.id
    ):
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid or missing JSON data"
        }), 400

    new_status = data.get("status")
    remarks = data.get("remarks", "")

    if new_status not in ["Shortlisted", "Rejected"]:
        return jsonify({
            "success": False,
            "message": (
                "Status must be Shortlisted or Rejected"
            )
        }), 400

    if new_status == "Rejected" and not remarks.strip():
        return jsonify({
            "success": False,
            "message": "Feedback is required when rejecting an applicant"
        }), 400

    if application.status != "Applied":
        return jsonify({
            "success": False,
            "message": (
                "Only applications with Applied status "
                "can be shortlisted or rejected"
            )
        }), 400

    application.status = new_status
    application.remarks = remarks.strip()

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": (
                f"Application {new_status.lower()} successfully"
            ),
            "application": {
                "id": application.id,
                "status": application.status,
                "remarks": application.remarks
            }
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update application status"
        }), 500


@company_bp.route(
    "/api/company/applications/<int:application_id>/resume",
    methods=["GET"]
)
@jwt_required()
def view_applicant_resume(application_id):

    user, company, error = get_current_company()

    if error:
        return error

    application = db.session.get(
        Application,
        application_id
    )

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    if (
        not application.job
        or application.job.company_id != company.id
    ):
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    student = application.student

    if not student or not student.resume:
        return jsonify({
            "success": False,
            "message": "Resume not found"
        }), 404

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        student.resume
    )

@company_bp.route(
    "/api/company/applications/<int:application_id>/interview",
    methods=["PUT"]
)
@jwt_required()
def schedule_interview(application_id):

    user, company, error = get_current_company()

    if error:
        return error

    application = db.session.get(
        Application,
        application_id
    )

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    if (
        not application.job
        or application.job.company_id != company.id
    ):
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    if application.status != "Shortlisted":
        return jsonify({
            "success": False,
            "message": (
                "Interview can only be scheduled "
                "for shortlisted applicants"
            )
        }), 400

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid or missing JSON data"
        }), 400

    required_fields = [
        "interview_datetime",
        "interview_mode"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        interview_datetime = datetime.fromisoformat(
            data["interview_datetime"]
        )
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": (
                "Interview date/time must be in "
                "valid ISO format"
            )
        }), 400

    if interview_datetime <= datetime.now():
        return jsonify({
            "success": False,
            "message": (
                "Interview date/time must be in the future"
            )
        }), 400

    interview_mode = data["interview_mode"].strip()

    if not interview_mode:
        return jsonify({
            "success": False,
            "message": "Interview mode is required"
        }), 400

    application.interview_datetime = interview_datetime
    application.interview_mode = interview_mode
    application.interview_location = (
        data.get("interview_location") or ""
    ).strip()
    application.interview_notes = (
        data.get("interview_notes") or ""
    ).strip()

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Interview scheduled successfully",
            "interview": {
                "datetime": (
                    application.interview_datetime.isoformat()
                ),
                "mode": application.interview_mode,
                "location": application.interview_location,
                "notes": application.interview_notes
            }
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to schedule interview"
        }), 500


@company_bp.route(
    "/api/company/applications/<int:application_id>/final-status",
    methods=["PUT"]
)
@jwt_required()
def update_final_application_status(application_id):

    user, company, error = get_current_company()

    if error:
        return error

    application = db.session.get(
        Application,
        application_id
    )

    if not application:
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    if (
        not application.job
        or application.job.company_id != company.id
    ):
        return jsonify({
            "success": False,
            "message": "Application not found"
        }), 404

    if application.status != "Shortlisted":
        return jsonify({
            "success": False,
            "message": (
                "Final decision can only be made "
                "for shortlisted applicants"
            )
        }), 400

    if not application.interview_datetime:
        return jsonify({
            "success": False,
            "message": (
                "Schedule an interview before making "
                "the final decision"
            )
        }), 400

    data = request.get_json()

    if not data or "status" not in data:
        return jsonify({
            "success": False,
            "message": "Status is required"
        }), 400

    new_status = data["status"]

    if new_status not in ["Selected", "Rejected"]:
        return jsonify({
            "success": False,
            "message": (
                "Status must be Selected or Rejected"
            )
        }), 400

    remarks = data.get("remarks", "").strip()

    if new_status == "Rejected" and not remarks:
        return jsonify({
            "success": False,
            "message": (
                "Feedback is required when rejecting "
                "an applicant"
            )
        }), 400

    application.status = new_status

    if remarks:
        application.remarks = remarks

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": (
                f"Applicant marked as {new_status.lower()}"
            ),
            "application": {
                "id": application.id,
                "status": application.status,
                "remarks": application.remarks
            }
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": (
                "Failed to update application status"
            )
        }), 500