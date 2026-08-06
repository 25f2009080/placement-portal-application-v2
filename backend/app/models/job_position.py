from datetime import datetime, UTC

from app import db


class JobPosition(db.Model):
    __tablename__ = "job_positions"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id"),
        nullable=False
    )


    title = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    location = db.Column(
        db.String(100),
        nullable=False
    )

    salary = db.Column(
        db.Float
    )

    experience = db.Column(
        db.String(50)
    )

    skills_required = db.Column(
        db.Text,
        default=""
    )


    deadline = db.Column(
        db.Date,
        nullable=False
    )

    application_limit = db.Column(
        db.Integer,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )


    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    last_updated_by = db.Column(
        db.String(50),
        nullable=True
    )


    company = db.relationship(
        "Company",
        back_populates="jobs"
    )

    applications = db.relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy=True
    )

    placements = db.relationship(
        "Placement",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<JobPosition {self.title}>"