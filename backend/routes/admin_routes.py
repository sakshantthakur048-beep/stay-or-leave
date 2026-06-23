from flask import Blueprint, request, jsonify

from backend.extensions import db
from backend.models import User, Review, Comment, Report, ContactMessage, Comparison, Place
from backend.middleware.auth_middleware import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def stats():
    return jsonify({
        "total_users": User.query.count(),
        "total_reviews": Review.query.count(),
        "total_comparisons": Comparison.query.count(),
        "total_places": Place.query.count(),
        "pending_reports": Report.query.filter_by(status="pending").count(),
        "unread_messages": ContactMessage.query.filter_by(is_read=False).count(),
        "flagged_reviews": Review.query.filter_by(status="flagged").count(),
    }), 200


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
    pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "users": [u.to_dict() for u in pagination.items],
        "page": page,
        "total": pagination.total,
        "total_pages": pagination.pages,
    }), 200


@admin_bp.route("/users/<user_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User deactivated"}), 200


@admin_bp.route("/users/<user_id>/reactivate", methods=["POST"])
@admin_required
def reactivate_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.is_active = True
    db.session.commit()
    return jsonify({"message": "User reactivated"}), 200


@admin_bp.route("/reviews", methods=["GET"])
@admin_required
def list_all_reviews():
    status = request.args.get("status")  # published | flagged | removed
    query = Review.query
    if status:
        query = query.filter_by(status=status)
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
    pagination = query.order_by(Review.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "reviews": [r.to_dict() for r in pagination.items],
        "page": page,
        "total": pagination.total,
        "total_pages": pagination.pages,
    }), 200


@admin_bp.route("/reviews/<review_id>/moderate", methods=["POST"])
@admin_required
def moderate_review(review_id):
    data = request.get_json(silent=True) or {}
    action = data.get("action")  # 'approve' | 'remove'
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    if action == "approve":
        review.status = "published"
    elif action == "remove":
        review.status = "removed"
    else:
        return jsonify({"error": "action must be 'approve' or 'remove'"}), 400

    db.session.commit()
    return jsonify({"review": review.to_dict()}), 200


@admin_bp.route("/reports", methods=["GET"])
@admin_required
def list_reports():
    status = request.args.get("status", "pending")
    reports = Report.query.filter_by(status=status).order_by(Report.created_at.desc()).all()
    return jsonify({"reports": [r.to_dict() for r in reports]}), 200


@admin_bp.route("/reports/<report_id>/resolve", methods=["POST"])
@admin_required
def resolve_report(report_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status", "reviewed")  # 'reviewed' | 'dismissed'
    if status not in ("reviewed", "dismissed"):
        return jsonify({"error": "status must be 'reviewed' or 'dismissed'"}), 400

    report = Report.query.get(report_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404

    report.status = status
    db.session.commit()
    return jsonify({"report": report.to_dict()}), 200


@admin_bp.route("/messages", methods=["GET"])
@admin_required
def list_contact_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify({"messages": [m.to_dict() for m in messages]}), 200


@admin_bp.route("/messages/<message_id>/read", methods=["POST"])
@admin_required
def mark_message_read(message_id):
    message = ContactMessage.query.get(message_id)
    if not message:
        return jsonify({"error": "Message not found"}), 404
    message.is_read = True
    db.session.commit()
    return jsonify({"message_record": message.to_dict()}), 200


@admin_bp.route("/comparisons/<comparison_id>/feature", methods=["POST"])
@admin_required
def feature_comparison(comparison_id):
    comparison = Comparison.query.get(comparison_id)
    if not comparison:
        return jsonify({"error": "Comparison not found"}), 404
    comparison.is_featured = not comparison.is_featured
    db.session.commit()
    return jsonify({"comparison": comparison.to_dict()}), 200


@admin_bp.route("/places", methods=["POST"])
@admin_required
def create_place():
    from backend.models import Place, slugify, PLACE_TYPES

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    place_type = data.get("type")

    if not name or place_type not in PLACE_TYPES:
        return jsonify({"error": f"name is required and type must be one of {list(PLACE_TYPES)}"}), 400

    slug = slugify(name)
    if Place.query.filter_by(slug=slug).first():
        return jsonify({"error": "A place with this name already exists"}), 409

    place = Place(
        name=name,
        type=place_type,
        slug=slug,
        country_code=data.get("country_code"),
        image_url=data.get("image_url"),
        description=data.get("description"),
    )
    db.session.add(place)
    db.session.commit()
    return jsonify({"place": place.to_dict()}), 201
