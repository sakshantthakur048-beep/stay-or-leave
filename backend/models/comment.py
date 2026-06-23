import uuid
from datetime import datetime

from backend.extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = db.Column(db.String(36), db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    body = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="published")  # published|flagged|removed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "review_id": self.review_id,
            "user_id": self.user_id,
            "author_name": self.author.name if self.author else "Unknown",
            "author_avatar": self.author.profile_picture if self.author else None,
            "body": self.body,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
