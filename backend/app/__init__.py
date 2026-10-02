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

    # Almacenamiento de imágenes de perfil (ADR-015-profile-media.md).
    from app.application.media.media_url import configure_media_url
    from app.infrastructure.media.factory import build_media_storage

    app.extensions["media_storage"] = build_media_storage(app.config)
    configure_media_url(app.config["MEDIA_PUBLIC_BASE_URL"])

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

    from app.interfaces.routes.like_routes import likes_bp
    app.register_blueprint(likes_bp, url_prefix="/api")

    from app.interfaces.routes.comment_routes import comments_bp
    app.register_blueprint(comments_bp, url_prefix="/api")

    from app.interfaces.routes.follow_routes import follows_bp
    app.register_blueprint(follows_bp, url_prefix="/api")

    from app.interfaces.routes.notification_routes import notifications_bp
    app.register_blueprint(notifications_bp, url_prefix="/api")

    from app.interfaces.routes.message_routes import messages_bp
    app.register_blueprint(messages_bp, url_prefix="/api")

    # Servir imágenes desde disco solo con STORAGE_BACKEND=local (en s3 las
    # sirve el proveedor directamente desde su URL pública).
    if (app.config.get("STORAGE_BACKEND") or "local").lower() == "local":
        from app.interfaces.routes.media_routes import media_bp
        app.register_blueprint(media_bp, url_prefix="/api")

    return app