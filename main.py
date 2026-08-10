from core.projection import project_total
from core.factors import (
    score_pace, score_recent_scoring, score_offense, score_defense,
    score_rest, score_home_away, score_injuries, score_matchup
)
from core.confidence import make_decision

def run_test():
    print("=== TotalEdge Test ===\n")

    projected = project_total(
        team_a_pace=107.5,
        team_b_pace=106.2,
        team_a_ortg=122.5,
        team_b_ortg=120.8,
        team_a_drtg=111.5,
        team_b_drtg=112.0,
        is_team_a_home=True,
        injury_adjustment=7.0,
        rest_adjustment=2.5
    )

    market_total = 219.5

    factors = [
        score_pace(107.5, 106.2, 100.0),
        score_recent_scoring(126, 122, 114, 112),
        score_offense(122.5, 120.8, 113.0),
        score_defense(111.5, 112.0, 113.5),
        score_rest(3, 3, False, False),
        score_home_away(124, 114, 119, 110, True),
        score_injuries(2, 7.0),
        score_matchup(238.0, 224.0, "fast")
    ]

    # Temporarily lower min_edge for testing
    result = make_decision(projected, market_total, factors)

    print(f"Projected Total : {projected}")
    print(f"Market Total    : {market_total}")
    print(f"Edge            : {result.get('edge')}")
    print(f"Decision        : {result['decision']}")
    print(f"Confidence      : {result.get('confidence', 0)}%")
    
    if result["decision"] != "NO BET":
        print(f"Tier            : {result['tier']}")
        print(f"Agreeing        : {', '.join(result['agreeing_factors'])}")
    
    print(f"\nReason: {result['reason']}")

if __name__ == "__main__":
    run_test()