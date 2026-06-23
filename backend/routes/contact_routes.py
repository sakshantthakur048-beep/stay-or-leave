from flask import Blueprint, request, jsonify

from backend.extensions import db, limiter
from backend.models import ContactMessage
from backend.middleware.validation_middleware import validate_json, sanitize_text, is_valid_email

contact_bp = Blueprint("contact", __name__, url_prefix="/api/contact")


@contact_bp.route("", methods=["POST"])
@limiter.limit("10 per hour")
@validate_json(required_fields=["name", "email", "message"], optional_fields=["subject"])
def submit_contact_message():
    data = request.get_json()

    if not is_valid_email(data["email"]):
        return jsonify({"error": "Enter a valid email address"}), 400

    name = sanitize_text(data["name"], max_length=100)
    message = sanitize_text(data["message"], max_length=3000)
    subject = sanitize_text(data.get("subject", ""), max_length=200)

    if len(message) < 5:
        return jsonify({"error": "Message is too short"}), 400

    contact_message = ContactMessage(
        name=name, email=data["email"].strip().lower(), subject=subject or None, message=message
    )
    db.session.add(contact_message)
    db.session.commit()

    return jsonify({"message": "Thanks for reaching out — we'll get back to you soon."}), 201
