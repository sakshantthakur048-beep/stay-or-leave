"""
Application entry point. Run with: python app.py
(Or in production: gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()')
"""

import os
import logging

from flask import Flask, jsonify, send_from_directory

from backend.config.config import get_config
from backend.extensions import db, jwt, bcrypt, cors, limiter


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    logging.basicConfig(level=logging.INFO)

    # --- Extensions ---
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)
    limiter.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- Models (import so SQLAlchemy registers them) ---
    from backend import models  # noqa: F401

    # --- JWT error handlers (consistent JSON shape) ---
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Authentication required"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid or expired token"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    # --- Blueprints ---
    from backend.routes.auth_routes import auth_bp
    from backend.routes.user_routes import users_bp
    from backend.routes.place_routes import places_bp
    from backend.routes.comparison_routes import comparisons_bp
    from backend.routes.review_routes import reviews_bp
    from backend.routes.contact_routes import contact_bp
    from backend.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(places_bp)
    app.register_blueprint(comparisons_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)

    # --- Error handlers ---
    from backend.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    # --- Serve uploaded files ---
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=app.config.get("DEBUG", False))
