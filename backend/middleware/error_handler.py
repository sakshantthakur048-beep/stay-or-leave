"""
Centralized error handling so every endpoint returns a consistent
JSON error shape: { "error": "message" }.
"""

import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.extensions import db

logger = logging.getLogger("stay_or_leave")


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "You don't have permission to do this"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "Uploaded file is too large"}), 413

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Too many requests — please slow down"}), 429

    @app.errorhandler(IntegrityError)
    def integrity_error(e):
        db.session.rollback()
        logger.warning("IntegrityError: %s", e)
        return jsonify({"error": "This record already exists or violates a constraint"}), 409

    @app.errorhandler(SQLAlchemyError)
    def db_error(e):
        db.session.rollback()
        logger.error("Database error: %s", e)
        return jsonify({"error": "A database error occurred"}), 500

    @app.errorhandler(HTTPException)
    def http_exception(e):
        return jsonify({"error": e.description or "An error occurred"}), e.code

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        db.session.rollback()
        logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error"}), 500
