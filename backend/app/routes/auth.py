from flask import Blueprint, request, jsonify

from app import db
from app.models import User, Student, Company

from flask_jwt_extended import create_access_token
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

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

@auth_bp.route("/api/register/company", methods=["POST"])
def register_company():
    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Invalid or missing JSON data"
        }), 400

    required_fields = [
        "username",
        "email",
        "password",
        "company_id",
        "name",
        "industry",
        "location",
        "hr_name",
        "hr_email",
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

    if Company.query.filter_by(company_id=data["company_id"]).first():
        return jsonify({
            "message": "Company ID already exists"
        }), 409

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            role=User.COMPANY,
        )

        user.set_password(data["password"])

        company = Company(
            user=user,
            company_id=data["company_id"],
            name=data["name"],
            industry=data["industry"],
            location=data["location"],
            website=data.get("website"),
            description=data.get("description"),
            hr_name=data["hr_name"],
            hr_email=data["hr_email"],
            approved=False,
            is_active=True,
        )

        db.session.add(user)
        db.session.add(company)

        db.session.commit()

        return jsonify({
            "message": "Company registered successfully. Waiting for admin approval."
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            "message": "Registration failed"
        }), 500

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Invalid or missing JSON data"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "message": "Username and password are required"
        }), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({
            "message": "Invalid username or password"
        }), 401

    if user.role == User.STUDENT:
        if not user.student.is_active:
            return jsonify({
                "message": "Your account has been blocked by the administrator."
            }), 403

    elif user.role == User.COMPANY:
        if not user.company.approved:
            return jsonify({
                "message": "Your company registration is pending admin approval."
            }), 403

        if not user.company.is_active:
            return jsonify({
                "message": "Your company account has been deactivated."
            }), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "username": user.username
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }), 200