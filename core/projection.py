def project_total(
    team_a_pace: float,
    team_b_pace: float,
    team_a_ortg: float,
    team_b_ortg: float,
    team_a_drtg: float,
    team_b_drtg: float,
    is_team_a_home: bool = True,
    injury_adjustment: float = 0.0,
    rest_adjustment: float = 0.0,
    matchup_adjustment: float = 0.0
) -> float:
    """
    Projects the total points BEFORE looking at the market line.
    """

    # Expected pace (blend of both teams)
    expected_pace = (team_a_pace + team_b_pace) / 2

    # Opponent-adjusted offensive ratings
    team_a_adj_ortg = (team_a_ortg + (200 - team_b_drtg)) / 2
    team_b_adj_ortg = (team_b_ortg + (200 - team_a_drtg)) / 2

    # Convert to points
    team_a_points = (expected_pace * team_a_adj_ortg) / 100
    team_b_points = (expected_pace * team_b_adj_ortg) / 100

    # Home court advantage
    if is_team_a_home:
        team_a_points += 2.8
    else:
        team_b_points += 2.8

    projected = team_a_points + team_b_points
    projected += injury_adjustment + rest_adjustment + matchup_adjustment

    return round(projected, 1)