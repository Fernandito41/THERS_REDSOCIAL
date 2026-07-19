from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import jwt


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    jwt.init_app(app)

    from app.interfaces.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api")

    return app