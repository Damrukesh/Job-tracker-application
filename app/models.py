from datetime import datetime

from . import db
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role")

    # Recruiter -> their job postings
    job_posts = db.relationship(
        "JobPost",
        back_populates="recruiter",
        cascade="all, delete-orphan",
    )

    # Candidate -> their applications
    applications = db.relationship(
        "Application",
        back_populates="applicant",
        cascade="all, delete-orphan",
    )

class JobPost(db.Model):
    __tablename__ = 'job_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Link to the User who created the post (Recruiter)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    recruiter = db.relationship(
        "User",
        back_populates="job_posts",
        foreign_keys=[recruiter_id],
    )

    applications = db.relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan",
    )

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(100), nullable=False)
    resume_filename = db.Column(db.String(200), nullable=False) # Store the path/name, not the file
    match_score = db.Column(db.Float, default=0.0, nullable=False) # This is where our AI result goes
    
    # Link to the specific Job
    job_id = db.Column(db.Integer, db.ForeignKey('job_posts.id'), nullable=False)
    # Link to the User who applied (Candidate)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    job = db.relationship(
        "JobPost",
        back_populates="applications",
        foreign_keys=[job_id],
    )

    applicant = db.relationship(
        "User",
        back_populates="applications",
        foreign_keys=[user_id],
    )