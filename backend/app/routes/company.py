from datetime import datetime, UTC
import os

from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Company, JobPosition, Application, Placement

from celery.result import AsyncResult
from app.tasks.exports import export_application_history


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



def get_cached_company_jobs(company_id):

    jobs = JobPosition.query.filter_by(
        company_id=company_id
    ).order_by(
        JobPosition.created_at.desc()
    ).all()

    return [
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
            "deadline": (
                job.deadline.isoformat()
                if job.deadline else None
            ),
            "application_limit": job.application_limit,
            "status": job.status,
            "created_at": (
                job.created_at.isoformat()
                if job.created_at else None
            ),
            "updated_at": (
                job.updated_at.isoformat()
                if job.updated_at else None
            )
        }
        for job in jobs
    ]


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

    jobs = get_cached_company_jobs(company.id)

    return jsonify({
        "success": True,
        "jobs": jobs
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

    application.status = "Interview"

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Interview scheduled successfully",
            "application": {
                "id": application.id,
                "status": application.status
            },
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

    if application.status != "Interview":
        return jsonify({
            "success": False,
            "message": (
                "Final decision can only be made "
                "after the interview stage"
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

    if request.content_type and request.content_type.startswith(
        "multipart/form-data"
    ):
        new_status = request.form.get("status")
        remarks = (
            request.form.get("remarks") or ""
        ).strip()

        offer_letter = request.files.get(
            "offer_letter"
        )

    else:
        data = request.get_json(silent=True)

        if not data or "status" not in data:
            return jsonify({
                "success": False,
                "message": "Status is required"
            }), 400

        new_status = data["status"]

        remarks = (
            data.get("remarks") or ""
        ).strip()

        offer_letter = None

    if new_status not in ["Offer", "Rejected"]:
        return jsonify({
            "success": False,
            "message": (
                "Status must be Offer or Rejected"
            )
        }), 400

    if new_status == "Rejected":

        if not remarks:
            return jsonify({
                "success": False,
                "message": (
                    "Feedback is required when rejecting "
                    "an applicant"
                )
            }), 400

        application.status = "Rejected"
        application.remarks = remarks

        try:
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Applicant marked as rejected",
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

    if offer_letter is None or not offer_letter.filename:
        return jsonify({
            "success": False,
            "message": (
                "Offer letter PDF is required "
                "when making an offer"
            )
        }), 400

    original_filename = offer_letter.filename

    if "." not in original_filename:
        return jsonify({
            "success": False,
            "message": "Invalid offer letter file"
        }), 400

    extension = original_filename.rsplit(
        ".",
        1
    )[1].lower()

    if extension != "pdf":
        return jsonify({
            "success": False,
            "message": "Only PDF offer letters are allowed"
        }), 400

    try:
        offer_letter.stream.seek(0, os.SEEK_END)
        file_size = offer_letter.stream.tell()
        offer_letter.stream.seek(0)

    except (OSError, AttributeError):
        return jsonify({
            "success": False,
            "message": "Could not validate offer letter size"
        }), 400

    if file_size > 5 * 1024 * 1024:
        return jsonify({
            "success": False,
            "message": (
                "Offer letter must be smaller than 5 MB"
            )
        }), 400

    filename = secure_filename(
        original_filename
    )

    if not filename:
        return jsonify({
            "success": False,
            "message": "Invalid offer letter filename"
        }), 400

    job = application.job
    student = application.student

    if not student:
        return jsonify({
            "success": False,
            "message": (
                "Student associated with application "
                "not found"
            )
        }), 404

    existing_placement = Placement.query.filter_by(
        application_id=application.id
    ).first()

    if existing_placement:
        return jsonify({
            "success": False,
            "message": (
                "An offer or placement already exists "
                "for this application"
            )
        }), 409

    if job.salary is None:
        return jsonify({
            "success": False,
            "message": (
                "Set a salary for this placement drive "
                "before making an offer"
            )
        }), 400

    joining_date = None

    if request.form.get("joining_date"):
        try:
            joining_date = datetime.strptime(
                request.form.get("joining_date"),
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": (
                    "Joining date must be in YYYY-MM-DD format"
                )
            }), 400

    upload_folder = current_app.config[
        "UPLOAD_FOLDER"
    ]

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    base_name, file_extension = os.path.splitext(
        filename
    )

    filename = (
        f"offer_{application.id}_{base_name}"
        f"{file_extension}"
    )

    file_path = os.path.join(
        upload_folder,
        filename
    )

    try:
        offer_letter.save(file_path)

        placement = Placement(
            application_id=application.id,
            student_id=student.id,
            company_id=company.id,
            job_id=job.id,
            position=job.title,
            salary=job.salary,
            joining_date=joining_date,
            placed_at=None,
            offer_letter=filename
        )

        application.status = "Offer"
        application.remarks = remarks

        db.session.add(placement)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": (
                "Offer issued and offer letter uploaded successfully"
            ),
            "application": {
                "id": application.id,
                "status": application.status,
                "remarks": application.remarks
            },
            "placement": {
                "id": placement.id,
                "position": placement.position,
                "salary": placement.salary,
                "joining_date": (
                    placement.joining_date.isoformat()
                    if placement.joining_date
                    else None
                ),
                "placed_at": None,
                "offer_letter": placement.offer_letter
            }
        }), 200

    except Exception:
        db.session.rollback()

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

        return jsonify({
            "success": False,
            "message": (
                "Failed to create offer or upload "
                "offer letter"
            )
        }), 500


@company_bp.route(
    "/api/company/applications/<int:application_id>/placed",
    methods=["PUT"]
)
@jwt_required()
def mark_application_placed(application_id):

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

    if application.status != "Offer":
        return jsonify({
            "success": False,
            "message": (
                "Only applicants with an active offer "
                "can be marked as placed"
            )
        }), 400

    placement = Placement.query.filter_by(
        application_id=application.id
    ).first()

    if not placement:
        return jsonify({
            "success": False,
            "message": (
                "Placement record not found for this offer"
            )
        }), 404

    if placement.placed_at:
        application.status = "Placed"

        try:
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Applicant is already placed",
                "application": {
                    "id": application.id,
                    "status": application.status,
                    "remarks": application.remarks
                },
                "placement": {
                    "id": placement.id,
                    "position": placement.position,
                    "salary": placement.salary,
                    "joining_date": (
                        placement.joining_date.isoformat()
                        if placement.joining_date
                        else None
                    ),
                    "placed_at": (
                        placement.placed_at.isoformat()
                        if placement.placed_at
                        else None
                    ),
                    "offer_letter": placement.offer_letter
                }
            }), 200

        except Exception:
            db.session.rollback()

            return jsonify({
                "success": False,
                "message": (
                    "Failed to synchronize placement status"
                )
            }), 500

    application.status = "Placed"
    placement.placed_at = datetime.now(UTC)

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Applicant marked as placed successfully",
            "application": {
                "id": application.id,
                "status": application.status,
                "remarks": application.remarks
            },
            "placement": {
                "id": placement.id,
                "position": placement.position,
                "salary": placement.salary,
                "joining_date": (
                    placement.joining_date.isoformat()
                    if placement.joining_date
                    else None
                ),
                "placed_at": (
                    placement.placed_at.isoformat()
                    if placement.placed_at
                    else None
                ),
                "offer_letter": placement.offer_letter
            }
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to mark applicant as placed"
        }), 500


@company_bp.route(
    "/api/company/export-history",
    methods=["POST"]
)
@jwt_required()
def start_company_export():

    from app.tasks.exports import export_application_history

    user, company, error = get_current_company()

    if error:
        return error

    task = export_application_history.delay(
        "company",
        company.id
    )

    return jsonify({
        "success": True,
        "message": "Export started",
        "task_id": task.id
    }), 202


@company_bp.route(
    "/api/company/export-history/status/<task_id>",
    methods=["GET"]
)
@jwt_required()
def company_export_status(task_id):

    from celery.result import AsyncResult
    from app.celery_app import celery

    user, company, error = get_current_company()

    if error:
        return error

    task = AsyncResult(
        task_id,
        app=celery
    )

    if task.state == "PENDING":
        return jsonify({
            "success": True,
            "status": "PENDING"
        }), 200

    if task.state == "STARTED":
        return jsonify({
            "success": True,
            "status": "STARTED"
        }), 200

    if task.state == "SUCCESS":

        result = task.result

        return jsonify({
            "success": True,
            "status": "SUCCESS",
            "filename": result.get("filename"),
            "records": result.get("records", 0)
        }), 200

    if task.state == "FAILURE":
        return jsonify({
            "success": False,
            "status": "FAILURE",
            "message": "CSV export failed"
        }), 500

    return jsonify({
        "success": True,
        "status": task.state
    }), 200


@company_bp.route(
    "/api/company/export-history/download/<task_id>",
    methods=["GET"]
)
@jwt_required()
def download_company_export(task_id):

    from celery.result import AsyncResult
    from app.celery_app import celery

    user, company, error = get_current_company()

    if error:
        return error

    task = AsyncResult(
        task_id,
        app=celery
    )

    if not task.ready():
        return jsonify({
            "success": False,
            "message": "Export is not ready yet"
        }), 400

    if task.failed():
        return jsonify({
            "success": False,
            "message": "Export failed"
        }), 500

    result = task.result

    filepath = result.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return jsonify({
            "success": False,
            "message": "Export file not found"
        }), 404

    return send_from_directory(
        os.path.dirname(filepath),
        os.path.basename(filepath),
        as_attachment=True
    )


@company_bp.route(
    "/api/company/placement-report",
    methods=["POST"]
)
@jwt_required()
def start_placement_report():

    from app.tasks.reports import generate_company_placement_report

    user, company, error = get_current_company()

    if error:
        return error

    task = generate_company_placement_report.delay(
        company.id
    )

    return jsonify({
        "success": True,
        "message": "Placement report generation started",
        "task_id": task.id
    }), 202


@company_bp.route(
    "/api/company/placement-report/status/<task_id>",
    methods=["GET"]
)
@jwt_required()
def placement_report_status(task_id):

    from celery.result import AsyncResult
    from app.celery_app import celery

    user, company, error = get_current_company()

    if error:
        return error

    task = AsyncResult(
        task_id,
        app=celery
    )

    if task.state == "PENDING":
        return jsonify({
            "success": True,
            "status": "PENDING"
        }), 200

    if task.state == "STARTED":
        return jsonify({
            "success": True,
            "status": "STARTED"
        }), 200

    if task.state == "SUCCESS":

        result = task.result

        if not result.get("success"):
            return jsonify({
                "success": False,
                "status": "FAILURE",
                "message": result.get(
                    "message",
                    "Report generation failed."
                )
            }), 500

        return jsonify({
            "success": True,
            "status": "SUCCESS",
            "filename": result.get("filename"),
            "total_applications":
                result.get("total_applications", 0),
            "total_placements":
                result.get("total_placements", 0)
        }), 200

    if task.state == "FAILURE":
        return jsonify({
            "success": False,
            "status": "FAILURE",
            "message": "Placement report generation failed."
        }), 500

    return jsonify({
        "success": True,
        "status": task.state
    }), 200


@company_bp.route(
    "/api/company/placement-report/download/<task_id>",
    methods=["GET"]
)
@jwt_required()
def download_placement_report(task_id):

    from celery.result import AsyncResult
    from app.celery_app import celery

    user, company, error = get_current_company()

    if error:
        return error

    task = AsyncResult(
        task_id,
        app=celery
    )

    if not task.ready():
        return jsonify({
            "success": False,
            "message": "Report is not ready yet."
        }), 400

    if task.failed():
        return jsonify({
            "success": False,
            "message": "Report generation failed."
        }), 500

    result = task.result

    if not result.get("success"):
        return jsonify({
            "success": False,
            "message": result.get(
                "message",
                "Report generation failed."
            )
        }), 500

    filepath = result.get("filepath")

    if not filepath or not os.path.exists(filepath):
        return jsonify({
            "success": False,
            "message": "Report file not found."
        }), 404

    return send_from_directory(
        os.path.dirname(filepath),
        os.path.basename(filepath),
        as_attachment=False,
        mimetype="text/html"
    )