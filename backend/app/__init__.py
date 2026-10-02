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

    # Marca `users.last_seen_at` en cada petición autenticada que resuelve
    # bien, con throttle (ADR-020-content-filters-and-privacy-preferences.md).
    # Se registra acá y no en cada route para que ningún endpoint nuevo se
    # olvide de hacerlo.
    from app.interfaces.activity_tracker import register_activity_tracker
    register_activity_tracker(app)

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

    from app.interfaces.routes.privacy_routes import privacy_bp
    app.register_blueprint(privacy_bp, url_prefix="/api")

    from app.interfaces.routes.security_routes import security_bp
    app.register_blueprint(security_bp, url_prefix="/api")

    from app.interfaces.routes.data_export_routes import data_exports_bp
    app.register_blueprint(data_exports_bp, url_prefix="/api")

    from app.interfaces.routes.restriction_routes import restrictions_bp
    app.register_blueprint(restrictions_bp, url_prefix="/api")

    from app.interfaces.routes.content_routes import content_bp
    app.register_blueprint(content_bp, url_prefix="/api")

    return app