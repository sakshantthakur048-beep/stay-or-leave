"""
Authentication & authorization middleware.

`@jwt_required()` from flask_jwt_extended handles "is this request
authenticated at all". The decorators here add role checks on top.
"""

from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

from backend.models import User


def admin_required(fn):
    """Require a valid JWT AND that the user's role is 'admin'."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def load_current_user():
    """Helper for routes that want the full User object, not just the JWT claims."""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


def owner_or_admin_required(get_owner_id):
    """
    Decorator factory: require the caller to either own the resource
    or be an admin. `get_owner_id(*args, **kwargs)` should return the
    resource's owner user_id given the view's own arguments.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            current_id = get_jwt_identity()
            owner_id = get_owner_id(*args, **kwargs)
            if current_id != owner_id and claims.get("role") != "admin":
                return jsonify({"error": "You don't have permission to do this"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
