import io

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db, limiter
from backend.models import Place, Comparison, Bookmark
from backend.controllers.comparison_controller import build_comparison_payload, save_comparison

comparisons_bp = Blueprint("comparisons", __name__, url_prefix="/api/comparisons")


def _get_place_or_404(identifier):
    """Accepts either a place id or a slug."""
    place = Place.query.get(identifier)
    if not place:
        place = Place.query.filter_by(slug=identifier).first()
    return place


@comparisons_bp.route("/compare", methods=["GET"])
@limiter.limit("60 per hour")
def compare():
    place_a_param = request.args.get("place_a")
    place_b_param = request.args.get("place_b")

    if not place_a_param or not place_b_param:
        return jsonify({"error": "place_a and place_b query parameters are required"}), 400

    place_a = _get_place_or_404(place_a_param)
    place_b = _get_place_or_404(place_b_param)

    if not place_a or not place_b:
        return jsonify({"error": "One or both places were not found"}), 404
    if place_a.id == place_b.id:
        return jsonify({"error": "Choose two different places to compare"}), 400

    payload = build_comparison_payload(place_a, place_b)
    return jsonify(payload), 200


@comparisons_bp.route("", methods=["POST"])
@jwt_required(optional=True)
def create_comparison():
    """Persist a comparison (e.g. so it can be bookmarked or appear in 'featured')."""
    data = request.get_json(silent=True) or {}
    place_a = _get_place_or_404(data.get("place_a", ""))
    place_b = _get_place_or_404(data.get("place_b", ""))

    if not place_a or not place_b:
        return jsonify({"error": "One or both places were not found"}), 404

    payload = build_comparison_payload(place_a, place_b)
    user_id = get_jwt_identity()  # None if not authenticated

    comparison = save_comparison(
        user_id, place_a, place_b, payload["recommendation"], payload["summary"]
    )
    return jsonify({"comparison": comparison.to_dict()}), 201


@comparisons_bp.route("/featured", methods=["GET"])
def featured():
    items = (
        Comparison.query.filter_by(is_featured=True)
        .order_by(Comparison.created_at.desc())
        .limit(6)
        .all()
    )
    return jsonify({"comparisons": [c.to_dict() for c in items]}), 200


@comparisons_bp.route("/<comparison_id>", methods=["GET"])
def get_comparison(comparison_id):
    comparison = Comparison.query.get(comparison_id)
    if not comparison:
        return jsonify({"error": "Comparison not found"}), 404
    comparison.view_count += 1
    db.session.commit()
    return jsonify({"comparison": comparison.to_dict()}), 200


@comparisons_bp.route("/<comparison_id>/bookmark", methods=["POST"])
@jwt_required()
def bookmark_comparison(comparison_id):
    user_id = get_jwt_identity()
    comparison = Comparison.query.get(comparison_id)
    if not comparison:
        return jsonify({"error": "Comparison not found"}), 404

    existing = Bookmark.query.filter_by(user_id=user_id, comparison_id=comparison_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"bookmarked": False}), 200

    db.session.add(Bookmark(user_id=user_id, comparison_id=comparison_id))
    db.session.commit()
    return jsonify({"bookmarked": True}), 201


@comparisons_bp.route("/bookmarks", methods=["GET"])
@jwt_required()
def list_bookmarks():
    user_id = get_jwt_identity()
    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    comparisons = [Comparison.query.get(b.comparison_id) for b in bookmarks]
    return jsonify({"comparisons": [c.to_dict() for c in comparisons if c]}), 200


@comparisons_bp.route("/export-pdf", methods=["GET"])
@limiter.limit("20 per hour")
def export_pdf():
    """Generate a simple PDF summary of a comparison for download."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    place_a_param = request.args.get("place_a")
    place_b_param = request.args.get("place_b")
    place_a = _get_place_or_404(place_a_param)
    place_b = _get_place_or_404(place_b_param)

    if not place_a or not place_b:
        return jsonify({"error": "One or both places were not found"}), 404

    payload = build_comparison_payload(place_a, place_b)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, f"{place_a.name} vs {place_b.name}")

    c.setFont("Helvetica", 11)
    y = height - 100
    for row in payload["rows"]:
        line = f"{row['label']}: {row['value_a']} vs {row['value_b']} ({row['unit']})"
        c.drawString(50, y, line)
        y -= 20
        if y < 80:
            c.showPage()
            y = height - 60

    c.setFont("Helvetica-Bold", 12)
    y -= 10
    c.drawString(50, y, "Summary:")
    y -= 20
    c.setFont("Helvetica", 11)

    # naive word-wrap for the summary paragraph
    words = payload["summary"].split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > 90:
            c.drawString(50, y, line)
            y -= 18
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        c.drawString(50, y, line)

    c.save()
    buffer.seek(0)

    filename = f"{place_a.slug}-vs-{place_b.slug}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)
