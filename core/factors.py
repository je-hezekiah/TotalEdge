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
    weight: float
    reason: str

def score_pace(team_a_pace: float, team_b_pace: float, league_avg_pace: float) -> FactorResult:
    combined = (team_a_pace + team_b_pace) / 2
    diff = combined - league_avg_pace

    if diff >= 3.0:
        return FactorResult("Pace", Signal.OVER, min(diff / 5.5, 1.0), 1.35, f"Fast pace ({combined:.1f})")
    elif diff <= -3.0:
        return FactorResult("Pace", Signal.UNDER, min(abs(diff) / 5.5, 1.0), 1.35, f"Slow pace ({combined:.1f})")
    return FactorResult("Pace", Signal.NEUTRAL, 0.0, 1.35, "Average pace")

def score_recent_scoring(team_a_recent: float, team_b_recent: float,
                         team_a_season: float, team_b_season: float) -> FactorResult:
    recent_total = team_a_recent + team_b_recent
    season_total = team_a_season + team_b_season
    diff = recent_total - season_total

    if diff >= 8:
        return FactorResult("Recent Scoring", Signal.OVER, min(diff / 15, 1.0), 1.25, "Scoring trending up strongly")
    elif diff <= -8:
        return FactorResult("Recent Scoring", Signal.UNDER, min(abs(diff) / 15, 1.0), 1.25, "Scoring trending down strongly")
    return FactorResult("Recent Scoring", Signal.NEUTRAL, 0.0, 1.25, "No clear scoring trend")

def score_offense(team_a_ortg: float, team_b_ortg: float, league_avg: float) -> FactorResult:
    combined = (team_a_ortg + team_b_ortg) / 2
    diff = combined - league_avg

    if diff >= 4.0:
        return FactorResult("Offense", Signal.OVER, min(diff / 7.5, 1.0), 1.2, "Strong combined offense")
    elif diff <= -4.0:
        return FactorResult("Offense", Signal.UNDER, min(abs(diff) / 7.5, 1.0), 1.2, "Weak combined offense")
    return FactorResult("Offense", Signal.NEUTRAL, 0.0, 1.2, "Average offense")

def score_defense(team_a_drtg: float, team_b_drtg: float, league_avg: float) -> FactorResult:
    combined = (team_a_drtg + team_b_drtg) / 2
    diff = league_avg - combined  # positive = better defense

    if diff >= 4.0:
        return FactorResult("Defense", Signal.UNDER, min(diff / 7.5, 1.0), 1.3, "Strong combined defense")
    elif diff <= -4.0:
        return FactorResult("Defense", Signal.OVER, min(abs(diff) / 7.5, 1.0), 1.3, "Weak combined defense")
    return FactorResult("Defense", Signal.NEUTRAL, 0.0, 1.3, "Average defense")

def score_rest(team_a_rest_days: int, team_b_rest_days: int,
               team_a_b2b: bool, team_b_b2b: bool) -> FactorResult:
    if team_a_b2b and team_b_b2b:
        return FactorResult("Rest", Signal.UNDER, 0.75, 1.2, "Both teams on back-to-back")
    if team_a_b2b or team_b_b2b:
        return FactorResult("Rest", Signal.UNDER, 0.50, 1.2, "One team on back-to-back")
    if team_a_rest_days >= 3 and team_b_rest_days >= 3:
        return FactorResult("Rest", Signal.OVER, 0.45, 1.2, "Both teams well rested")
    return FactorResult("Rest", Signal.NEUTRAL, 0.0, 1.2, "Normal rest")

def score_home_away(team_a_home_ppg: float, team_a_away_ppg: float,
                    team_b_home_ppg: float, team_b_away_ppg: float,
                    is_team_a_home: bool) -> FactorResult:
    if is_team_a_home:
        expected = team_a_home_ppg + team_b_away_ppg
        baseline = team_a_away_ppg + team_b_home_ppg
    else:
        expected = team_b_home_ppg + team_a_away_ppg
        baseline = team_b_away_ppg + team_a_home_ppg

    diff = expected - baseline

    if diff >= 7:
        return FactorResult("Home/Away", Signal.OVER, min(diff / 13, 1.0), 1.05, "Strong home scoring environment")
    elif diff <= -7:
        return FactorResult("Home/Away", Signal.UNDER, min(abs(diff) / 13, 1.0), 1.05, "Weak home scoring environment")
    return FactorResult("Home/Away", Signal.NEUTRAL, 0.0, 1.05, "Normal home/away effect")

def score_injuries(impact_score: float) -> FactorResult:
    """
    impact_score:
    + positive = missing defenders → higher total expected
    - negative = missing scorers → lower total expected
    """
    if impact_score >= 5.0:
        return FactorResult("Injuries", Signal.OVER, min(impact_score / 9, 1.0), 1.45, f"Missing key defenders (+{impact_score:.1f})")
    elif impact_score <= -5.0:
        return FactorResult("Injuries", Signal.UNDER, min(abs(impact_score) / 9, 1.0), 1.45, f"Missing key scorers ({impact_score:.1f})")
    return FactorResult("Injuries", Signal.NEUTRAL, 0.0, 1.45, "No major injury impact")

def score_matchup(h2h_avg_total: float, league_avg_total: float, style: str = "neutral") -> FactorResult:
    if style == "fast":
        return FactorResult("Matchup", Signal.OVER, 0.70, 1.1, "Playing styles favor high scoring")
    if style == "slow":
        return FactorResult("Matchup", Signal.UNDER, 0.70, 1.1, "Playing styles favor low scoring")

    diff = h2h_avg_total - league_avg_total
    if diff >= 6:
        return FactorResult("Matchup", Signal.OVER, min(diff / 11, 1.0), 1.1, f"H2H averages high ({h2h_avg_total:.1f})")
    elif diff <= -6:
        return FactorResult("Matchup", Signal.UNDER, min(abs(diff) / 11, 1.0), 1.1, f"H2H averages low ({h2h_avg_total:.1f})")
    return FactorResult("Matchup", Signal.NEUTRAL, 0.0, 1.1, "Neutral matchup")