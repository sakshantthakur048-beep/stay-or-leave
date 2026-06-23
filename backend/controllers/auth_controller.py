"""
Auth controller: the actual business logic behind register/login/
password-reset/email-verify. Routes stay thin and call into here.
"""

import logging

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token

from backend.extensions import db
from backend.models import User, AuthToken
from backend.middleware.validation_middleware import is_valid_email, is_valid_password

logger = logging.getLogger("stay_or_leave")


class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_user(name: str, email: str, password: str) -> dict:
    name = name.strip()
    email = email.strip().lower()

    if not is_valid_email(email):
        raise AuthError("Enter a valid email address")
    if not is_valid_password(password):
        raise AuthError("Password must be at least 8 characters and include a letter and a number")
    if len(name) < 2:
        raise AuthError("Name must be at least 2 characters")

    if User.query.filter_by(email=email).first():
        raise AuthError("An account with this email already exists", 409)

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # get user.id before creating the token

    verify_token = AuthToken.generate(user.id, "email_verify", ttl_minutes=60 * 24)
    db.session.commit()

    # In production this sends a real email via Flask-Mail. Logged here instead.
    logger.info("Email verification link for %s: /verify-email?token=%s", email, verify_token.token)

    return {"user": user.to_dict(), "verification_token": verify_token.token}


def login_user(email: str, password: str) -> dict:
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        raise AuthError("Invalid email or password", 401)

    if not user.is_active:
        raise AuthError("This account has been deactivated", 403)

    claims = {"role": user.role}
    access_token = create_access_token(identity=user.id, additional_claims=claims)
    refresh_token = create_refresh_token(identity=user.id, additional_claims=claims)

    return {
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def request_password_reset(email: str) -> str | None:
    """Returns the raw token (for dev/logging) or None if no such user — caller should
    respond identically either way to avoid leaking which emails are registered."""
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return None

    reset_token = AuthToken.generate(user.id, "password_reset", ttl_minutes=30)
    db.session.commit()
    logger.info("Password reset link for %s: /reset-password?token=%s", email, reset_token.token)
    return reset_token.token


def reset_password(token: str, new_password: str) -> None:
    if not is_valid_password(new_password):
        raise AuthError("Password must be at least 8 characters and include a letter and a number")

    record = AuthToken.query.filter_by(token=token, token_type="password_reset").first()
    if not record or not record.is_valid:
        raise AuthError("This reset link is invalid or has expired", 400)

    user = User.query.get(record.user_id)
    if not user:
        raise AuthError("User not found", 404)

    user.set_password(new_password)
    record.mark_used()
    db.session.commit()


def verify_email(token: str) -> None:
    record = AuthToken.query.filter_by(token=token, token_type="email_verify").first()
    if not record or not record.is_valid:
        raise AuthError("This verification link is invalid or has expired", 400)

    user = User.query.get(record.user_id)
    if not user:
        raise AuthError("User not found", 404)

    user.is_verified = True
    record.mark_used()
    db.session.commit()
