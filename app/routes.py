from flask import Blueprint, request, jsonify
from .models import User, JobPost, Application
from . import db, bcrypt
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity,get_jwt
from .models import Role
from werkzeug.utils import secure_filename
from flask import current_app
import os
import re
import fitz
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/signup", methods=["POST"])
def signup():
    data = request.json

    hashed_pw = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    # Default role for signups = "candidate"
    default_role = Role.query.filter_by(role_name="candidate").first()
    if not default_role:
        default_role = Role(role_name="candidate")
        db.session.add(default_role)
        db.session.flush()

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
        identity=str(user.id),
        additional_claims={"role": user.role.role_name}
    )

    return jsonify({"access_token": token})
    
@auth_routes.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = int(get_jwt_identity())
    return jsonify({"user_id": current_user_id})
@auth_routes.route("/admin", methods=["GET"])
@jwt_required()
def admin_only():
    # Always check role from DB to avoid stale tokens
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.role or user.role.role_name != "admin":
        return jsonify({"error": "Admins only"}), 403

    return jsonify({"message": "Welcome Admin"})


@auth_routes.route("/admin/users", methods=["GET"])
@jwt_required()
def get_users():
    user_id = int(get_jwt_identity())
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
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.role_name
    })

@auth_routes.route("/check-admin", methods=["GET"])
@jwt_required()
def check_admin():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    # Not found or missing role -> treat as forbidden for this check
    if not user or not user.role:
        return jsonify({"admin": False}), 403

    if user.role.role_name != "admin":
        return jsonify({"admin": False}), 403

    return jsonify({"admin": True}), 200


@auth_routes.route("/jobs", methods=["GET", "POST"])
@jwt_required()
def jobs():
    # Recruiter can create jobs and view only their own jobs.
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.role or user.role.role_name != "recruiter":
        return jsonify({"error": "Recruiters only"}), 403

    if request.method == "POST":
        data = request.json or {}
        title = data.get("title")
        description = data.get("description")
        location = data.get("location")

        if not title or not description or not location:
            return jsonify({"error": "title, description, and location are required"}), 400

        job = JobPost(
            title=title,
            description=description,
            location=location,
            recruiter_id=user.id,
        )
        db.session.add(job)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "location": job.location,
                    "date_created": job.date_created.isoformat(),
                    "recruiter_id": job.recruiter_id,
                }
            ),
            201,
        )

    # GET
    jobs = (
        JobPost.query.filter_by(recruiter_id=user.id)
        .order_by(JobPost.date_created.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": j.id,
                "title": j.title,
                "description": j.description,
                "location": j.location,
                "date_created": j.date_created.isoformat() if j.date_created else None,
                "applications": [
                    {
                        "id": app.id,
                        "candidate_name": app.candidate_name,
                        "resume_filename": app.resume_filename,
                        "match_score": app.match_score,
                        "user_id": app.user_id,
                    }
                    for app in j.applications
                ],
            }
            for j in jobs
        ]
    )


@auth_routes.route("/jobs/<int:job_id>", methods=["GET"])
@jwt_required()
def job_detail(job_id: int):
    # View a specific job the recruiter created.
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.role or user.role.role_name != "recruiter":
        return jsonify({"error": "Recruiters only"}), 403

    job = JobPost.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.recruiter_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(
        {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "location": job.location,
            "date_created": job.date_created.isoformat() if job.date_created else None,
            "recruiter_id": job.recruiter_id,
            "applications": [
                {
                    "id": app.id,
                    "candidate_name": app.candidate_name,
                    "resume_filename": app.resume_filename,
                    "match_score": app.match_score,
                    "user_id": app.user_id,
                }
                for app in job.applications
            ],
        }
    )


@auth_routes.route("/jobs-feed", methods=["GET"])
@jwt_required()
def jobs_feed():
    # Candidates can see all jobs.
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.role or user.role.role_name != "candidate":
        return jsonify({"error": "Candidates only"}), 403

    jobs = JobPost.query.order_by(JobPost.date_created.desc()).all()
    return jsonify(
        [
            {
                "id": j.id,
                "title": j.title,
                "description": j.description,
                "location": j.location,
                "date_created": j.date_created.isoformat() if j.date_created else None,
            }
            for j in jobs
        ]
    )


ALLOWED_EXTENSIONS = {"pdf"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _extract_pdf_pages_as_list(pdf_path: str) -> list[str]:
    pages_text = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pages_text.append(page.get_text("text") or "")
    return pages_text


def _clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [tok for tok in text.split() if tok and tok not in ENGLISH_STOP_WORDS]
    return " ".join(tokens)


def _compute_match_score(resume_text: str, job_description: str) -> float:
    cleaned_resume = _clean_text(resume_text)
    cleaned_job = _clean_text(job_description)

    if not cleaned_resume.strip() or not cleaned_job.strip():
        return 0.0

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([cleaned_resume, cleaned_job])
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(float(score * 100), 2)


@auth_routes.route("/apply", methods=["POST"])
@jwt_required()
def apply():
    # Candidate applies to a job with a PDF resume.
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.role or user.role.role_name != "candidate":
        return jsonify({"error": "Candidates only"}), 403

    job_id = request.form.get("job_id", type=int)
    candidate_name = request.form.get("candidate_name") or user.name
    file = request.files.get("resume")

    if not job_id or not file:
        return jsonify({"error": "job_id and resume are required"}), 400

    job = JobPost.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if file.filename == "" or not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    # Ensure unique filename per user+job by prefixing.
    unique_name = f"user{user.id}_job{job.id}_{filename}"
    save_path = os.path.join(upload_folder, unique_name)

    file.save(save_path)

    rel_path = os.path.relpath(save_path, current_app.root_path)
    page_texts = _extract_pdf_pages_as_list(save_path)
    resume_text = " ".join(page_texts)
    score = _compute_match_score(resume_text, job.description)

    application = Application(
        candidate_name=candidate_name,
        resume_filename=rel_path,
        match_score=score,
        job_id=job.id,
        user_id=user.id,
    )
    db.session.add(application)
    db.session.commit()

    return jsonify(
        {
            "id": application.id,
            "candidate_name": application.candidate_name,
            "resume_filename": application.resume_filename,
            "match_score": application.match_score,
            "job_id": application.job_id,
            "user_id": application.user_id,
        }
    ), 201


@auth_routes.route("/my-applications", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.role or user.role.role_name != "candidate":
        return jsonify({"error": "Candidates only"}), 403

    apps = (
        Application.query.filter_by(user_id=user.id)
        .order_by(Application.id.desc())
        .all()
    )

    return jsonify(
        [
            {
                "id": app.id,
                "job_id": app.job_id,
                "job_title": app.job.title if app.job else None,
                "candidate_name": app.candidate_name,
                "resume_filename": app.resume_filename,
                "match_score": app.match_score,
            }
            for app in apps
        ]
    )