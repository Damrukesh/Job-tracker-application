from app import create_app, db
from app.models import Role
app = create_app()

with app.app_context():
    db.create_all()

    if not Role.query.first():
        db.session.add(Role(role_name="admin"))
        db.session.add(Role(role_name="manager"))
        db.session.add(Role(role_name="user"))
        db.session.commit()
if __name__ == "__main__":
    app.run(debug=True)