from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app import db, cache
from app.models import (
    User,
    Student,
    Company,
    JobPosition,
    Application,
)


admin_bp = Blueprint("admin", __name__)


def admin_required():
    claims = get_jwt()

    if claims.get("role") != User.ADMIN:
        return False

    return True


def get_cached_admin_companies(search):
    try:
        query = Company.query

        if search:
            query = query.filter(
                db.or_(
                    Company.name.ilike(f"%{search}%"),
                    Company.industry.ilike(f"%{search}%")
                )
            )

        companies = query.order_by(
            Company.created_at.desc()
        ).all()

        result = []

        for company in companies:
            result.append({
                "id": company.id,
                "company_id": company.company_id,
                "name": company.name,
                "industry": company.industry,
                "location": company.location,
                "website": company.website,
                "description": company.description,
                "hr_name": company.hr_name,
                "hr_email": company.hr_email,
                "approved": bool(company.approved),
                "is_active": bool(company.is_active),
                "created_at": (
                    company.created_at.isoformat()
                    if company.created_at else None
                )
            })

        return result

    except Exception as e:
        print("ERROR loading admin companies:", repr(e))
        raise



def get_cached_admin_students(search):

    query = Student.query

    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f"%{search}%"),
                Student.student_id.ilike(f"%{search}%"),
                Student.phone.ilike(f"%{search}%")
            )
        )

    students = query.order_by(
        Student.created_at.desc()
    ).all()

    result = []

    for student in students:
        result.append({
            "id": student.id,
            "student_id": student.student_id,
            "name": student.name,
            "department": student.department,
            "cgpa": student.cgpa,
            "phone": student.phone,
            "skills": student.skills,
            "education": student.education,
            "resume": student.resume,
            "is_active": student.is_active,
            "created_at": (
                student.created_at.isoformat()
                if student.created_at else None
            )
        })

    return result



def get_cached_admin_jobs():

    jobs = JobPosition.query.order_by(
        JobPosition.created_at.desc()
    ).all()

    result = []

    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "salary": job.salary,
            "experience": job.experience,
            "skills_required": job.skills_required,
            "deadline": (
                job.deadline.isoformat()
                if job.deadline else None
            ),
            "application_limit": job.application_limit,
            "status": job.status,
            "company": {
                "id": job.company.id,
                "company_id": job.company.company_id,
                "name": job.company.name
            } if job.company else None,
            "application_count": len(job.applications),
            "created_at": (
                job.created_at.isoformat()
                if job.created_at else None
            )
        })

    return result



@admin_bp.route("/api/admin/dashboard", methods=["GET"])
@jwt_required()
def dashboard():

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_jobs = JobPosition.query.count()
    total_applications = Application.query.count()

    return jsonify({
        "success": True,
        "stats": {
            "total_students": total_students,
            "total_companies": total_companies,
            "total_jobs": total_jobs,
            "total_applications": total_applications
        }
    }), 200



@admin_bp.route("/api/admin/companies", methods=["GET"])
@jwt_required()
def get_companies():

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    try:
        search = request.args.get("search", "").strip().lower()

        companies = get_cached_admin_companies(search)

        return jsonify({
            "success": True,
            "companies": companies
        }), 200

    except Exception as e:
        print("ADMIN COMPANIES ERROR:", repr(e))

        return jsonify({
            "success": False,
            "message": "Failed to load companies",
            "error": str(e)
        }), 500


@admin_bp.route(
    "/api/admin/company/<int:company_id>/approve",
    methods=["PUT"]
)
@jwt_required()
def approve_company(company_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    company = db.session.get(
        Company,
        company_id
    )

    if not company:
        return jsonify({
            "success": False,
            "message": "Company not found"
        }), 404

    company.approved = True
    company.is_active = True

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Company approved successfully"
    }), 200


@admin_bp.route(
    "/api/admin/company/<int:company_id>/deactivate",
    methods=["PUT"]
)
@jwt_required()
def deactivate_company(company_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    company = db.session.get(
        Company,
        company_id
    )

    if not company:
        return jsonify({
            "success": False,
            "message": "Company not found"
        }), 404

    company.is_active = False

    for job in company.jobs:
        if job.status == "Active":
            job.status = "Inactive"
            job.last_updated_by = "admin"

    db.session.commit()


    return jsonify({
        "success": True,
        "message": (
            "Company and its active job postings "
            "have been deactivated"
        )
    }), 200


@admin_bp.route(
    "/api/admin/company/<int:company_id>/activate",
    methods=["PUT"]
)
@jwt_required()
def activate_company(company_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    company = db.session.get(
        Company,
        company_id
    )

    if not company:
        return jsonify({
            "success": False,
            "message": "Company not found"
        }), 404

    company.is_active = True

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Company activated successfully"
    }), 200



@admin_bp.route("/api/admin/students", methods=["GET"])
@jwt_required()
def get_students():

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    search = request.args.get(
        "search",
        ""
    ).strip().lower()

    students = get_cached_admin_students(search)

    return jsonify({
        "success": True,
        "students": students
    }), 200


@admin_bp.route(
    "/api/admin/student/<int:student_id>/deactivate",
    methods=["PUT"]
)
@jwt_required()
def deactivate_student(student_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    student = db.session.get(
        Student,
        student_id
    )

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    student.is_active = False

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Student deactivated successfully"
    }), 200


@admin_bp.route(
    "/api/admin/student/<int:student_id>/activate",
    methods=["PUT"]
)
@jwt_required()
def activate_student(student_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    student = db.session.get(
        Student,
        student_id
    )

    if not student:
        return jsonify({
            "success": False,
            "message": "Student not found"
        }), 404

    student.is_active = True

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Student activated successfully"
    }), 200



@admin_bp.route("/api/admin/jobs", methods=["GET"])
@jwt_required()
def get_jobs():

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    jobs = get_cached_admin_jobs()

    return jsonify({
        "success": True,
        "jobs": jobs
    }), 200


@admin_bp.route(
    "/api/admin/job/<int:job_id>/approve",
    methods=["PUT"]
)
@jwt_required()
def approve_job(job_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    job = db.session.get(
        JobPosition,
        job_id
    )

    if not job:
        return jsonify({
            "success": False,
            "message": "Job posting not found"
        }), 404

    job.status = "Active"
    job.last_updated_by = "admin"

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Job posting approved successfully"
    }), 200


@admin_bp.route(
    "/api/admin/job/<int:job_id>/reject",
    methods=["PUT"]
)
@jwt_required()
def reject_job(job_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin Access Required"
        }), 403

    job = db.session.get(
        JobPosition,
        job_id
    )

    if not job:
        return jsonify({
            "success": False,
            "message": "Job posting not found"
        }), 404

    job.status = "Rejected"
    job.last_updated_by = "admin"

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Job posting rejected successfully"
    }), 200


@admin_bp.route(
    "/api/admin/job/<int:job_id>/deactivate",
    methods=["PUT"]
)
@jwt_required()
def deactivate_job(job_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    job = db.session.get(
        JobPosition,
        job_id
    )

    if not job:
        return jsonify({
            "success": False,
            "message": "Job posting not found"
        }), 404

    job.status = "Inactive"
    job.last_updated_by = "admin"

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Job posting deactivated successfully"
    }), 200


@admin_bp.route(
    "/api/admin/job/<int:job_id>/activate",
    methods=["PUT"]
)
@jwt_required()
def activate_job(job_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    job = db.session.get(
        JobPosition,
        job_id
    )

    if not job:
        return jsonify({
            "success": False,
            "message": "Job posting not found"
        }), 404

    if job.status != "Inactive":
        return jsonify({
            "success": False,
            "message": "Only deactivated jobs can be reactivated"
        }), 400

    job.status = "Active"
    job.last_updated_by = "admin"

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Job posting reactivated successfully"
    }), 200


@admin_bp.route(
    "/api/admin/company/<int:company_id>/revoke",
    methods=["PUT"]
)
@jwt_required()
def revoke_company_approval(company_id):

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    company = db.session.get(
        Company,
        company_id
    )

    if not company:
        return jsonify({
            "success": False,
            "message": "Company not found"
        }), 404

    company.approved = False

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Company approval revoked successfully"
    }), 200



@admin_bp.route(
    "/api/admin/applications",
    methods=["GET"]
)
@jwt_required()
def get_applications():

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin access required"
        }), 403

    applications = Application.query.order_by(
        Application.applied_at.desc()
    ).all()

    result = []

    for application in applications:
        result.append({
            "id": application.id,
            "status": application.status,
            "remarks": application.remarks,
            "applied_at": (
                application.applied_at.isoformat()
                if application.applied_at else None
            ),

            "student": {
                "id": application.student.id,
                "student_id": application.student.student_id,
                "name": application.student.name
            } if application.student else None,

            "job": {
                "id": application.job.id,
                "title": application.job.title,
                "company": (
                    application.job.company.name
                    if application.job.company
                    else None
                )
            } if application.job else None
        })

    return jsonify({
        "success": True,
        "applications": result
    }), 200