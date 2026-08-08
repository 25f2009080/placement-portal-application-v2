from flask import Blueprint, request, jsonify

from app import db
from app.models import User, Student

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register/student", methods=["POST"])
def register_student():
    data = request.get_json()
    if not data:
        return jsonify({
            "message": "Invalid or missing JSON data"
        }), 400

    required_fields = [
        "username",
        "email",
        "password",
        "student_id",
        "name",
        "department",
        "phone",
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "message": f"{field} is required"
            }), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({
            "message": "Username already exists"
        }), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({
            "message": "Email already exists"
        }), 409

    if Student.query.filter_by(student_id=data["student_id"]).first():
        return jsonify({
            "message": "Student ID already exists"
        }), 409

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            role=User.STUDENT,
        )

        user.set_password(data["password"])

        student = Student(
            user=user,
            student_id=data["student_id"],
            name=data["name"],
            department=data["department"],
            phone=data["phone"],
        )

        db.session.add(user)
        db.session.add(student)
        db.session.commit()

        return jsonify({
            "message": "Student registered successfully"
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "message": "Registration failed",
            "error": str(e)
        }), 500