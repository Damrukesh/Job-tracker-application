from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas, auth
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    data = auth.decode_token(token)
    return db.query(models.User).filter(models.User.id == data["id"]).first()

@router.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed = auth.hash_password(user.password)
    db_user = models.User(email=user.email, password=hashed)
    db.add(db_user)
    db.commit()
    return {"message": "user created"}

@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(400, "Invalid credentials")
    token = auth.create_token({"id": db_user.id})
    return {"access_token": token}

@router.post("/jobs")
def add_job(job: schemas.JobCreate, db: Session = Depends(get_db), user=Depends(get_user)):
    j = models.Job(**job.dict(), user_id=user.id)
    db.add(j)
    db.commit()
    return {"status": "added"}

@router.get("/jobs")
def get_jobs(db: Session = Depends(get_db), user=Depends(get_user)):
    return db.query(models.Job).filter(models.Job.user_id == user.id).all()
