from app.extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone

# user model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')

    def __repr__(self):
        return f'<User {self.username}>'

# expired/blacklisted jwt token model
class ExpiredToken(db.Model):
    __tablename__ = 'expired_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<ExpiredToken jti={self.jti}>'