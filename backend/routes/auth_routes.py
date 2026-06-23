from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    get_jwt,
)

from backend.extensions import limiter
from backend.middleware.validation_middleware import validate_json
from backend.controllers.auth_controller import (
    AuthError,
    register_user,
    login_user,
    request_password_reset,
    reset_password,
    verify_email,
)
from backend.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per hour")
@validate_json(required_fields=["name", "email", "password"])
def register():
    data = request.get_json()
    try:
        result = register_user(data["name"], data["email"], data["password"])
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code
    return jsonify({
        "message": "Account created. Check your email to verify your account.",
        "user": result["user"],
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("20 per hour")
@validate_json(required_fields=["email", "password"])
def login():
    data = request.get_json()
    try:
        result = login_user(data["email"], data["password"])
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code
    return jsonify(result), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims = get_jwt()
    new_access_token = create_access_token(identity=identity, additional_claims={"role": claims.get("role")})
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    # Stateless JWT — logout is handled client-side by discarding the token.
    # If a denylist is needed later, add the token's jti to a blocklist store here.
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per hour")
@validate_json(required_fields=["email"])
def forgot_password():
    data = request.get_json()
    request_password_reset(data["email"])
    # Same response regardless of whether the email exists, to avoid account enumeration.
    return jsonify({
        "message": "If an account with that email exists, a reset link has been sent."
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("10 per hour")
@validate_json(required_fields=["token", "new_password"])
def do_reset_password():
    data = request.get_json()
    try:
        reset_password(data["token"], data["new_password"])
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code
    return jsonify({"message": "Password updated. You can now log in."}), 200


@auth_bp.route("/verify-email", methods=["POST"])
def do_verify_email():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or request.args.get("token")
    if not token:
        return jsonify({"error": "Verification token is required"}), 400
    try:
        verify_email(token)
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code
    return jsonify({"message": "Email verified successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200
