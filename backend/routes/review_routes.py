import os
import uuid

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename

from backend.extensions import db, limiter
from backend.models import Review, ReviewImage, Comment, Like, Report, Place
from backend.middleware.validation_middleware import validate_json, sanitize_text

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")


def _current_user_id_optional():
    """Best-effort: returns user id if a valid JWT is present, else None."""
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        return get_jwt_identity()
    except Exception:
        return None


@reviews_bp.route("", methods=["GET"])
def list_reviews():
    query = Review.query.filter_by(status="published")

    place_id = request.args.get("place_id")
    if place_id:
        query = query.filter_by(place_id=place_id)

    place_slug = request.args.get("place_slug")
    if place_slug:
        place = Place.query.filter_by(slug=place_slug).first()
        if not place:
            return jsonify({"reviews": [], "page": 1, "total": 0, "total_pages": 0}), 200
        query = query.filter_by(place_id=place.id)

    sort = request.args.get("sort", "newest")
    if sort == "highest_rated":
        query = query.order_by(Review.rating.desc(), Review.created_at.desc())
    elif sort == "most_helpful":
        query = query.order_by(Review.helpful_count.desc(), Review.created_at.desc())
    else:
        query = query.order_by(Review.created_at.desc())

    search = request.args.get("search")
    if search:
        query = query.filter(Review.body.ilike(f"%{search.strip()}%"))

    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 10)), 1), 50)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    viewer_id = _current_user_id_optional()

    return jsonify({
        "reviews": [r.to_dict(viewer_id=viewer_id) for r in pagination.items],
        "page": page,
        "total": pagination.total,
        "total_pages": pagination.pages,
    }), 200


@reviews_bp.route("", methods=["POST"])
@jwt_required()
@validate_json(required_fields=["place_id", "title", "body", "rating"])
def create_review():
    data = request.get_json()
    user_id = get_jwt_identity()

    place = Place.query.get(data["place_id"])
    if not place:
        return jsonify({"error": "Place not found"}), 404

    try:
        rating = int(data["rating"])
    except (TypeError, ValueError):
        return jsonify({"error": "Rating must be a number between 1 and 5"}), 400
    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    title = sanitize_text(data["title"], max_length=150)
    body = sanitize_text(data["body"], max_length=5000)
    if len(title) < 3 or len(body) < 10:
        return jsonify({"error": "Title and review body must be more descriptive"}), 400

    review = Review(user_id=user_id, place_id=place.id, title=title, body=body, rating=rating)
    db.session.add(review)
    db.session.commit()

    return jsonify({"review": review.to_dict(viewer_id=user_id)}), 201


@reviews_bp.route("/<review_id>", methods=["PUT"])
@jwt_required()
def update_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    if review.user_id != user_id:
        return jsonify({"error": "You can only edit your own reviews"}), 403

    data = request.get_json(silent=True) or {}
    if "title" in data:
        review.title = sanitize_text(data["title"], max_length=150)
    if "body" in data:
        review.body = sanitize_text(data["body"], max_length=5000)
    if "rating" in data:
        try:
            rating = int(data["rating"])
        except (TypeError, ValueError):
            return jsonify({"error": "Rating must be a number between 1 and 5"}), 400
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400
        review.rating = rating

    db.session.commit()
    return jsonify({"review": review.to_dict(viewer_id=user_id)}), 200


@reviews_bp.route("/<review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    if review.user_id != user_id and claims.get("role") != "admin":
        return jsonify({"error": "You can only delete your own reviews"}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"}), 200


@reviews_bp.route("/<review_id>/images", methods=["POST"])
@jwt_required()
def upload_review_image(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    if review.user_id != user_id:
        return jsonify({"error": "You can only add images to your own reviews"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return jsonify({"error": "Only image files (png, jpg, jpeg, gif, webp) are allowed"}), 400

    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "reviews")
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, unique_name))

    image = ReviewImage(review_id=review.id, image_url=f"/uploads/reviews/{unique_name}")
    db.session.add(image)
    db.session.commit()

    return jsonify({"image_url": image.image_url}), 201


@reviews_bp.route("/<review_id>/like", methods=["POST"])
@jwt_required()
def like_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    existing = Like.query.filter_by(user_id=user_id, target_type="review", target_id=review_id).first()
    if existing:
        db.session.delete(existing)
        review.helpful_count = max(review.helpful_count - 1, 0)
        db.session.commit()
        return jsonify({"liked": False, "helpful_count": review.helpful_count}), 200

    db.session.add(Like(user_id=user_id, target_type="review", target_id=review_id))
    review.helpful_count += 1
    db.session.commit()
    return jsonify({"liked": True, "helpful_count": review.helpful_count}), 201


@reviews_bp.route("/<review_id>/comments", methods=["GET"])
def list_comments(review_id):
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404
    comments = review.comments.filter_by(status="published").order_by(Comment.created_at.asc()).all()
    return jsonify({"comments": [c.to_dict() for c in comments]}), 200


@reviews_bp.route("/<review_id>/comments", methods=["POST"])
@jwt_required()
@limiter.limit("30 per hour")
@validate_json(required_fields=["body"])
def add_comment(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    data = request.get_json()
    body = sanitize_text(data["body"], max_length=1000)
    if len(body) < 1:
        return jsonify({"error": "Comment cannot be empty"}), 400

    comment = Comment(review_id=review_id, user_id=user_id, body=body)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"comment": comment.to_dict()}), 201


@reviews_bp.route("/<review_id>/report", methods=["POST"])
@jwt_required()
@validate_json(required_fields=["reason"])
def report_review(review_id):
    user_id = get_jwt_identity()
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    data = request.get_json()
    reason = sanitize_text(data["reason"], max_length=255)
    report = Report(reporter_id=user_id, target_type="review", target_id=review_id, reason=reason)
    db.session.add(report)

    # auto-flag after 3 reports so it surfaces for moderation
    pending_count = Report.query.filter_by(target_type="review", target_id=review_id, status="pending").count()
    if pending_count + 1 >= 3 and review.status == "published":
        review.status = "flagged"

    db.session.commit()
    return jsonify({"message": "Report submitted. Thank you for helping keep the community safe."}), 201
