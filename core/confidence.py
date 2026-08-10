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

    # Calculate confidence
    total_weight = sum(f.weight * f.strength for f in agreeing)
    max_weight = sum(f.weight for f in factors) or 1
    factor_score = total_weight / max_weight
    edge_score = min(abs_edge / 9.0, 1.0)

    raw_confidence = (edge_score * 0.40) + (factor_score * 0.60)
    confidence = int(raw_confidence * 100)

    if confidence < 80:
        return {
            "decision": "NO BET",
            "confidence": confidence,
            "edge": round(edge, 1),
            "reason": "Confidence below 80"
        }

    tier = "Extremely Strong" if confidence >= 90 else "Strong" if confidence >= 85 else "Good"

    return {
        "decision": side,
        "confidence": confidence,
        "tier": tier,
        "edge": round(edge, 1),
        "projected": projected,
        "market": market,
        "agreeing_factors": [f.name for f in agreeing],
        "reason": f"{len(agreeing)} strong factors | {abs_edge:.1f} pt edge"
    }