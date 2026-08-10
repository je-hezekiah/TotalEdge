import json
import os
from datetime import datetime
from typing import Optional

TRACKER_FILE = "data/predictions.json"

def _load_predictions():
    if not os.path.exists(TRACKER_FILE):
        return []
    with open(TRACKER_FILE, "r") as f:
        return json.load(f)

def _save_predictions(data):
    os.makedirs("data", exist_ok=True)
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_prediction(
    home_team: str,
    away_team: str,
    projected: float,
    market: float,
    decision: str,
    confidence: int,
    tier: str,
    edge: float,
    agreeing_factors: list,
    league: str = "NBA"
):
    """Save a new prediction."""
    if decision == "NO BET":
        return  # We don't log NO BETs

    predictions = _load_predictions()

    record = {
        "id": len(predictions) + 1,
        "timestamp": datetime.now().isoformat(),
        "league": league,
        "home_team": home_team,
        "away_team": away_team,
        "projected": projected,
        "market": market,
        "edge": edge,
        "decision": decision,          # OVER or UNDER
        "confidence": confidence,
        "tier": tier,
        "agreeing_factors": agreeing_factors,
        "result": None,                # Will be filled later
        "actual_total": None,
        "hit": None,                   # True / False
        "notes": ""
    }

    predictions.append(record)
    _save_predictions(predictions)
    print(f"Prediction logged (ID: {record['id']})")

def update_result(prediction_id: int, actual_total: float, notes: str = ""):
    """Update a prediction with the real result."""
    predictions = _load_predictions()

    for pred in predictions:
        if pred["id"] == prediction_id:
            pred["actual_total"] = actual_total
            pred["notes"] = notes

            if pred["decision"] == "OVER":
                pred["hit"] = actual_total > pred["market"]
            else:
                pred["hit"] = actual_total < pred["market"]

            pred["result"] = "WIN" if pred["hit"] else "LOSS"
            _save_predictions(predictions)
            print(f"Updated prediction {prediction_id} → {pred['result']}")
            return

    print("Prediction ID not found.")

def show_performance():
    """Show simple performance summary."""
    predictions = _load_predictions()
    finished = [p for p in predictions if p["result"] is not None]

    if not finished:
        print("No settled predictions yet.")
        return

    total = len(finished)
    wins = len([p for p in finished if p["hit"]])
    winrate = (wins / total) * 100

    print("\n=== TotalEdge Performance ===")
    print(f"Total settled picks : {total}")
    print(f"Wins                : {wins}")
    print(f"Winrate             : {winrate:.1f}%")

    # By tier
    for tier in ["Extremely Strong", "Strong", "Good"]:
        tier_picks = [p for p in finished if p["tier"] == tier]
        if tier_picks:
            tier_wins = len([p for p in tier_picks if p["hit"]])
            print(f"{tier:18} : {tier_wins}/{len(tier_picks)}")