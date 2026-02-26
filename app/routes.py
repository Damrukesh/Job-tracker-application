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
    )

    role_name = data.get("role", "user")
    selected_role = Role.query.filter_by(role_name=role_name).first()

    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=hashed_pw,
        role=selected_role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201

@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not bcrypt.check_password_hash(
        user.password_hash, data["password"]
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": str(user.role.role_name)}
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
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"error": "Admins only"}), 403
    return jsonify({"message": "Welcome Admin"})
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