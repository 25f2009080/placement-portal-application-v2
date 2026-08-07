from app import create_app, db
from app.models import User

app = create_app()


def create_admin():

    admin = User.query.filter_by(username="admin").first()

    if admin:
        print("Admin user already exists.")
        return

    admin = User(
        username="admin",
        email="admin@placementportal.com",
        role="admin"
    )

    admin.set_password("admin123")

    db.session.add(admin)
    db.session.commit()

    print("Default admin created successfully.")


with app.app_context():

    print("Creating database...")

    db.create_all()

    print("Database created successfully.")

    create_admin()

    print("Initialization complete.")