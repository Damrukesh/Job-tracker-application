from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = "super-secret-key"

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from .routes import auth_routes
    app.register_blueprint(auth_routes)

    return app