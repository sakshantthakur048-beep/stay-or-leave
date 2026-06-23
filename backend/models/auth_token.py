import uuid
import secrets
from datetime import datetime, timedelta

from backend.extensions import db


class AuthToken(db.Model):
    __tablename__ = "auth_tokens"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    token_type = db.Column(db.String(30), nullable=False)  # 'email_verify' | 'password_reset'
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate(user_id: str, token_type: str, ttl_minutes: int = 60) -> "AuthToken":
        token = AuthToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            token_type=token_type,
            expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
        )
        db.session.add(token)
        return token

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at > datetime.utcnow()

    def mark_used(self) -> None:
        self.used_at = datetime.utcnow()
