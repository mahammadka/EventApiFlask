from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Register Blueprints for modular app structure
    from .routes import main, auth_bp, event_bp
    app.register_blueprint(main)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(event_bp)

    return app