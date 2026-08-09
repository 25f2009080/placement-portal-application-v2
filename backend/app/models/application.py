from datetime import datetime, UTC

from app import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)


    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job_positions.id"),
        nullable=False
    )


    status = db.Column(
        db.String(20),
        default="Applied",
        nullable=False
    )

    remarks = db.Column(
        db.Text,
        default=""
    )

    interview_datetime = db.Column(
        db.DateTime,
        nullable=True
    )

    interview_mode = db.Column(
        db.String(50),
        nullable=True
    )

    interview_location = db.Column(
        db.String(255),
        nullable=True
    )

    interview_notes = db.Column(
        db.Text,
        nullable=True
    )

    applied_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )


    student = db.relationship(
        "Student",
        back_populates="applications"
    )

    job = db.relationship(
        "JobPosition",
        back_populates="applications"
    )

    placement = db.relationship(
        "Placement",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan"
    )


    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "job_id",
            name="unique_student_application"
        ),
    )

    def __repr__(self):
        return (
            f"<Application Student={self.student_id} "
            f"Job={self.job_id} Status={self.status}>"
        )