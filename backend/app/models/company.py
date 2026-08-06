from datetime import datetime, UTC

from app import db


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    company_id = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    industry = db.Column(
        db.String(100),
        nullable=False
    )

    location = db.Column(
        db.String(100),
        nullable=False
    )

    website = db.Column(
        db.String(255),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    hr_name = db.Column(
        db.String(100),
        nullable=False
    )

    hr_email = db.Column(
        db.String(100),
        nullable=False
    )

    approved = db.Column(
        db.Boolean,
        default=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True
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


    user = db.relationship(
        "User",
        back_populates="company"
    )

    jobs = db.relationship(
        "JobPosition",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy=True
    )

    placements = db.relationship(
        "Placement",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Company {self.name}>"