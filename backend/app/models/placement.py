from datetime import datetime, UTC

from app import db


class Placement(db.Model):
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)


    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        unique=True,
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id"),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job_positions.id"),
        nullable=False
    )


    position = db.Column(
        db.String(100),
        nullable=False
    )

    salary = db.Column(
        db.Float,
        nullable=False
    )

    joining_date = db.Column(
        db.Date,
        nullable=True
    )

    placed_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )


    application = db.relationship(
        "Application",
        back_populates="placement"
    )

    student = db.relationship(
        "Student",
        back_populates="placements"
    )

    company = db.relationship(
        "Company",
        back_populates="placements"
    )

    job = db.relationship(
        "JobPosition",
        back_populates="placements"
    )

    def __repr__(self):
        return (
            f"<Placement Student={self.student_id} "
            f"Company={self.company_id}>"
        )