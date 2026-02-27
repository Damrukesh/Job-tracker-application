from flask import Blueprint, request, jsonify
from .models import User
from . import db, bcrypt
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity,get_jwt
from .models import Role

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/signup", methods=["POST"])
def signup():
    data = request.json

    hashed_pw = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    # Get default role = "user"
    default_role = Role.query.filter_by(role_name="user").first()

    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=hashed_pw,
        role=default_role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201

@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    # ❗ Check user exists
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # ❗ Check password
    try:
        password_ok = bcrypt.check_password_hash(
            user.password_hash, data["password"]
        )
    except ValueError:
        # Stored hash is invalid or corrupted – treat as bad credentials
        return jsonify({"error": "Invalid credentials"}), 401

    if not password_ok:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role.role_name}
    )

    return jsonify({"access_token": token})
    
@auth_routes.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({"user_id": current_user_id})
@auth_routes.route("/admin", methods=["GET"])
@jwt_required()
def admin_only():
    # Always check role from DB to avoid stale tokens
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.role or user.role.role_name != "admin":
        return jsonify({"error": "Admins only"}), 403

    return jsonify({"message": "Welcome Admin"})


@auth_routes.route("/admin/users", methods=["GET"])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # 🔒 Admin-only protection based on DB role
    if not user or not user.role or user.role.role_name != "admin":
        return jsonify({"error": "Admins only"}), 403

    users = User.query.all()

    result = []
    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role.role_name
        })

    return jsonify(result)    
@auth_routes.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.role_name
    })