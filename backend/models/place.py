import re
import uuid
from datetime import datetime

from backend.extensions import db

PLACE_TYPES = ("country", "city", "company", "college")

# The fixed set of comparable factors the comparison page understands.
# Keys map 1:1 to place_metrics.metric_key rows.
METRIC_DEFINITIONS = [
    {"key": "cost_of_living",   "label": "Cost of Living",     "unit": "index_0_100", "higher_is_better": False},
    {"key": "avg_salary",       "label": "Average Salary",     "unit": "USD",          "higher_is_better": True},
    {"key": "tax_rate",         "label": "Tax Rate",           "unit": "percent",      "higher_is_better": False},
    {"key": "safety_index",     "label": "Safety",             "unit": "index_0_100", "higher_is_better": True},
    {"key": "healthcare_index", "label": "Healthcare",         "unit": "index_0_100", "higher_is_better": True},
    {"key": "internet_speed",   "label": "Internet Speed",     "unit": "mbps",         "higher_is_better": True},
    {"key": "happiness_index",  "label": "Happiness Index",    "unit": "index_0_10",  "higher_is_better": True},
    {"key": "pollution_index",  "label": "Pollution",          "unit": "index_0_100", "higher_is_better": False},
    {"key": "gdp_per_capita",   "label": "GDP per Capita",     "unit": "USD",          "higher_is_better": True},
]


def slugify(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # country | city | company | college
    slug = db.Column(db.String(170), nullable=False, unique=True, index=True)
    country_code = db.Column(db.String(2))
    image_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    metrics = db.relationship("PlaceMetric", backref="place", lazy="dynamic", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="place", lazy="dynamic", cascade="all, delete-orphan")

    def metrics_dict(self) -> dict:
        return {m.metric_key: float(m.value) if m.value is not None else None for m in self.metrics}

    def to_dict(self, with_metrics: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "slug": self.slug,
            "country_code": self.country_code,
            "image_url": self.image_url,
            "description": self.description,
        }
        if with_metrics:
            data["metrics"] = self.metrics_dict()
        return data


class PlaceMetric(db.Model):
    __tablename__ = "place_metrics"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id = db.Column(db.String(36), db.ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_key = db.Column(db.String(50), nullable=False, index=True)
    value = db.Column(db.Numeric(12, 2))
    unit = db.Column(db.String(20))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("place_id", "metric_key", name="uq_place_metric"),)
