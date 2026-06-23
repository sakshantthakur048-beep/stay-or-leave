"""
Lightweight request validation. Each view declares the fields it
needs; validate_json() checks presence, type, and basic constraints
before the view body runs, so handlers don't repeat boilerplate.
"""

import re
from functools import wraps

from flask import request, jsonify

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def is_valid_email(value: str) -> bool:
    return bool(value) and bool(EMAIL_RE.match(value.strip()))


def is_valid_password(value: str) -> bool:
    """At least 8 chars, one letter and one number — kept simple and explainable."""
    if not value or len(value) < 8:
        return False
    return bool(re.search(r"[A-Za-z]", value)) and bool(re.search(r"\d", value))


def validate_json(required_fields=None, optional_fields=None):
    """
    Decorator: ensures the request has a JSON body containing every
    key in required_fields (non-empty), and rejects unknown keys
    outside required_fields + optional_fields.
    """
    required_fields = required_fields or []
    optional_fields = optional_fields or []
    allowed = set(required_fields) | set(optional_fields)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({"error": "Request body must be valid JSON"}), 400

            missing = [f for f in required_fields if not str(data.get(f, "")).strip()]
            if missing:
                return jsonify({
                    "error": "Missing required fields",
                    "fields": missing,
                }), 400

            if allowed:
                unknown = [k for k in data.keys() if k not in allowed]
                if unknown:
                    return jsonify({
                        "error": "Unexpected fields in request",
                        "fields": unknown,
                    }), 400

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def sanitize_text(value: str, max_length: int = None) -> str:
    """Strip control characters and trim whitespace; truncate if needed."""
    if value is None:
        return ""
    cleaned = "".join(ch for ch in value if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    cleaned = cleaned.strip()
    if max_length:
        cleaned = cleaned[:max_length]
    return cleaned
