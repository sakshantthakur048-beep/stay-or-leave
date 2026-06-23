"""
One-off helper to create all tables via SQLAlchemy models (alternative
to running schema.sql directly with psql). Useful for quick local setup.

Usage:
    cd backend
    python database/init_db.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app import create_app
from backend.extensions import db
from backend import models  # noqa: F401  -- registers models with SQLAlchemy


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("All tables created successfully.")


if __name__ == "__main__":
    main()
