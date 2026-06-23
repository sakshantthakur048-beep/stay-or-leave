import os
import uuid

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from backend.extensions import db
from backend.models import User
from backend.middleware.validation_middleware import validate_json, sanitize_text

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


def _allowed_image(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
@validate_json(optional_fields=["name"])
def update_profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if "name" in data:
        name = sanitize_text(data["name"], max_length=100)
        if len(name) < 2:
            return jsonify({"error": "Name must be at least 2 characters"}), 400
        user.name = name

    db.session.commit()
    return jsonify({"user": user.to_dict()}), 200


@users_bp.route("/me/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_image(file.filename):
        return jsonify({"error": "Only image files (png, jpg, jpeg, gif, webp) are allowed"}), 400

    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, unique_name)
    file.save(filepath)

    user.profile_picture = f"/uploads/avatars/{unique_name}"
    db.session.commit()

    return jsonify({"user": user.to_dict()}), 200


@users_bp.route("/<user_id>", methods=["GET"])
def get_public_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict(include_email=False)}), 200
