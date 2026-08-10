from enum import Enum
from dataclasses import dataclass
from typing import List

class Signal(Enum):
    OVER = "OVER"
    UNDER = "UNDER"
    NEUTRAL = "NEUTRAL"

@dataclass
class FactorResult:
    name: str
    signal: Signal
    strength: float      # 0.0 to 1.0
    weight: float        # importance
    reason: str

def score_pace(team_a_pace: float, team_b_pace: float, league_avg_pace: float) -> FactorResult:
    combined = (team_a_pace + team_b_pace) / 2
    diff = combined - league_avg_pace

    if diff >= 2.5:
        return FactorResult("Pace", Signal.OVER, min(diff / 5, 1.0), 1.3, f"Fast pace ({combined:.1f})")
    elif diff <= -2.5:
        return FactorResult("Pace", Signal.UNDER, min(abs(diff) / 5, 1.0), 1.3, f"Slow pace ({combined:.1f})")
    return FactorResult("Pace", Signal.NEUTRAL, 0.0, 1.3, "Average pace")

def score_recent_scoring(team_a_recent: float, team_b_recent: float, 
                         team_a_season: float, team_b_season: float) -> FactorResult:
    recent_total = team_a_recent + team_b_recent
    season_total = team_a_season + team_b_season
    diff = recent_total - season_total

    if diff >= 7:
        return FactorResult("Recent Scoring", Signal.OVER, min(diff / 14, 1.0), 1.2, "Scoring trending up")
    elif diff <= -7:
        return FactorResult("Recent Scoring", Signal.UNDER, min(abs(diff) / 14, 1.0), 1.2, "Scoring trending down")
    return FactorResult("Recent Scoring", Signal.NEUTRAL, 0.0, 1.2, "No clear scoring trend")

def score_offense(team_a_ortg: float, team_b_ortg: float, league_avg: float) -> FactorResult:
    combined = (team_a_ortg + team_b_ortg) / 2
    diff = combined - league_avg

    if diff >= 3.5:
        return FactorResult("Offense", Signal.OVER, min(diff / 7, 1.0), 1.1, "Strong combined offense")
    elif diff <= -3.5:
        return FactorResult("Offense", Signal.UNDER, min(abs(diff) / 7, 1.0), 1.1, "Weak combined offense")
    return FactorResult("Offense", Signal.NEUTRAL, 0.0, 1.1, "Average offense")

def score_defense(team_a_drtg: float, team_b_drtg: float, league_avg: float) -> FactorResult:
    combined = (team_a_drtg + team_b_drtg) / 2
    diff = league_avg - combined  # positive = better defense

    if diff >= 3.5:
        return FactorResult("Defense", Signal.UNDER, min(diff / 7, 1.0), 1.25, "Strong combined defense")
    elif diff <= -3.5:
        return FactorResult("Defense", Signal.OVER, min(abs(diff) / 7, 1.0), 1.25, "Weak combined defense")
    return FactorResult("Defense", Signal.NEUTRAL, 0.0, 1.25, "Average defense")

def score_rest(team_a_rest_days: int, team_b_rest_days: int, team_a_b2b: bool, team_b_b2b: bool) -> FactorResult:
    if team_a_b2b and team_b_b2b:
        return FactorResult("Rest", Signal.UNDER, 0.7, 1.15, "Both teams on back-to-back")
    if team_a_b2b or team_b_b2b:
        return FactorResult("Rest", Signal.UNDER, 0.45, 1.15, "One team on back-to-back")
    if team_a_rest_days >= 3 and team_b_rest_days >= 3:
        return FactorResult("Rest", Signal.OVER, 0.4, 1.15, "Both teams well rested")
    return FactorResult("Rest", Signal.NEUTRAL, 0.0, 1.15, "Normal rest situation")

def score_home_away(team_a_home_ppg: float, team_a_away_ppg: float,
                    team_b_home_ppg: float, team_b_away_ppg: float,
                    is_team_a_home: bool) -> FactorResult:
    if is_team_a_home:
        home_scoring = team_a_home_ppg + team_b_away_ppg
        away_scoring = team_a_away_ppg + team_b_home_ppg
    else:
        home_scoring = team_b_home_ppg + team_a_away_ppg
        away_scoring = team_b_away_ppg + team_a_home_ppg

    diff = home_scoring - away_scoring

    if diff >= 6:
        return FactorResult("Home/Away", Signal.OVER, min(diff / 12, 1.0), 1.0, "Strong home scoring environment")
    elif diff <= -6:
        return FactorResult("Home/Away", Signal.UNDER, min(abs(diff) / 12, 1.0), 1.0, "Weak home scoring environment")
    return FactorResult("Home/Away", Signal.NEUTRAL, 0.0, 1.0, "Normal home/away effect")

def score_injuries(key_players_out: int, impact_score: float) -> FactorResult:
    """
    impact_score: estimated points effect on the total
    Positive = more points expected (missing defender)
    Negative = fewer points expected (missing scorer)
    """
    if impact_score >= 4.5:
        return FactorResult("Injuries", Signal.OVER, min(impact_score / 8, 1.0), 1.4, f"Missing key defenders (+{impact_score:.1f})")
    elif impact_score <= -4.5:
        return FactorResult("Injuries", Signal.UNDER, min(abs(impact_score) / 8, 1.0), 1.4, f"Missing key scorers ({impact_score:.1f})")
    return FactorResult("Injuries", Signal.NEUTRAL, 0.0, 1.4, "No major injury impact")

def score_matchup(h2h_avg_total: float, league_avg_total: float, style_clash: str = "neutral") -> FactorResult:
    diff = h2h_avg_total - league_avg_total

    if style_clash == "fast":
        return FactorResult("Matchup", Signal.OVER, 0.65, 1.05, "Style favors high scoring")
    if style_clash == "slow":
        return FactorResult("Matchup", Signal.UNDER, 0.65, 1.05, "Style favors low scoring")

    if diff >= 5:
        return FactorResult("Matchup", Signal.OVER, min(diff / 10, 1.0), 1.05, f"H2H averages high ({h2h_avg_total:.1f})")
    elif diff <= -5:
        return FactorResult("Matchup", Signal.UNDER, min(abs(diff) / 10, 1.0), 1.05, f"H2H averages low ({h2h_avg_total:.1f})")
    return FactorResult("Matchup", Signal.NEUTRAL, 0.0, 1.05, "Neutral matchup history")