from typing import List
from .factors import FactorResult, Signal

def make_decision(
    projected: float,
    market: float,
    factors: List[FactorResult],
    min_edge: float = 4.5,
    min_strong_factors: int = 3
) -> dict:

    edge = projected - market
    abs_edge = abs(edge)

    strong_over = [f for f in factors if f.signal == Signal.OVER and f.strength >= 0.5]
    strong_under = [f for f in factors if f.signal == Signal.UNDER and f.strength >= 0.5]

    if edge >= min_edge and len(strong_over) >= min_strong_factors:
        side = "OVER"
        agreeing = strong_over
    elif edge <= -min_edge and len(strong_under) >= min_strong_factors:
        side = "UNDER"
        agreeing = strong_under
    else:
        return {
            "decision": "NO BET",
            "confidence": 0,
            "edge": round(edge, 1),
            "reason": "Mixed signals or edge too small"
        }

    # ========== IMPROVED CONFIDENCE CALCULATION ==========

    # 1. Edge score (more generous)
    if abs_edge >= 12:
        edge_score = 1.0
    elif abs_edge >= 8:
        edge_score = 0.85
    elif abs_edge >= 6:
        edge_score = 0.70
    else:
        edge_score = 0.55

    # 2. Factor score
    num_agreeing = len(agreeing)
    avg_strength = sum(f.strength for f in agreeing) / num_agreeing
    total_weight = sum(f.weight * f.strength for f in agreeing)

    factor_score = min((num_agreeing / 6) * 0.6 + (avg_strength * 0.4), 1.0)

    # 3. Final confidence
    raw_confidence = (edge_score * 0.45) + (factor_score * 0.55)
    confidence = int(raw_confidence * 100)

    # Small boost for very strong factor agreement
    if num_agreeing >= 5 and avg_strength >= 0.7:
        confidence = min(confidence + 6, 96)

    if confidence < 80:
        return {
            "decision": "NO BET",
            "confidence": confidence,
            "edge": round(edge, 1),
            "reason": "Confidence below 80"
        }

    tier = (
        "Extremely Strong" if confidence >= 90 else
        "Strong" if confidence >= 85 else
        "Good"
    )

    return {
        "decision": side,
        "confidence": confidence,
        "tier": tier,
        "edge": round(edge, 1),
        "projected": projected,
        "market": market,
        "agreeing_factors": [f.name for f in agreeing],
        "reason": f"{num_agreeing} strong factors | {abs_edge:.1f} pt edge"
    }