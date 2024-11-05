import os
import secrets

from cryptography.fernet import Fernet
from flask import Flask

from app.extensions import db, migrate, login_manager, bootstrap, csrf, jwt
from app.models import User, ExpiredToken
from app.routes import api_bp, login_bp, jwt_bp
from app.cli import create_user
from dotenv import load_dotenv, set_key
from datetime import timedelta

load_dotenv('.env')

def create_app():
    app = Flask(__name__)

    # check for the existence of the APP_SECRET and JWT_SECRET environment variables
    if os.getenv('APP_SECRET') is None or os.getenv('JWT_SECRET') is None:
        print('APP_SECRET environment variable is not set, setting one now')
        set_key('.env', 'APP_SECRET', secrets.token_urlsafe(64))
        set_key('.env', 'JWT_SECRET', secrets.token_urlsafe(64))
    else:
        print('APP_SECRET environment variable is set, using existing value')
        app.secret_key = os.getenv('APP_SECRET')
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')

    # configure JWT options
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # Shorter access token expiration
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Longer refresh token expiration

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    jwt.init_app(app)

    # exempt routes from CSRF protection
    csrf.exempt(api_bp)
    csrf.exempt(jwt_bp)

    # add a check to see if a user's JWT token has been revoked
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        # Query the database to check if the token is revoked
        token = ExpiredToken.query.filter_by(jti=jti).first()
        return token is not None  # Return True if token is found (revoked)

    # Initialize encryption key
    encryption_key = os.getenv('ENCRYPTION_KEY')
    if not encryption_key:
        # Generate a new key and save it if not present
        encryption_key = Fernet.generate_key().decode()
        fernet = Fernet(encryption_key)
        set_key('.env', 'ENCRYPTION_KEY', encryption_key)
        app.config['FERNET'] = fernet
        raise ValueError("No ENCRYPTION_KEY set for Flask application on first run, set a key in the .env file")
    else:
        fernet = Fernet(encryption_key)

    app.config['FERNET'] = fernet

    login_manager.login_view = 'login.login'
    login_manager.login_message = 'Please log in to access this page.'

    # register blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(jwt_bp)
    app.register_blueprint(api_bp)

    app.cli.add_command(create_user)

    with app.app_context():
        db.create_all()

    return app
