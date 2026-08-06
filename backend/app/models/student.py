from datetime import datetime

from app import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    student_id = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    cgpa = db.Column(
        db.Float,
        nullable=True
    )

    phone = db.Column(
        db.String(15),
        nullable=False
    )

    skills = db.Column(
        db.Text,
        default="",
        nullable=True
    )

    education = db.Column(
        db.Text,
         default="",
        nullable=True
    )

    resume = db.Column(
        db.String(255),
         default="",
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    user = db.relationship(
        "User",
        back_populates="student"
    )

    applications = db.relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy=True
    )

    placements = db.relationship(
        "Placement",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Student {self.student_id}>"