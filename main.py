from fastapi import FastAPI
from database import engine
import models
from routes import router
from dotenv import load_dotenv
load_dotenv()


models.Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(router)
