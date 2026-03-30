from app import create_app, db
from app.models import Role
app = create_app()

with app.app_context():
    db.create_all()

    # Ensure default roles exist and legacy role names are normalized.
    # Legacy names:
    # - "manager" -> "recruiter"
    # - "user" -> "candidate"
    legacy_map = {"manager": "recruiter", "user": "candidate"}

    for old_name, new_name in legacy_map.items():
        old_role = Role.query.filter_by(role_name=old_name).first()
        if old_role and not Role.query.filter_by(role_name=new_name).first():
            old_role.role_name = new_name

    for role_name in ("admin", "recruiter", "candidate"):
        if not Role.query.filter_by(role_name=role_name).first():
            db.session.add(Role(role_name=role_name))

    db.session.commit()
if __name__ == "__main__":
    app.run(debug=True)