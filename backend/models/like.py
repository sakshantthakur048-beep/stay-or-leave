import uuid
from datetime import datetime

from backend.extensions import db


class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type = db.Column(db.String(20), nullable=False)  # 'review' | 'comment'
    target_id = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_like_target"),
    )
