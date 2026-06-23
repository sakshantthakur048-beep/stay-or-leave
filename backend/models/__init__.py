"""
Importing this package registers every model with SQLAlchemy's metadata,
which is required before db.create_all() or Flask-Migrate can see them.
"""

from backend.models.user import User
from backend.models.auth_token import AuthToken
from backend.models.place import Place, PlaceMetric, METRIC_DEFINITIONS, PLACE_TYPES, slugify
from backend.models.comparison import Comparison, Bookmark
from backend.models.review import Review, ReviewImage
from backend.models.comment import Comment
from backend.models.like import Like
from backend.models.report import Report, ContactMessage

__all__ = [
    "User",
    "AuthToken",
    "Place",
    "PlaceMetric",
    "METRIC_DEFINITIONS",
    "PLACE_TYPES",
    "slugify",
    "Comparison",
    "Bookmark",
    "Review",
    "ReviewImage",
    "Comment",
    "Like",
    "Report",
    "ContactMessage",
]
