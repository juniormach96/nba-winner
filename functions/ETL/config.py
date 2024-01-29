from dataclasses import dataclass
from datetime import date


@dataclass
class AppConfig:
    START_DATE: str = date.today().strftime("%m/%d/%Y")
    NBA_LEAGUE_ID: str = "00"
    PRE_SELECTED_FEATURES: list = [
        "TEAM_NAME",
        "GAME_ID",
        "GAME_DATE",
        "PTS",
        "PLUS_MINUS",
        "MATCHUP",
    ]
    MIN_GAMES_PER_TEAM: int = 100
    MOVING_AVERAGE_WINDOWS: list = [1, 5, 10, 15, 20]


config = AppConfig()
