import uuid
from datetime import datetime

from backend.extensions import db


class Comparison(db.Model):
    __tablename__ = "comparisons"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), index=True)
    place_a_id = db.Column(db.String(36), db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    place_b_id = db.Column(db.String(36), db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    recommendation = db.Column(db.String(10))  # 'A' | 'B' | 'tie'
    summary = db.Column(db.Text)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    place_a = db.relationship("Place", foreign_keys=[place_a_id])
    place_b = db.relationship("Place", foreign_keys=[place_b_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "place_a": self.place_a.to_dict(with_metrics=True) if self.place_a else None,
            "place_b": self.place_b.to_dict(with_metrics=True) if self.place_b else None,
            "recommendation": self.recommendation,
            "summary": self.summary,
            "view_count": self.view_count,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    comparison_id = db.Column(db.String(36), db.ForeignKey("comparisons.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "comparison_id", name="uq_user_comparison_bookmark"),)
