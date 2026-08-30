from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import jwt, db, migrate


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.interfaces.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Registra los modelos en el metadata de SQLAlchemy para que Flask-Migrate
    # los detecte al autogenerar migraciones (flask db migrate).
    from app.infrastructure.persistence import models  # noqa: F401

    from app.interfaces.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api")

    from app.interfaces.routes.user_routes import users_bp
    app.register_blueprint(users_bp, url_prefix="/api")

    from app.interfaces.routes.post_routes import posts_bp
    app.register_blueprint(posts_bp, url_prefix="/api")

    return app