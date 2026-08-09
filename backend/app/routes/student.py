from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models import User, Student


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