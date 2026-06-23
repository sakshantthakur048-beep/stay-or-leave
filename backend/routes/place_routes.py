from flask import Blueprint, request, jsonify

from backend.models import Place, PLACE_TYPES

places_bp = Blueprint("places", __name__, url_prefix="/api/places")


@places_bp.route("", methods=["GET"])
def list_places():
    query = Place.query

    place_type = request.args.get("type")
    if place_type:
        if place_type not in PLACE_TYPES:
            return jsonify({"error": f"type must be one of {list(PLACE_TYPES)}"}), 400
        query = query.filter_by(type=place_type)

    search = request.args.get("search")
    if search:
        query = query.filter(Place.name.ilike(f"%{search.strip()}%"))

    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)

    pagination = query.order_by(Place.name.asc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "places": [p.to_dict() for p in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "total_pages": pagination.pages,
    }), 200


@places_bp.route("/<slug>", methods=["GET"])
def get_place(slug):
    place = Place.query.filter_by(slug=slug).first()
    if not place:
        return jsonify({"error": "Place not found"}), 404
    return jsonify({"place": place.to_dict(with_metrics=True)}), 200
