from fastapi import FastAPI
from database import engine
import models
from routes import auth_routes, job_routes

models.Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(auth_routes.router)
app.include_router(job_routes.router)
