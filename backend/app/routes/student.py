from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from app import db
from app.models import User, Student, JobPosition, Application


student_bp = Blueprint("student", __name__)


def get_current_student():
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

    if user.role != User.STUDENT:
        return None, None, (
            jsonify({
                "success": False,
                "message": "Student access required"
            }),
            403
        )

    student = user.student

    if not student:
        return None, None, (
            jsonify({
                "success": False,
                "message": "Student profile not found"
            }),
            404
        )

    if not student.is_active:
        return None, None, (
            jsonify({
                "success": False,
                "message": "Student account is inactive"
            }),
            403
        )

    return user, student, None


@student_bp.route("/api/student/profile", methods=["GET"])
@jwt_required()
def get_student_profile():

    user, student, error = get_current_student()

    if error:
        return error

    return jsonify({
        "success": True,
        "student": {
            "id": student.id,
            "student_id": student.student_id,
            "name": student.name,
            "department": student.department,
            "cgpa": student.cgpa,
            "phone": student.phone,
            "skills": student.skills,
            "education": student.education,
            "experience": student.experience,
            "resume": student.resume,
            "is_active": student.is_active,
            "email": user.email,
            "username": user.username
        }
    }), 200


@student_bp.route("/api/student/profile", methods=["PUT"])
@jwt_required()
def update_student_profile():

    user, student, error = get_current_student()

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
        "department",
        "phone",
        "cgpa"
    ]

    for field in required_fields:
        if field not in data or data[field] in [None, ""]:
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        cgpa = float(data["cgpa"])

        if cgpa < 0 or cgpa > 10:
            return jsonify({
                "success": False,
                "message": "CGPA must be between 0 and 10"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "CGPA must be a valid number"
        }), 400

    student.name = data["name"].strip()
    student.department = data["department"].strip()
    student.phone = data["phone"].strip()
    student.cgpa = cgpa
    student.skills = (data.get("skills") or "").strip()
    student.education = (data.get("education") or "").strip()
    student.experience = (data.get("experience") or "").strip()

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Student profile updated successfully",
            "student": {
                "id": student.id,
                "student_id": student.student_id,
                "name": student.name,
                "department": student.department,
                "cgpa": student.cgpa,
                "phone": student.phone,
                "skills": student.skills,
                "education": student.education,
                "experience": student.experience,
                "resume": student.resume,
                "is_active": student.is_active
            }
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update student profile"
        }), 500

@student_bp.route("/api/student/jobs", methods=["GET"])
@jwt_required()
def get_student_jobs():

    user, student, error = get_current_student()

    if error:
        return error

    search = request.args.get("search", "").strip().lower()
    company_search = request.args.get("company", "").strip().lower()
    skills_search = request.args.get("skills", "").strip().lower()

    today = date.today()

    jobs = JobPosition.query.filter(
        JobPosition.status == "Active",
        JobPosition.deadline >= today,
        JobPosition.company.has(
            approved=True,
            is_active=True
        )
    ).order_by(
        JobPosition.deadline.asc()
    ).all()

    result = []

    for job in jobs:

        company = job.company

        if not company:
            continue

        if search:
            search_matches = (
                search in (job.title or "").lower()
                or search in (company.name or "").lower()
                or search in (job.skills_required or "").lower()
            )

            if not search_matches:
                continue

        if company_search:
            if company_search not in (company.name or "").lower():
                continue

        if skills_search:
            if skills_search not in (job.skills_required or "").lower():
                continue

        application_count = Application.query.filter_by(
            job_id=job.id
        ).count()

        student_application = Application.query.filter_by(
            student_id=student.id,
            job_id=job.id
        ).first()

        application_limit_reached = (
            job.application_limit is not None
            and application_count >= job.application_limit
        )

        already_applied = student_application is not None

        cgpa_eligible = (
            job.min_cgpa is None
            or student.cgpa is not None
            and student.cgpa >= job.min_cgpa
        )

        can_apply = (
            not already_applied
            and not application_limit_reached
            and cgpa_eligible
        )

        if already_applied:
            application_message = "Already applied"
        elif application_limit_reached:
            application_message = "Application limit reached"
        elif not cgpa_eligible:
            application_message = "CGPA requirement not met"
        else:
            application_message = "Eligible to apply"

        result.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "salary": job.salary,
            "experience": job.experience,
            "skills_required": job.skills_required,
            "benefits": job.benefits,
            "min_cgpa": job.min_cgpa,
            "deadline": job.deadline.isoformat()
                if job.deadline else None,
            "application_limit": job.application_limit,
            "application_count": application_count,
            "application_limit_reached": application_limit_reached,
            "status": job.status,
            "already_applied": already_applied,
            "cgpa_eligible": cgpa_eligible,
            "can_apply": can_apply,
            "application_message": application_message,
            "company": {
                "id": company.id,
                "company_id": company.company_id,
                "name": company.name,
                "industry": company.industry,
                "location": company.location,
                "website": company.website,
                "description": company.description
            }
        })

    return jsonify({
        "success": True,
        "jobs": result
    }), 200



@student_bp.route(
    "/api/student/jobs/<int:job_id>/apply",
    methods=["POST"]
)
@jwt_required()
def apply_for_job(job_id):

    user, student, error = get_current_student()

    if error:
        return error

    job = db.session.get(JobPosition, job_id)

    if not job:
        return jsonify({
            "success": False,
            "message": "Job not found"
        }), 404

    if job.status != "Active":
        return jsonify({
            "success": False,
            "message": "This job is not currently accepting applications"
        }), 400

    company = job.company

    if not company:
        return jsonify({
            "success": False,
            "message": "Company associated with this job was not found"
        }), 404

    if not company.approved:
        return jsonify({
            "success": False,
            "message": "This company is not approved"
        }), 403

    if not company.is_active:
        return jsonify({
            "success": False,
            "message": "This company is currently inactive"
        }), 403

    today = date.today()

    if job.deadline < today:
        return jsonify({
            "success": False,
            "message": "The application deadline has passed"
        }), 400

    if (
        job.min_cgpa is not None
        and (
            student.cgpa is None
            or student.cgpa < job.min_cgpa
        )
    ):
        return jsonify({
            "success": False,
            "message": (
                f"Minimum CGPA required is {job.min_cgpa}"
            )
        }), 400

    existing_application = Application.query.filter_by(
        student_id=student.id,
        job_id=job.id
    ).first()

    if existing_application:
        return jsonify({
            "success": False,
            "message": "You have already applied for this job"
        }), 409

    application_count = Application.query.filter_by(
        job_id=job.id
    ).count()

    if (
        job.application_limit is not None
        and application_count >= job.application_limit
    ):
        return jsonify({
            "success": False,
            "message": "Application limit has been reached"
        }), 400

    application = Application(
        student_id=student.id,
        job_id=job.id,
        status="Applied",
        remarks=""
    )

    try:
        db.session.add(application)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "application": {
                "id": application.id,
                "job_id": job.id,
                "status": application.status,
                "applied_at": (
                    application.applied_at.isoformat()
                    if application.applied_at else None
                )
            }
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to submit application"
        }), 500


@student_bp.route(
    "/api/student/applications",
    methods=["GET"]
)
@jwt_required()
def get_student_applications():

    user, student, error = get_current_student()

    if error:
        return error

    applications = Application.query.filter_by(
        student_id=student.id
    ).order_by(
        Application.applied_at.desc()
    ).all()

    result = []

    for application in applications:

        job = application.job

        if not job:
            continue

        company = job.company

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

            "interview": {
                "datetime": (
                    application.interview_datetime.isoformat()
                    if application.interview_datetime
                    else None
                ),
                "mode": application.interview_mode,
                "location": application.interview_location,
                "notes": application.interview_notes
            },

            "job": {
                "id": job.id,
                "title": job.title,
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
                "status": job.status
            },

            "company": {
                "id": company.id,
                "company_id": company.company_id,
                "name": company.name,
                "industry": company.industry,
                "location": company.location,
                "website": company.website
            } if company else None
        })

    return jsonify({
        "success": True,
        "applications": result
    }), 200