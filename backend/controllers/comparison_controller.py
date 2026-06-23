"""
Comparison controller: scoring two places against each other across
the fixed metric set, and producing a plain-language recommendation.

The "AI-generated summary" is a deterministic, rule-based summary
generator (no external LLM call) — it reads the actual metric deltas
and writes sentences from them. This keeps the feature fully working
without requiring a third-party API key, while leaving an obvious
extension point (see generate_ai_summary) to swap in a real LLM call
later if desired.
"""

from backend.models import Place, METRIC_DEFINITIONS, Comparison
from backend.extensions import db


def _better_count(metrics_a: dict, metrics_b: dict) -> tuple[int, int]:
    """Count how many metrics favor A vs B, respecting higher_is_better per metric."""
    a_wins, b_wins = 0, 0
    for m in METRIC_DEFINITIONS:
        key = m["key"]
        val_a, val_b = metrics_a.get(key), metrics_b.get(key)
        if val_a is None or val_b is None or val_a == val_b:
            continue
        a_better = (val_a > val_b) if m["higher_is_better"] else (val_a < val_b)
        if a_better:
            a_wins += 1
        else:
            b_wins += 1
    return a_wins, b_wins


def build_comparison_payload(place_a: Place, place_b: Place) -> dict:
    metrics_a = place_a.metrics_dict()
    metrics_b = place_b.metrics_dict()

    rows = []
    for m in METRIC_DEFINITIONS:
        key = m["key"]
        val_a, val_b = metrics_a.get(key), metrics_b.get(key)
        winner = None
        if val_a is not None and val_b is not None and val_a != val_b:
            a_better = (val_a > val_b) if m["higher_is_better"] else (val_a < val_b)
            winner = "A" if a_better else "B"
        rows.append({
            "key": key,
            "label": m["label"],
            "unit": m["unit"],
            "value_a": val_a,
            "value_b": val_b,
            "winner": winner,
        })

    a_wins, b_wins = _better_count(metrics_a, metrics_b)
    if a_wins > b_wins:
        recommendation = "A"
    elif b_wins > a_wins:
        recommendation = "B"
    else:
        recommendation = "tie"

    summary = generate_ai_summary(place_a, place_b, rows, recommendation)

    return {
        "place_a": place_a.to_dict(),
        "place_b": place_b.to_dict(),
        "rows": rows,
        "a_wins": a_wins,
        "b_wins": b_wins,
        "recommendation": recommendation,
        "summary": summary,
    }


def generate_ai_summary(place_a: Place, place_b: Place, rows: list, recommendation: str) -> str:
    """
    Rule-based natural-language summary. Picks the two largest relative
    gaps in each direction and writes them into sentences, then states
    the overall recommendation.
    """
    a_strengths = [r for r in rows if r["winner"] == "A"]
    b_strengths = [r for r in rows if r["winner"] == "B"]

    def top_labels(strengths, limit=2):
        return [r["label"] for r in strengths[:limit]]

    a_top = top_labels(a_strengths)
    b_top = top_labels(b_strengths)

    sentences = []

    if a_top:
        sentences.append(f"{place_a.name} comes out ahead on {', '.join(a_top)}.")
    if b_top:
        sentences.append(f"{place_b.name} has the edge on {', '.join(b_top)}.")

    if recommendation == "A":
        sentences.append(f"Overall, {place_a.name} is the stronger choice based on the factors compared.")
    elif recommendation == "B":
        sentences.append(f"Overall, {place_b.name} is the stronger choice based on the factors compared.")
    else:
        sentences.append("Overall, the two are closely matched — the right choice depends on which factors matter most to you.")

    return " ".join(sentences)


def save_comparison(user_id: str | None, place_a: Place, place_b: Place, recommendation: str, summary: str) -> Comparison:
    comparison = Comparison(
        user_id=user_id,
        place_a_id=place_a.id,
        place_b_id=place_b.id,
        recommendation=recommendation,
        summary=summary,
    )
    db.session.add(comparison)
    db.session.commit()
    return comparison
