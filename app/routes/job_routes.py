from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
from core.auth import decode_token, require_admin
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/jobs")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    user = db.query(models.User).filter(models.User.id == payload["id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# USER: create job
@router.post("/")
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    j = models.Job(**job.dict(), user_id=user.id)
    db.add(j)
    db.commit()
    return {"status": "job added"}

# USER: view own jobs
@router.get("/")
def list_my_jobs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Job).filter(models.Job.user_id == user.id).all()

# ADMIN: view all jobs
@router.get("/admin/all")
def list_all_jobs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_admin(user)
    return db.query(models.Job).all()

# ADMIN: delete any job
@router.delete("/admin/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_admin(user)
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"status": "job deleted"}
