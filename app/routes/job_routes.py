from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from core.auth import decode_token
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

@router.get("/")
def list_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=50),
    status: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(models.Job).filter(models.Job.user_id == user.id)

    if status:
        query = query.filter(models.Job.status == status)

    offset = (page - 1) * limit
    jobs = query.offset(offset).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "count": len(jobs),
        "jobs": jobs
    }
