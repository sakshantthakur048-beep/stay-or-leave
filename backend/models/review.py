import uuid
from datetime import datetime

from backend.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    place_id = db.Column(db.String(36), db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)  # 1-5
    status = db.Column(db.String(20), nullable=False, default="published", index=True)  # published|flagged|removed
    helpful_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    images = db.relationship("ReviewImage", backref="review", lazy="select", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="review", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, viewer_id: str = None) -> dict:
        from backend.models.like import Like  # local import avoids circular import

        liked = False
        if viewer_id:
            liked = Like.query.filter_by(
                user_id=viewer_id, target_type="review", target_id=self.id
            ).first() is not None

        return {
            "id": self.id,
            "user_id": self.user_id,
            "author_name": self.author.name if self.author else "Unknown",
            "author_avatar": self.author.profile_picture if self.author else None,
            "place_id": self.place_id,
            "place_name": self.place.name if self.place else None,
            "title": self.title,
            "body": self.body,
            "rating": self.rating,
            "status": self.status,
            "helpful_count": self.helpful_count,
            "comment_count": self.comments.count(),
            "images": [img.image_url for img in self.images],
            "liked_by_viewer": liked,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ReviewImage(db.Model):
    __tablename__ = "review_images"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = db.Column(db.String(36), db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
